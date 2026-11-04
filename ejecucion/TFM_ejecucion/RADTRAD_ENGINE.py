#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RADTRAD_ENGINE.py  —  Motor unificado ARCON96 + RADTRAD + Generador PSF
========================================================================
Contiene:
  · PSF_GENERATOR  — Generador de archivos PSF para RADTRAD 3.03
  · PIPELINE       — modo --gui-mode: ejecuta PIPELINE.py (cadena ARCON96 → RADTRAD →
                     dosis → zonas EAB/LPZ y mapa) con los parámetros de RADTRAD_GUI.py,
                     usando las carpetas INPUT/ y RUN_N/ de la interfaz.

Cambios respecto a la versión anterior (TFM, 11/2026):
  · El generador escribe los números con el ancho de columna que lee RADTRAD (campos de
    13 caracteres, E10.4 tras 3 blancos) y la tabla de χ/Q del EAB/LPZ con su formato
    propio ("   0.0000E+00 1.5629E-02"); con un solo blanco RADTRAD perdía los exponentes.
  · Las unidades que pide la interfaz (m³, m³/s, 1/s) se convierten a las de RADTRAD
    (ft³, cfm, %/día). Antes se escribían sin convertir.
  · El cálculo lo hace PIPELINE.py, el mismo que se usa por consola.

Uso como script:
    python RADTRAD_ENGINE.py                             # modo consola
    python RADTRAD_ENGINE.py --gui-mode --params p.json  # modo GUI

Uso como modulo:
    from RADTRAD_ENGINE import PSFModel, Compartment, ...
