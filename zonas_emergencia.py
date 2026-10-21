#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
zonas_emergencia.py  —  EAB / LPZ radii and map from the PIPELINE.py results
============================================================================

Reads the RADTRAD post-processing written by PIPELINE.py
  <out_root>/postprocess/Sets_Worst2h.xlsx          (worst 2-h TEDE at the EAB)
  <out_root>/postprocess/post_timeseries_accum.csv  (cumulative TEDE per receptor)
and, for every distance, takes the most unfavourable value over all the iodine
fraction sets (envelope). Each zone radius is the smallest distance beyond which
the envelope dose never exceeds the criterion; it is refined by log-linear
interpolation between the last distance that exceeds it and the next one.

Outputs, next to the inputs:
  zonas_emergencia.json   radii, criteria and dose–distance envelopes
  mapa_zonas.html         interactive viewer (visor_zonas.html with the results embedded):
                          ship on an OpenStreetMap background with the EAB and LPZ circles,
                          editable position, heading and dose criteria, dose–distance chart;
                          schematic view in metres when there is no internet access
  mapa_zonas.png          static schematic for reports (requires matplotlib)

Usage:
  python zonas_emergencia.py psf_batch/postprocess [--lat 43.353 --lon -3.086 --rumbo 300]
"""

from __future__ import annotations

import argparse, json, logging, math
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Optional

import numpy as np
import pandas as pd

REM_TO_MSV = 10.0

# Default berth: outer port of Bilbao (Zierbena LNG terminal area, approximate)
DEFAULT_LAT, DEFAULT_LON, DEFAULT_HEADING = 43.3530, -3.0860, 300.0


@dataclass
class Criterio:
    clave: str
    nombre: str
    limite_msv: float
    periodo: str
    color: str


# Siting criteria (10 CFR 50.34(a)(1)(ii)(D) / RG 1.183): 250 mSv TEDE
CRITERIOS = {
    "EAB": Criterio("EAB", "Límite del área de exclusión (EAB)", 250.0, "peores 2 h", "#c0392b"),
    "LPZ": Criterio("LPZ", "Zona de baja población (LPZ)", 250.0, "duración de la emisión (30 d)", "#e67e22"),
}


@dataclass
class Zona:
    clave: str
    nombre: str
    limite_msv: float
    periodo: str
    radio_m: Optional[float]      # None when the criterion is exceeded at every distance
    estado: str                   # "interpolado" | "menor_que_minimo" | "mayor_que_maximo"
    distancia_critica_m: Optional[float]
    set_critico: Optional[int]
    color: str


# ===========================================================================
# INPUT
# ===========================================================================
def leer_worst2h(xlsx: Path) -> pd.DataFrame:
    """Worst 2-h TEDE at the EAB per (set, distance) from Sets_Worst2h.xlsx."""
    rows = []
    for sheet, df in pd.read_excel(xlsx, sheet_name=None, engine="openpyxl").items():
        if not sheet.startswith("Set") or "TEDE_Worst2h_mSv" not in df.columns:
            continue
        sid = int(sheet[3:])
        for d, v in zip(df["distance_m"], df["TEDE_Worst2h_mSv"]):
            if pd.notna(d) and pd.notna(v):
                rows.append({"set_id": sid, "distance_m": float(d), "dosis_msv": float(v)})
    return pd.DataFrame(rows, columns=["set_id", "distance_m", "dosis_msv"])


def leer_acumulada(csv: Path) -> pd.DataFrame:
    df = pd.read_csv(csv)
    df["dosis_msv"] = df["TEDE_rem"] * REM_TO_MSV
    return df


def worst2h_desde_acumulada(acc: pd.DataFrame) -> pd.DataFrame:
    """Fallback: worst 2-h window of the cumulative EAB TEDE (linear interpolation)."""
    rows = []
    for (sid, d), g in acc[acc["receptor"] == "EAB"].groupby(["set_id", "distance_m"]):
        g = g.sort_values("time_h")
        t, D = g["time_h"].to_numpy(float), g["dosis_msv"].to_numpy(float)
        t, D = np.concatenate(([0.0], t)), np.concatenate(([0.0], D))
        grid = np.unique(np.concatenate((t, t + 2.0)))
        grid = grid[grid <= t[-1]]
        Dg = np.interp(grid, t, D)
        Dm2 = np.interp(np.maximum(grid - 2.0, 0.0), t, D)
        rows.append({"set_id": sid, "distance_m": float(d), "dosis_msv": float(np.max(Dg - Dm2))})
    return pd.DataFrame(rows, columns=["set_id", "distance_m", "dosis_msv"])


def lpz_desde_acumulada(acc: pd.DataFrame, horas: float = 720.0) -> pd.DataFrame:
    """Cumulative LPZ TEDE at the last output time not later than `horas`."""
    rows = []
    for (sid, d), g in acc[acc["receptor"] == "LPZ"].groupby(["set_id", "distance_m"]):
        g = g[g["time_h"] <= horas + 1e-9].sort_values("time_h")
        if not g.empty:
            rows.append({"set_id": sid, "distance_m": float(d), "dosis_msv": float(g["dosis_msv"].iloc[-1])})
    return pd.DataFrame(rows, columns=["set_id", "distance_m", "dosis_msv"])


# ===========================================================================
# RADIUS
# ===========================================================================
def envolvente(df: pd.DataFrame) -> pd.DataFrame:
    """Most unfavourable dose over the fraction sets at every distance."""
    idx = df.groupby("distance_m")["dosis_msv"].idxmax()
    return df.loc[idx].sort_values("distance_m").reset_index(drop=True)


def radio(env: pd.DataFrame, crit: Criterio) -> Zona:
    d = env["distance_m"].to_numpy(float)
    D = env["dosis_msv"].to_numpy(float)
    exceed = np.nonzero(D > crit.limite_msv)[0]
    base = dict(clave=crit.clave, nombre=crit.nombre, limite_msv=crit.limite_msv,
                periodo=crit.periodo, color=crit.color)
    if len(exceed) == 0:
        return Zona(radio_m=float(d[0]), estado="menor_que_minimo", distancia_critica_m=None,
                    set_critico=None, **base)
    k = exceed[-1]
    worst = int(env["set_id"].iloc[int(np.argmax(D))])
    if k == len(d) - 1:
        return Zona(radio_m=None, estado="mayor_que_maximo", distancia_critica_m=float(d[k]),
                    set_critico=worst, **base)
    d1, d2, D1, D2 = d[k], d[k + 1], D[k], D[k + 1]
    if D2 > 0 and D1 > 0:
        f = (math.log(D1) - math.log(crit.limite_msv)) / (math.log(D1) - math.log(D2))
    else:
        f = (D1 - crit.limite_msv) / (D1 - D2)
    return Zona(radio_m=float(d1 + f * (d2 - d1)), estado="interpolado", distancia_critica_m=float(d[k]),
                set_critico=worst, **base)


def calcular_zonas(postprocess: Path) -> Dict:
    acc_csv = postprocess / "post_timeseries_accum.csv"
    w2h_xlsx = postprocess / "Sets_Worst2h.xlsx"
    acc = leer_acumulada(acc_csv) if acc_csv.exists() else None
    if w2h_xlsx.exists():
        eab = leer_worst2h(w2h_xlsx)
    elif acc is not None:
        eab = worst2h_desde_acumulada(acc)
    else:
        raise FileNotFoundError(f"No RADTRAD post-processing found in {postprocess}")
    if acc is None:
        raise FileNotFoundError(f"{acc_csv} is required for the LPZ")
    lpz = lpz_desde_acumulada(acc)

    envs = {"EAB": envolvente(eab), "LPZ": envolvente(lpz)}
    zonas = [radio(envs[k], CRITERIOS[k]) for k in ("EAB", "LPZ")]
    return {
        "n_sets": int(eab["set_id"].nunique()),
        "zonas": [asdict(z) for z in zonas],
        "envolventes": {k: env[["distance_m", "dosis_msv", "set_id"]].to_dict("records")
                        for k, env in envs.items()},
    }


# ===========================================================================
# MAP
# ===========================================================================
VISOR = Path(__file__).resolve().parent / "visor_zonas.html"
PAGE = ('<!doctype html>\n<html lang="es"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">'
        '</head><body>\n%s\n</body></html>\n')


def escribir_mapa(resultado: Dict, html: Path, fuente: str = "") -> Path:
    """Interactive viewer (visor_zonas.html) with the results embedded."""
    data = dict(resultado, _fuente=fuente or html.parent.name)
    page = VISOR.read_text(encoding="utf-8").replace(
        "/*DATOS*/null/*FIN*/", "/*DATOS*/%s/*FIN*/" % json.dumps(data, ensure_ascii=False))
    html.write_text(PAGE % page, encoding="utf-8")
    return html


def escribir_png(resultado: Dict, png: Path, titulo: str = "Zonas de emergencia — Puerto de Bilbao") -> Optional[Path]:
    """Static schematic (local metres, north up) for reports; skipped without matplotlib."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.patches import Circle, Polygon
    except ImportError:
        logging.warning("matplotlib not installed: mapa_zonas.png not written")
        return None
    zonas = [z for z in resultado["zonas"] if z["radio_m"] is not None]
    R = max([z["radio_m"] for z in zonas] + [50.0]) * 1.2
    fig, ax = plt.subplots(figsize=(6.5, 6.5), dpi=150)
    ax.set_facecolor("#eef3f7")
    for z in sorted(zonas, key=lambda z: -z["radio_m"]):
        ax.add_patch(Circle((0, 0), z["radio_m"], facecolor=z["color"], alpha=0.12, edgecolor="none"))
        ax.add_patch(Circle((0, 0), z["radio_m"], fill=False, edgecolor=z["color"], lw=2,
                            label="%s: %s%.0f m (%.0f mSv, %s)" % (
                                z["clave"], "≤ " if z["estado"] == "menor_que_minimo" else "",
                                z["radio_m"], z["limite_msv"], z["periodo"])))
    a = math.radians(resultado.get("rumbo", 0.0))
    hull = [(0, 13), (6, 4), (6, -11), (-6, -11), (-6, 4)]
    s_ = R / 120.0
    pts = [(s_ * (x * math.cos(a) + y * math.sin(a)), s_ * (-x * math.sin(a) + y * math.cos(a))) for x, y in hull]
    ax.add_patch(Polygon(pts, closed=True, color="#1f4e79", zorder=5, label="Buque (icono no a escala)"))
    ax.annotate("N", xy=(0.93, 0.95), xytext=(0.93, 0.85), xycoords="axes fraction",
                ha="center", arrowprops=dict(arrowstyle="-|>", color="#333"))
    ax.set_xlim(-R, R)
    ax.set_ylim(-R, R)
    ax.set_aspect("equal")
    ax.set_xlabel("Distancia E–O al buque [m]")
    ax.set_ylabel("Distancia N–S al buque [m]")
    ax.set_title("%s\n(%.4f, %.4f)" % (titulo, resultado.get("lat", 0), resultado.get("lon", 0)), fontsize=10)
    ax.legend(loc="lower left", fontsize=8, framealpha=0.9)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(png)
    plt.close(fig)
    return png


def generar(postprocess: Path, lat: float = DEFAULT_LAT, lon: float = DEFAULT_LON,
            rumbo: float = DEFAULT_HEADING) -> Dict:
    """Compute the zones and write zonas_emergencia.json and mapa_zonas.html."""
    res = calcular_zonas(postprocess)
    res.update(lat=lat, lon=lon, rumbo=rumbo)
    (postprocess / "zonas_emergencia.json").write_text(
        json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
    escribir_mapa(res, postprocess / "mapa_zonas.html", str(postprocess))
    escribir_png(res, postprocess / "mapa_zonas.png")
    for z in res["zonas"]:
        if z["radio_m"] is None:
            logging.warning("%s: criterion exceeded at the largest distance (%s m) — extend the range",
                            z["clave"], z["distancia_critica_m"])
        else:
            logging.info("%s radius: %s%.0f m", z["clave"],
                         "≤ " if z["estado"] == "menor_que_minimo" else "", z["radio_m"])
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("postprocess", type=Path, help="PIPELINE postprocess folder")
    ap.add_argument("--lat", type=float, default=DEFAULT_LAT)
    ap.add_argument("--lon", type=float, default=DEFAULT_LON)
    ap.add_argument("--rumbo", type=float, default=DEFAULT_HEADING, help="ship heading [deg]")
    a = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)-8s %(message)s")
    generar(a.postprocess, a.lat, a.lon, a.rumbo)


if __name__ == "__main__":
    main()