"""

from __future__ import annotations

import sys
sys.dont_write_bytecode = True  # no genera __pycache__

# Limitar threads de OpenBLAS/MKL para evitar errores de memoria en Windows
import os as _os
for _k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    _os.environ.setdefault(_k, "1")

# Forzar UTF-8 en stdout/stderr para evitar errores en consolas Windows (cp1252)
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse, csv, json, logging, os, random, re, shutil, subprocess
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import textwrap

# =============================================================================
# PSF GENERATOR
# =============================================================================

# ---------------------------------------------------------------------------
# Constantes del formato PSF
# ---------------------------------------------------------------------------

# Tipos de compartimento
COMP_TYPE_CONTROL_ROOM = 1
COMP_TYPE_ENVIRONMENT  = 2
COMP_TYPE_OTHER        = 3

COMP_TYPE_NAMES = {
    COMP_TYPE_CONTROL_ROOM: "Control Room",
    COMP_TYPE_ENVIRONMENT:  "Environment",
    COMP_TYPE_OTHER:        "Other",
}

# Tipos de pathway
PATH_TYPE_PIPING          = 1
PATH_TYPE_FILTER          = 2
PATH_TYPE_SUPPRESSION_POOL= 3
PATH_TYPE_AIR_LEAKAGE     = 4

PATH_TYPE_NAMES = {
    PATH_TYPE_PIPING:           "Piping",
    PATH_TYPE_FILTER:           "Filter",
    PATH_TYPE_SUPPRESSION_POOL: "Suppression Pool",
    PATH_TYPE_AIR_LEAKAGE:      "Air Leakage",
}

# Modelos de deposición de aerosoles
DEPOSIT_AEROSOL_NONE   = 0
DEPOSIT_AEROSOL_USER   = 1
DEPOSIT_AEROSOL_HENRY  = 2
DEPOSIT_AEROSOL_POWERS = 3


# ---------------------------------------------------------------------------
# Formato científico compatible con RADTRAD
# ---------------------------------------------------------------------------

# Unidades: la interfaz trabaja en SI y RADTRAD 3.03 en unidades inglesas
M3_TO_FT3        = 35.314667        # volumen de compartimentos   m³   → ft³
M3S_TO_CFM       = 2118.8800        # caudal de los filtros       m³/s → cfm
PER_S_TO_PCT_DAY = 100.0 * 86400.0  # fuga de aire (convección)   1/s  → %/día


def _e12(v: float) -> str:
    """Campo de 13 caracteres (3 blancos + E10.4): «   1.2340E+02», como en las tablas
    que RADTRAD lee bien (caminos, respiración, ocupación, volumen efectivo, fracciones)."""
    return f"{float(v):13.4E}"


def _e11(v: float) -> str:
    """Valor suelto con 2 blancos + E10.4 («  3.8920E+05»): potencia y volúmenes."""
    return f"{float(v):12.4E}"


def _xq_row(t: float, v: float) -> str:
    """Fila de la tabla de χ/Q del EAB/LPZ: RADTRAD lee el tiempo en las columnas 4-13,
    salta una y lee el χ/Q en las 15-24 («   0.0000E+00 1.5629E-02»)."""
    return f"   {float(t):10.4E} {float(v):10.4E}"


def _fmt_table_row(times: List[float], values: List[float]) -> str:
    """Una fila de tabla (tiempo, valor) en formato PSF."""
    lines = []
    for t, v in zip(times, values):
        lines.append(f"{_e12(t)}{_e12(v)}")
    return "\n".join(lines)


def _fmt_table_row3(times: List[float],
                    v1: List[float],
                    v2: List[float],
                    v3: List[float]) -> str:
    """Tabla de 3 valores por fila (tiempo, val1, val2, val3)."""
    lines = []
    for t, a, b, c in zip(times, v1, v2, v3):
        lines.append(f"{_e12(t)}{_e12(a)}{_e12(b)}{_e12(c)}")
    return "\n".join(lines)


def _fmt_table_row5(times: List[float],
                    flow: List[float],
                    aer: List[float],
                    elem: List[float],
                    org: List[float]) -> str:
    """Tabla de 5 valores: tiempo, flow, aer%, elem%, org%."""
    lines = []
    for t, f, a, e, o in zip(times, flow, aer, elem, org):
        lines.append(f"{_e12(t)}{_e12(f)}{_e12(a)}{_e12(e)}{_e12(o)}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Tipos de datos para tablas genéricas
# ---------------------------------------------------------------------------

@dataclass
class TimeValueTable:
    """Tabla de pares (tiempo_h, valor)."""
    times:  List[float] = field(default_factory=lambda: [0.0, 720.0])
    values: List[float] = field(default_factory=lambda: [0.0, 0.0])

    def __post_init__(self):
        assert len(self.times) == len(self.values), \
            "times y values deben tener la misma longitud"
        assert 1 <= len(self.times) <= 10, \
            "La tabla debe tener entre 1 y 10 filas"

    def count(self) -> int:
        return len(self.times)


@dataclass
class TimeValue3Table:
    """Tabla de cuádruplos (tiempo, v1, v2, v3)."""
    times: List[float] = field(default_factory=lambda: [0.0, 720.0])
    v1:    List[float] = field(default_factory=lambda: [0.0, 0.0])
    v2:    List[float] = field(default_factory=lambda: [0.0, 0.0])
    v3:    List[float] = field(default_factory=lambda: [0.0, 0.0])

    def count(self) -> int:
        return len(self.times)


@dataclass
class FilterTable:
    """Tabla de filtro: tiempo, flow_rate, aer%, elem%, org%."""
    times: List[float] = field(default_factory=lambda: [0.0, 720.0])
    flow:  List[float] = field(default_factory=lambda: [0.0, 0.0])
    aer:   List[float] = field(default_factory=lambda: [99.0, 99.0])
    elem:  List[float] = field(default_factory=lambda: [99.0, 99.0])
    org:   List[float] = field(default_factory=lambda: [99.0, 99.0])

    def count(self) -> int:
        return len(self.times)


# ---------------------------------------------------------------------------
# COMPARTIMENTO
# ---------------------------------------------------------------------------

@dataclass
class Compartment:
    """
    Define un compartimento RADTRAD completo.

    Parámetros principales:
        name            Nombre del compartimento
        comp_type       1=Control Room, 2=Environment, 3=Other
        volume_m3       Volumen en m³

    Flags de características (sección PLANTA):
        has_sprays      Sprays presentes
        has_filters     Filtros de recirculación
        has_deposition  Deposición natural
        has_opool       Overlying pool

    Parámetros de escenario:
        detail_output   Imprimir output detallado
        decay           Procesar cadena de desintegración

    Filtros de recirculación (si has_filters=True):
        filter_flow_rate        Caudal normalizado [1/s]
        filter_eff_table        Tabla eficiencias (tiempo, aer%, elem%, org%)

    Deposición natural de aerosoles:
        deposit_aerosol_model   0=ninguno, 1=user, 2=Henry, 3=Powers
        deposit_aerosol_table   Tabla para modelo user (tiempo, coef[/s])
        deposit_henry_table     Tabla Henry (tiempo, altura[m], densidad[g/cc])
        deposit_powers_reactor  Tipo reactor (1=PWR-DBA, 2=PWR-SA, 3=BWR-DBA,
                                              4=BWR-SA, 5=APWR-DBA)
        deposit_powers_pctile   Percentil (10.0, 50.0, 90.0)

    Deposición de yodo elemental:
        deposit_elemental_model 0=ninguno, 1=user
        deposit_elemental_table Tabla (tiempo, coef[/s])
    """
    name:       str
    comp_type:  int   = COMP_TYPE_OTHER
    volume_m3:  float = 0.0

    # Flags planta
    has_sprays:     bool = False
    has_filters:    bool = False
    has_deposition: bool = False
    has_opool:      bool = False

    # Escenario
    detail_output: bool = False
    decay:         bool = True

    # Filtros recirculación
    filter_flow_rate: float = 0.0
    filter_eff_table: Optional[TimeValue3Table] = None   # (t, aer%, elem%, org%)

    # Deposición aerosoles
    deposit_aerosol_model:   int = DEPOSIT_AEROSOL_NONE
    deposit_aerosol_table:   Optional[TimeValueTable]  = None  # user-defined [/s]
    deposit_henry_table:     Optional[TimeValue3Table] = None  # (t, h[m], rho[g/cc])
    deposit_powers_reactor:  int   = 1      # 1=PWR-DBA
    deposit_powers_pctile:   float = 50.0   # percentil

    # Deposición yodo elemental
    deposit_elemental_model: int = 0
    deposit_elemental_table: Optional[TimeValueTable] = None   # (t, coef[/s])


# ---------------------------------------------------------------------------
# PATHWAY
# ---------------------------------------------------------------------------

@dataclass
class Pathway:
    """
    Define un pathway RADTRAD completo.

    Parámetros principales:
        name            Nombre del pathway
        from_comp       Número de compartimento origen (1-based)
        to_comp         Número de compartimento destino (1-based)
        path_type       1=Piping, 2=Filter, 3=SuppressionPool, 4=AirLeakage

    Air Leakage (path_type=4):
        convection_table    Tabla caudal normalizado (tiempo, flow[/s])

    Filter pathway (path_type=2):
        filter_table        Tabla filtro (tiempo, flow[m³/s], aer%, elem%, org%)

    Piping (path_type=1):
        piping_aerosol_model    0=ninguno, 1=user
        piping_aerosol_table    Tabla (tiempo, coef[/s], flow[m³/s])
        piping_elemental_model  0=ninguno, 1=user
        piping_elemental_table  Tabla (tiempo, coef[/s], flow[m³/s])
        piping_organic_model    0=ninguno, 1=user
        piping_organic_table    Tabla (tiempo, coef[/s], flow[m³/s])

    Suppression Pool (path_type=3):
        sp_initial_volume       Volumen inicial [m³]
        sp_aerosol_table        Tabla (tiempo, DF) — DF≥1
        sp_elemental_table      Tabla (tiempo, DF)
        sp_organic_table        Tabla (tiempo, DF)
    """
    name:      str
    from_comp: int
    to_comp:   int
    path_type: int = PATH_TYPE_AIR_LEAKAGE

    # Air leakage
    convection_table: Optional[TimeValueTable] = None   # (tiempo, flow[/s])

    # Filter pathway
    filter_table: Optional[FilterTable] = None

    # Piping
    piping_aerosol_model:   int = 0
    piping_aerosol_table:   Optional[TimeValue3Table] = None  # (t, coef, flow)
    piping_elemental_model: int = 0
    piping_elemental_table: Optional[TimeValue3Table] = None
    piping_organic_model:   int = 0
    piping_organic_table:   Optional[TimeValue3Table] = None

    # Suppression pool
    sp_initial_volume:   float = 0.0
    sp_aerosol_table:    Optional[TimeValueTable] = None
    sp_elemental_table:  Optional[TimeValueTable] = None
    sp_organic_table:    Optional[TimeValueTable] = None


# ---------------------------------------------------------------------------
# DOSE LOCATION
# ---------------------------------------------------------------------------

@dataclass
class DoseLocation:
    """
    Define una dose location RADTRAD.

    Parámetros:
        name                Nombre (e.g. "Exclusion Area Boundary")
        compartment_number  Número del compartimento donde está (1-based)
        xq_model            0=constante 1.0, 1=usuario
        xq_table            Tabla X/Q (tiempo[h], X/Q[s/m³]) si xq_model=1
        br_table            Tabla breathing rate (tiempo[h], BR[m³/s])
        has_occupancy       Si True, incluir factores de ocupación (solo CR)
        occupancy_table     Tabla occupancy (tiempo[h], factor[-])
    """
    name:               str
    compartment_number: int
    xq_model:           int = 0
    xq_table:           Optional[TimeValueTable] = None
    br_table:           Optional[TimeValueTable] = None
    has_occupancy:      bool = False
    occupancy_table:    Optional[TimeValueTable] = None


# ---------------------------------------------------------------------------
# MODELO GLOBAL DEL PSF
# ---------------------------------------------------------------------------

@dataclass
class PSFModel:
    """
    Modelo completo de un archivo PSF RADTRAD.

    Parámetros globales:
        title               Título del caso
        plant_model_name    Nombre del modelo de planta
        scenario_name       Nombre del escenario
        nif_file            Ruta al archivo NIF
        inp_file            Ruta al archivo INP (dose conversion factors)
        rft_file            Ruta al archivo RFT (release fractions)
        plant_power_mwt     Potencia de la planta en MWt
        output_filename     Nombre del archivo de salida .o0
        frac_aerosol        Fracción de yodo como aerosol
        frac_elemental      Fracción de yodo elemental
        frac_organic        Fracción de yodo orgánico
        delay_time_h        Tiempo de retardo [h]
        calculate_daughters Si True, calcula productos de desintegración
        source_compartment  Compartimento fuente (1-based)
        source_fraction     Fracción del término fuente en ese compartimento
        eff_vol_xq_table    Tabla X/Q volumen efectivo (sala control)
        show_plant          Incluir descripción de planta en output
        show_scenario       Incluir descripción de escenario en output
        show_event          Mostrar resultados por evento
        show_step           Mostrar resultados por paso suplementario
        show_model          Mostrar info del modelo
    """
    title:           str   = "RADTRAD Case"
    plant_model_name:str   = "Plant Model"
    scenario_name:   str   = "Scenario"
    nif_file:        str   = "defaults\\bwr_i131.nif"
    inp_file:        str   = "defaults\\fgr11&12.inp"
    rft_file:        str   = "defaults\\bwr_dba.rft"
    plant_power_mwt: float = 530.4
    output_filename: str   = "output.o0"

    frac_aerosol:   float = 0.95
    frac_elemental: float = 0.0485
    frac_organic:   float = 0.0015
    delay_time_h:   float = 0.0
    calculate_daughters: bool = True

    source_compartment: int   = 1
    source_fraction:    float = 1.0

    eff_vol_xq_table: Optional[TimeValueTable] = None

    show_plant:    bool = True
    show_scenario: bool = True
    show_event:    bool = True
    show_step:     bool = False
    show_model:    bool = False

    compartments:   List[Compartment]  = field(default_factory=list)
    pathways:       List[Pathway]      = field(default_factory=list)
    dose_locations: List[DoseLocation] = field(default_factory=list)

    def add_compartment(self, c: Compartment) -> "PSFModel":
        self.compartments.append(c)
        return self

    def add_pathway(self, p: Pathway) -> "PSFModel":
        self.pathways.append(p)
        return self

    def add_dose_location(self, d: DoseLocation) -> "PSFModel":
        self.dose_locations.append(d)
        return self

    # -----------------------------------------------------------------------
    # VALIDACIÓN
    # -----------------------------------------------------------------------

    def validate(self) -> List[str]:
        """Devuelve lista de errores. Vacía = válido."""
        errors = []
        n = len(self.compartments)
        if n == 0:
            errors.append("Se necesita al menos 1 compartimento.")
        if len(self.pathways) == 0:
            errors.append("Se necesita al menos 1 pathway.")
        if len(self.dose_locations) == 0:
            errors.append("Se necesita al menos 1 dose location.")

        # Fracciones de yodo
        total = self.frac_aerosol + self.frac_elemental + self.frac_organic
        if abs(total - 1.0) > 1e-6:
            errors.append(
                f"Las fracciones de yodo deben sumar 1.0 (suma actual: {total:.6f})")

        # Compartimentos referenciados en pathways
        for i, p in enumerate(self.pathways, 1):
            for label, num in (("from_comp", p.from_comp), ("to_comp", p.to_comp)):
                if not (1 <= num <= n):
                    errors.append(
                        f"Pathway {i}: {label}={num} fuera de rango (1-{n})")

        # Compartimentos en dose locations
        for i, dl in enumerate(self.dose_locations, 1):
            if not (1 <= dl.compartment_number <= n):
                errors.append(
                    f"DoseLocation {i}: compartment_number={dl.compartment_number} "
                    f"fuera de rango (1-{n})")

        return errors

    # -----------------------------------------------------------------------
    # ESCRITURA
    # -----------------------------------------------------------------------

    def write(self, path: str | Path) -> Path:
        """Genera el archivo PSF y lo escribe en disco."""
        errors = self.validate()
        if errors:
            raise ValueError("PSF inválido:\n" + "\n".join(f"  - {e}" for e in errors))

        content = self._build()
        out = Path(path)
        out.parent.mkdir(parents=True, exist_ok=True)
        # RADTRAD usa CRLF
        out.write_bytes(content.encode("utf-8").replace(b"\n", b"\r\n"))
        return out

    def to_string(self) -> str:
        """Devuelve el contenido del PSF como string (LF)."""
        errors = self.validate()
        if errors:
            raise ValueError("PSF inválido:\n" + "\n".join(f"  - {e}" for e in errors))
        return self._build()

    # -----------------------------------------------------------------------
    # CONSTRUCTOR INTERNO
    # -----------------------------------------------------------------------

    def _build(self) -> str:
        lines = []
        a = lines.append  # alias para brevedad

        # ── Cabecera ─────────────────────────────────────────────────────────
        a(f" Radtrad 3.03")
        a(f" {self.plant_model_name}")
        a(f" Nuclide Inventory File:")
        a(f" {self.nif_file}")
        a(f" Plant Power Level:")
        a(_e11(self.plant_power_mwt))

        # ── Compartimentos (sección PLANTA) ───────────────────────────────────
        a(f" Compartments:")
        a(f"   {len(self.compartments)}")
        for i, c in enumerate(self.compartments, 1):
            a(f" Compartment {i}:")
            a(f" {c.name}")
            a(f"   {c.comp_type}")
            a(_e11(c.volume_m3 * M3_TO_FT3))              # m³ → ft³
            a(f"   {'1' if c.has_sprays     else '0'}")
            a(f"   0")   # sump — siempre 0
            a(f"   {'1' if c.has_filters    else '0'}")
            a(f"   {'1' if c.has_deposition else '0'}")
            a(f"   {'1' if c.has_opool      else '0'}")

        # ── Pathways (sección PLANTA) ─────────────────────────────────────────
        a(f" Pathways:")
        a(f"   {len(self.pathways)}")
        for i, p in enumerate(self.pathways, 1):
            a(f" Pathway {i}:")
            a(f" {p.name}")
            a(f"   {p.from_comp}")
            a(f"   {p.to_comp}")
            a(f"   {p.path_type}")

        a(f" End of Plant Model File")

        # ── Escenario ─────────────────────────────────────────────────────────
        a(f" Scenario Description Name:")
        a(f" {self.scenario_name}")
        a(f" Plant Model Filename:")
        a(f" {self.plant_model_name}")

        # Source term
        a(f" Source Term:")
        a(f"   1")
        a(f"   {self.source_compartment}{_e12(self.source_fraction)}")
        a(f" {self.inp_file}")
        a(f" {self.rft_file}")
        a(f"{_e12(self.delay_time_h)}")
        a(f"   {'1' if self.calculate_daughters else '0'}")
        a(f"{_e12(self.frac_aerosol)}{_e12(self.frac_elemental)}"
          f"{_e12(self.frac_organic)}{_e12(1.0)}")

        # Overlying Pool — siempre desactivado (placeholder)
        a(f" Overlying Pool:")
        a(f"   0")
        a(f"{_e12(0.0)}")
        a(f"   0")
        a(f"   0")
        a(f"   0")
        a(f"   0")

        # ── Compartimentos (sección ESCENARIO) ────────────────────────────────
        a(f" Compartments:")
        a(f"   {len(self.compartments)}")
        for i, c in enumerate(self.compartments, 1):
            a(f" Compartment {i}:")
            a(f"   {'1' if c.detail_output else '0'}")
            a(f"   {'1' if c.decay         else '0'}")

            # Sprays — siempre 0 en este borrador
            a(f"   0")   # sprays_aerosol_model
            a(f"   0")   # sprays_elemental_model
            a(f"   0")   # sprays_organic_model
            a(f"   0")   # sump_volatilization_count

            # Filtros de recirculación
            if c.has_filters and c.filter_eff_table is not None:
                tbl = c.filter_eff_table
                a(f"   1")   # c_filter_eff_model
                a(f"{_e12(c.filter_flow_rate)}")
                a(f"   {tbl.count()}")
                for t, v1, v2, v3 in zip(tbl.times, tbl.v1, tbl.v2, tbl.v3):
                    a(f"{_e12(t)}{_e12(v1)}{_e12(v2)}{_e12(v3)}")
            else:
                a(f"   0")   # c_filter_eff_model NO

            # Deposición de aerosoles
            if not c.has_deposition or c.deposit_aerosol_model == DEPOSIT_AEROSOL_NONE:
                a(f"   0")   # deposit_aerosol_model
            elif c.deposit_aerosol_model == DEPOSIT_AEROSOL_USER:
                tbl = c.deposit_aerosol_table
                a(f"   1")
                a(f"   {tbl.count()}")
                for t, v in zip(tbl.times, tbl.values):
                    a(f"{_e12(t)}{_e12(v)}")
            elif c.deposit_aerosol_model == DEPOSIT_AEROSOL_HENRY:
                tbl = c.deposit_henry_table
                a(f"   2")
                a(f"   {tbl.count()}")
                for t, h, rho in zip(tbl.times, tbl.v1, tbl.v2):
                    a(f"{_e12(t)}{_e12(h)}{_e12(rho)}")
            elif c.deposit_aerosol_model == DEPOSIT_AEROSOL_POWERS:
                a(f"   3")
                a(f"   {c.deposit_powers_reactor}")
                a(f"{_e12(c.deposit_powers_pctile)}")

            # Deposición de yodo elemental
            if c.deposit_elemental_model == 1 and c.deposit_elemental_table is not None:
                tbl = c.deposit_elemental_table
                a(f"   1")
                a(f"   {tbl.count()}")
                for t, v in zip(tbl.times, tbl.values):
                    a(f"{_e12(t)}{_e12(v)}")
            else:
                a(f"   0")

        # ── Pathways (sección ESCENARIO) ──────────────────────────────────────
        a(f" Pathways:")
        a(f"   {len(self.pathways)}")
        for i, p in enumerate(self.pathways, 1):
            a(f" Pathway {i}:")
            a(f"   0")   # pathway_detail (placeholder)
            a(f"   0")   # pathway_decay  (placeholder)

            # Piping
            if p.path_type == PATH_TYPE_PIPING:
                a(f"   {p.piping_aerosol_model}")
                if p.piping_aerosol_model == 1 and p.piping_aerosol_table:
                    tbl = p.piping_aerosol_table
                    a(f"   {tbl.count()}")
                    for t, v1, v2 in zip(tbl.times, tbl.v1, tbl.v2):
                        a(f"{_e12(t)}{_e12(v1)}{_e12(v2)}")
                a(f"   {p.piping_elemental_model}")
                if p.piping_elemental_model == 1 and p.piping_elemental_table:
                    tbl = p.piping_elemental_table
                    a(f"   {tbl.count()}")
                    for t, v1, v2 in zip(tbl.times, tbl.v1, tbl.v2):
                        a(f"{_e12(t)}{_e12(v1)}{_e12(v2)}")
                a(f"   {p.piping_organic_model}")
                if p.piping_organic_model == 1 and p.piping_organic_table:
                    tbl = p.piping_organic_table
                    a(f"   {tbl.count()}")
                    for t, v1, v2 in zip(tbl.times, tbl.v1, tbl.v2):
                        a(f"{_e12(t)}{_e12(v1)}{_e12(v2)}")
                a(f"   0")   # p_filter_eff_model
                a(f"   0")   # sp_aerosol_model
                a(f"   0")   # sp_elemental_model
                a(f"   0")   # sp_organic_model
                a(f"   0")   # sp_volatilization_model
                a(f"   0")   # convection_model
                a(f"   0")   # water_leakage_model

            # Filter pathway
            elif p.path_type == PATH_TYPE_FILTER:
                a(f"   0")   # piping_aerosol_model
                a(f"   0")   # piping_elemental_model
                a(f"   0")   # piping_organic_model
                if p.filter_table is not None:
                    tbl = p.filter_table
                    a(f"   1")   # p_filter_eff_model
                    a(f"   {tbl.count()}")
                    for t, fl, ae, el, og in zip(
                            tbl.times, tbl.flow, tbl.aer, tbl.elem, tbl.org):
                        a(f"{_e12(t)}{_e12(fl * M3S_TO_CFM)}{_e12(ae)}{_e12(el)}{_e12(og)}")  # m³/s → cfm
                else:
                    a(f"   0")   # p_filter_eff_model
                a(f"   0")   # sp_aerosol_model
                a(f"   0")   # sp_elemental_model
                a(f"   0")   # sp_organic_model
                a(f"   0")   # sp_volatilization_model
                a(f"   0")   # convection_model
                a(f"   0")   # water_leakage_model

            # Suppression pool
            elif p.path_type == PATH_TYPE_SUPPRESSION_POOL:
                a(f"   0")   # piping
                a(f"   0")
                a(f"   0")
                a(f"   0")   # p_filter
                # sp aerosol
                if p.sp_aerosol_table:
                    tbl = p.sp_aerosol_table
                    a(f"   1")
                    a(f"{_e12(p.sp_initial_volume)}")
                    a(f"   {tbl.count()}")
                    for t, v in zip(tbl.times, tbl.values):
                        a(f"{_e12(t)}{_e12(v)}")
                else:
                    a(f"   0")
                # sp elemental
                if p.sp_elemental_table:
                    tbl = p.sp_elemental_table
                    a(f"   1")
                    a(f"   {tbl.count()}")
                    for t, v in zip(tbl.times, tbl.values):
                        a(f"{_e12(t)}{_e12(v)}")
                else:
                    a(f"   0")
                # sp organic
                if p.sp_organic_table:
                    tbl = p.sp_organic_table
                    a(f"   1")
                    a(f"   {tbl.count()}")
                    for t, v in zip(tbl.times, tbl.values):
                        a(f"{_e12(t)}{_e12(v)}")
                else:
                    a(f"   0")
                a(f"   0")   # sp_volatilization
                a(f"   0")   # convection
                a(f"   0")   # water_leakage

            # Air leakage
            elif p.path_type == PATH_TYPE_AIR_LEAKAGE:
                a(f"   0")   # piping_aerosol_model
                a(f"   0")   # piping_elemental_model
                a(f"   0")   # piping_organic_model
                a(f"   0")   # p_filter_eff_model
                a(f"   0")   # sp_aerosol_model
                a(f"   0")   # sp_elemental_model
                a(f"   0")   # sp_organic_model
                a(f"   0")   # sp_volatilization_model
                if p.convection_table:
                    tbl = p.convection_table
                    a(f"   1")   # convection_model
                    a(f"   {tbl.count()}")
                    for t, v in zip(tbl.times, tbl.values):
                        a(f"{_e12(t)}{_e12(v * PER_S_TO_PCT_DAY)}")   # 1/s → %/día
                else:
                    a(f"   0")   # convection_model (sin caudal)
                a(f"   0")   # water_leakage_model

        # ── Dose Locations ────────────────────────────────────────────────────
        a(f" Dose Locations:")
        a(f"   {len(self.dose_locations)}")
        for i, dl in enumerate(self.dose_locations, 1):
            a(f" Location {i}:")
            a(f" {dl.name}")
            a(f"   {dl.compartment_number}")

            # X/Q
            if dl.xq_model == 1 and dl.xq_table:
                tbl = dl.xq_table
                a(f"   1")
                a(f"{tbl.count():3d}")
                for t, v in zip(tbl.times, tbl.values):
                    a(_xq_row(t, v))
            else:
                a(f"   0")   # X/Q constante = 1.0

            # Breathing rate
            if dl.br_table:
                tbl = dl.br_table
                a(f"   1")
                a(f"   {tbl.count()}")
                for t, v in zip(tbl.times, tbl.values):
                    a(f"{_e12(t)}{_e12(v)}")
            else:
                a(f"   0")

            # Occupancy (solo sala de control)
            if dl.has_occupancy and dl.occupancy_table:
                tbl = dl.occupancy_table
                a(f"   1")
                a(f"   {tbl.count()}")
                for t, v in zip(tbl.times, tbl.values):
                    a(f"{_e12(t)}{_e12(v)}")
            else:
                a(f"   0")

        # Effective Volume Location (X/Q sala de control)
        if self.eff_vol_xq_table:
            tbl = self.eff_vol_xq_table
            a(f" Effective Volume Location:")
            a(f"   1")
            a(f"   {tbl.count()}")
            for t, v in zip(tbl.times, tbl.values):
                a(f"{_e12(t)}{_e12(v)}")
        else:
            a(f" Effective Volume Location:")
            a(f"   0")

        # ── Simulation parameters & output ────────────────────────────────────
        a(f" Simulation Parameters:")
        a(f"   1")                       # como en la plantilla de RADTRAD que funciona
        a(f"{_e12(0.0)}{_e12(0.0)}")
        a(f" Output Filename:")
        a(f" {self.output_filename}")
        a(f"   {'1' if self.show_plant    else '0'}")
        a(f"   {'1' if self.show_scenario else '0'}")
        a(f"   {'1' if self.show_event    else '0'}")
        a(f"   {'1' if self.show_step     else '0'}")
        a(f"   {'1' if self.show_model    else '0'}")
        a(f" End of Scenario File")

        return "\n".join(lines) + "\n"



# =============================================================================
# PIPELINE  --  ARCON96 + RADTRAD  (modo --gui-mode de RADTRAD_GUI.py)
# =============================================================================
# El cálculo lo hace PIPELINE.py (la misma cadena que se usa por consola). Este bloque
# traduce los parámetros de la interfaz a los de PIPELINE.run() y organiza las carpetas:
#   INPUT/MET, INPUT/NIF, INPUT/RFT, INPUT/INP, INPUT/PSF   datos de entrada
#   RUN_N/INPUT_USED   copia de los datos usados y params.json
#   RUN_N/WORK         casos de ARCON96 y RADTRAD
#   RUN_N/OUTPUT       resultados: χ/Q, Sets_Worst2h.xlsx, zonas_emergencia.json, mapa

import json
import logging
import os
import shutil

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

DIR_TEMPLATES = SCRIPT_DIR / "README_&_TEMPLATE"
DIR_INPUT     = SCRIPT_DIR / "INPUT"
DIR_MET       = DIR_INPUT / "MET"      # MET01.MET … o MET*.xlsx
DIR_NIF       = DIR_INPUT / "NIF"      # inventario .nif (y Excel/TXT para generarlo)
DIR_RFT       = DIR_INPUT / "RFT"      # fracciones de liberación .rft
DIR_INP       = DIR_INPUT / "INP"      # factores de dosis .inp
DIR_PSF       = DIR_INPUT / "PSF"      # plantilla .psf
DIR_INFO      = DIR_NIF                # alias usado por la interfaz

GUI_MODE: bool = False

try:
    import numpy, pandas, openpyxl   # noqa: F401  (dependencias del cálculo)
    _PIPELINE_DEPS_OK = True
    _PIPELINE_DEPS_ERROR = ""
except ImportError as _dep_err:
    _PIPELINE_DEPS_OK = False
    _PIPELINE_DEPS_ERROR = str(_dep_err)


def set_gui_mode(enabled: bool = True):
    """Call this from the GUI before launching the pipeline."""
    global GUI_MODE
    GUI_MODE = enabled


def _get_run_dir() -> Path:
    i = 1
    while (SCRIPT_DIR / f"RUN_{i}").exists():
        i += 1
    return SCRIPT_DIR / f"RUN_{i}"


def _init_run_dirs() -> dict:
    run_dir = _get_run_dir()
    d = {"run_dir": run_dir, "input_used": run_dir / "INPUT_USED", "work": run_dir / "WORK",
         "arcon": run_dir / "WORK" / "ARCON", "radtrad": run_dir / "WORK" / "RADTRAD",
         "defaults": run_dir / "WORK" / "Defaults", "output": run_dir / "OUTPUT"}
    for k in ("input_used", "arcon", "radtrad", "defaults", "output"):
        d[k].mkdir(parents=True, exist_ok=True)
    return d


def _snapshot_inputs(dest: Path, params: dict):
    for sub in (DIR_MET, DIR_NIF, DIR_RFT, DIR_INP, DIR_PSF):
        if sub.exists():
            shutil.copytree(sub, dest / sub.name, dirs_exist_ok=True)
    tpl = Path(params.get("template_path") or "")
    if tpl.is_file():
        shutil.copy2(tpl, dest / tpl.name)
    (dest / "params.json").write_text(json.dumps(params, indent=2, ensure_ascii=False, default=str),
                                      encoding="utf-8")


def _prepare_met(p: dict, met_dir: Path) -> int:
    """MET files for ARCON96 in RUN_N/WORK/MET, written in the columns ARCON96 reads
    (preparar_met.py): from the files of INPUT/MET or from the MET*.xlsx template."""
    import preparar_met
    met_dir.mkdir(parents=True, exist_ok=True)
    if p.get("met_mode") == "excel":
        xlsx = Path(p.get("excel_path") or "")
        if not xlsx.is_file():
            xlsx = next(iter(sorted(DIR_INFO.glob("MET*.xlsx")) + sorted(DIR_MET.glob("MET*.xlsx"))), None)
        if xlsx is None:
            raise FileNotFoundError("No MET*.xlsx found (INPUT/NIF or INPUT/MET)")
        logging.info("MET files from Excel: %s", xlsx.name)
        summaries = preparar_met.from_excel(xlsx, met_dir)
    else:
        n = int(p.get("num_met") or 0) or len(list(DIR_MET.glob("MET*.MET")))
        summaries = []
        for i in range(1, n + 1):
            src = DIR_MET / f"MET{i:02d}.MET"
            if not src.exists():
                raise FileNotFoundError(f"Missing {src}")
            summaries.append(preparar_met.prepare_file(src, met_dir / src.name))
    for s in summaries:
        bad = preparar_met.check_columns(met_dir / s["fichero"])
        logging.info("  %s: %d h, recovery %.2f %%, %d invalid hours for ARCON96 %s",
                     s["fichero"], s["horas"], s["recuperacion_pct"], bad,
                     ("(" + s["correcciones"] + ")") if s["correcciones"] else "")
    return len(summaries)


def _stage_defaults(p: dict, dest: Path) -> tuple:
    """Copy the chosen .rft, .nif and .inp to RUN_N/WORK/Defaults (copied next to every .psf)."""
    import PIPELINE as P
    rft, nif, inp = p["support_names"]
    if p.get("nif_mode") == "txt" and p.get("nif_txt"):
        nif = nif or "i_SMR.NIF"
        P.generate_nif(Path(p["nif_txt"]), DIR_NIF / nif)
        logging.info("Inventory generated from %s → %s", Path(p["nif_txt"]).name, nif)
    elif p.get("nif_mode") == "existing" and p.get("nif_path"):
        src = Path(p["nif_path"])
        if src.is_file() and src.parent.resolve() != DIR_NIF.resolve():
            shutil.copy2(src, DIR_NIF / src.name)
        nif = src.name
    for folder, name in ((DIR_RFT, rft), (DIR_NIF, nif), (DIR_INP, inp)):
        src = folder / name
        if not src.exists():
            raise FileNotFoundError(f"Not found: {src}")
        shutil.copy2(src, dest / name)
    return rft, nif, inp


def run_gui(p: dict) -> int:
    import PIPELINE as P
    P.setup_logging()
    for d in (DIR_INPUT, DIR_MET, DIR_NIF, DIR_RFT, DIR_INP, DIR_PSF, DIR_TEMPLATES):
        d.mkdir(parents=True, exist_ok=True)
    run = _init_run_dirs()
    _snapshot_inputs(run["input_used"], p)
    logging.info("=== %s ===", run["run_dir"].name)

    do_arcon = p.get("run_arcon", True)
    do_radtrad = p.get("run_radtrad", True)
    num_met = _prepare_met(p, run["work"] / "MET") if do_arcon else 0
    support = _stage_defaults(p, run["defaults"]) if do_radtrad else tuple(p.get("support_names", ("", "", "")))
    P.configure(arcon_dir=run["arcon"], met_dir=run["work"] / "MET", defaults_dir=run["defaults"],
                arcon_exe=p.get("arcon_exe"), radtrad_exe=p.get("radtrad_exe"))
    fixed = [tuple(s) if s else None for s in p.get("fixed_sets", [None])]
    nsets = int(p.get("nsets") or len(fixed) or 1)
    fixed = (fixed + [None] * nsets)[:nsets]
    params = dict(
        num_met=num_met, dist_min=int(p["dist_min"]), dist_max=int(p["dist_max"]), delta=int(p["delta"]),
        template_path=Path(p.get("template_path") or DIR_PSF / "template_kpfhr.psf"),
        nsets=nsets, fixed_sets=fixed, support_names=support,
        radtrad_exe=Path(p.get("radtrad_exe") or P.RADTRAD_EXE), out_root=run["radtrad"], out_action="3",
        no_run=bool(p.get("no_run", False)), workers=int(p.get("workers") or max(1, (os.cpu_count() or 2) - 1)),
        del_arcon=bool(p.get("delete_arcon_dirs", False)), ship=tuple(p.get("ship") or (43.353, -3.086, 300.0)),
        run_arcon=do_arcon, run_radtrad=do_radtrad, bridge_excel=p.get("bridge_excel", ""))
    rc = P.run(params)

    # results to RUN_N/OUTPUT (the interface looks for the χ/Q Excel there)
    for f in (P.XQ_EXCEL, P.TOTAL_XQ_EXCEL, P.XQ_MAX_TXT):
        if Path(f).exists() and Path(f).parent.resolve() != run["output"].resolve():
            shutil.copy2(f, run["output"] / Path(f).name)
    post = run["radtrad"] / "postprocess"
    if post.exists():
        shutil.copytree(post, run["output"], dirs_exist_ok=True)
    log = SCRIPT_DIR / "pipeline.log"
    if log.exists():
        shutil.copy2(log, run["output"] / "pipeline.log")
    if not p.get("keep_work", True):
        shutil.rmtree(run["work"], ignore_errors=True)
        logging.info("WORK deleted (keep_work = False)")
    logging.info("Results: %s", run["output"])
    if (run["output"] / "mapa_zonas.html").exists():
        logging.info("Map: run  python ver_mapa.py \"%s\"  (or VER_MAPA.bat) to see it on OpenStreetMap",
                     run["output"])
    return rc


def main():
    import argparse
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--gui-mode", action="store_true")
    parser.add_argument("--params", type=str, default=None)
    args, _ = parser.parse_known_args()
    if args.gui_mode and args.params:
        set_gui_mode(True)
        with open(args.params, encoding="utf-8") as f:
            return run_gui(json.load(f))
    import PIPELINE                       # console: same questions as PIPELINE.py
    return PIPELINE.main()


if __name__ == "__main__":
    raise SystemExit(main())
