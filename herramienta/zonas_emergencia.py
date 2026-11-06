#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
zonas_emergencia.py  —  emergency zone radii and map from the PIPELINE.py results
============================================================================

Reads the RADTRAD post-processing written by PIPELINE.py
  <out_root>/postprocess/Sets_Worst2h.xlsx          (worst 2-h TEDE at the EAB)
  <out_root>/postprocess/post_timeseries_accum.csv  (cumulative TEDE per receptor)
for scenario E1 and, if run, scenario E2 (<out_root>/E2/postprocess), and evaluates the
zones of Table 4 of the memoria: EAB and LPZ (250 mSv TEDE, E1), evacuation (50 mSv,
7 d, E2), sheltering (10 mSv, 48 h), iodine prophylaxis (100 mSv thyroid, 7 d) and
planning zone (10 mSv, 96 h), envelope of E1 and E2, and deterministic effects (E2).
For every distance it takes the most unfavourable value over all the iodine fraction
sets (envelope). Each zone radius is the smallest distance beyond which
the envelope dose never exceeds the criterion; it is refined by log-linear
interpolation between the last distance that exceeds it and the next one.

Outputs, next to the inputs:
  zonas_emergencia.json   radii, criteria and dose–distance envelopes
  mapa_zonas.html         interactive viewer (visor_zonas.html with the results embedded):
                          ship on an OpenStreetMap base map with the EAB and LPZ circles,
                          editable position, heading and dose criteria, dose–distance chart;
                          schematic view in metres when there is no internet access
  mapa_zonas.png          static schematic for reports (requires matplotlib)

Usage:
  python zonas_emergencia.py psf_batch/postprocess [--lat 43.3605 --lon -3.082 --rumbo 300]
"""

from __future__ import annotations

import argparse, json, logging, math
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Optional

try:
    import numpy as np
    import pandas as pd
except ImportError:          # the map tab of the interface only needs the geometry and the map writer
    np = pd = None

REM_TO_MSV = 10.0

# Default berth: LNG carrier jetty of the Bahía de Bizkaia Gas (BBG) terminal, Punta Ceballos,
# Zierbena (outer port of Bilbao). APPROXIMATE position of the ship's centre: to be fixed on the
# satellite view of the viewer ("Copiar posición") and written here.
DEFAULT_LAT, DEFAULT_LON, DEFAULT_HEADING = 43.3605, -3.0820, 300.0
DEFAULT_BERTH = "Pantalán de metaneros de BBG, Punta Ceballos (Zierbena)"
# Reference ship (memoria, Table 7): LNG carrier, length overall and beam [m]
SHIP_LENGTH_M, SHIP_BEAM_M = 284.4, 42.5
SHIP_NAME = "Metanero de referencia (284,4 × 42,5 m)"
# Release point: the reactor, in the aft machinery space (memoria, chapter 6: 30–35 m long). Centre of
# that space measured from the stern; the zones are centred there, not amidships.
REACTOR_FROM_STERN_M = 28.0


def reactor_y(eslora: float = SHIP_LENGTH_M, desde_popa: float = REACTOR_FROM_STERN_M) -> float:
    """Position of the reactor along the ship axis, from amidships (negative = aft), metres."""
    return -(eslora / 2.0 - desde_popa)


def desplazar(lat: float, lon: float, este_m: float, norte_m: float):
    """lat/lon of a point east_m/north_m metres away (local flat-earth approximation)."""
    return lat + norte_m / 111320.0, lon + este_m / (111320.0 * math.cos(math.radians(lat)))


def posicion_reactor(lat, lon, rumbo, eslora=SHIP_LENGTH_M, desde_popa=REACTOR_FROM_STERN_M):
    """lat/lon of the reactor for a ship centred at lat/lon with the given heading (bow direction)."""
    a = math.radians(rumbo)
    y = reactor_y(eslora, desde_popa)
    return desplazar(lat, lon, y * math.sin(a), y * math.cos(a))


def casco(eslora: float = SHIP_LENGTH_M, manga: float = SHIP_BEAM_M):
    """Hull outline in ship axes (x to starboard, y to the bow), metres, centred amidships:
    parallel body, bow tapering over the forward 17 % of the length, square stern."""
    L, B = eslora / 2.0, manga / 2.0
    half = [(0.5 * B, 0.93 * L), (0.85 * B, 0.82 * L), (B, 0.66 * L), (B, -0.97 * L), (0.9 * B, -L)]
    return [(0.0, L)] + half + [(-x, y) for x, y in reversed(half)]


@dataclass
class Criterio:
    clave: str
    nombre: str
    limite_msv: float
    periodo: str
    color: str
    magnitud: str = "TEDE"          # "TEDE" or "Tiroides" (thyroid equivalent dose)
    horas: Optional[float] = None   # integration time of the cumulative dose (None: worst 2 h)
    escenarios: str = "E1"          # "E1", "E2" or "E1+E2" (envelope of both)


# Table 4 of the memoria (chapter 3): siting check (10 CFR 50.34 / RG 1.183, 250 mSv TEDE) and
# urgent protective action zones of the Directriz Básica (RD 1564/2010). Deterministic effects
# (1 Gy red marrow, 5 Gy thyroid in 48 h) are checked with the TEDE and the thyroid dose, which
# RADTRAD computes, as proxies of the absorbed doses.
CRITERIOS = {
    "EAB": Criterio("EAB", "Límite del área de exclusión (EAB)", 250.0, "peores 2 h", "#c0392b", "TEDE", None, "E1"),
    "LPZ": Criterio("LPZ", "Zona de baja población (LPZ)", 250.0, "30 días", "#e67e22", "TEDE", 720.0, "E1"),
    "EVAC": Criterio("EVAC", "Medidas urgentes: evacuación", 50.0, "7 días", "#8e44ad", "TEDE", 168.0, "E2"),
    "CONF": Criterio("CONF", "Medidas urgentes: confinamiento", 10.0, "48 h", "#2471a3", "TEDE", 48.0, "E1+E2"),
    "YODO": Criterio("YODO", "Profilaxis con yodo (tiroides)", 100.0, "7 días", "#16a085", "Tiroides", 168.0, "E1+E2"),
    "PLAN": Criterio("PLAN", "Zona de planificación de emergencias", 10.0, "96 h", "#7f8c8d", "TEDE", 96.0, "E1+E2"),
    "DETM": Criterio("DETM", "Efectos deterministas: médula (1 Gy, aprox. con TEDE)", 1000.0, "48 h", "#000000", "TEDE", 48.0, "E2"),
    "DETT": Criterio("DETT", "Efectos deterministas: tiroides (5 Gy)", 5000.0, "48 h", "#5d4037", "Tiroides", 48.0, "E2"),
}


@dataclass
class Zona:
    clave: str
    nombre: str
    limite_msv: float
    periodo: str
    magnitud: str
    escenarios: str
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
    df["tiroides_msv"] = df["Thyroid_rem"] * REM_TO_MSV if "Thyroid_rem" in df.columns else np.nan
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


def lpz_desde_acumulada(acc: pd.DataFrame, horas: float = 720.0, col: str = "dosis_msv") -> pd.DataFrame:
    """Cumulative dose of the LPZ receptor at `horas` (linear interpolation between output times;
    the LPZ and EAB receptors use the same χ/Q table, so either series gives the dose at that distance)."""
    rows = []
    for (sid, d), g in acc[acc["receptor"] == "LPZ"].groupby(["set_id", "distance_m"]):
        g = g.sort_values("time_h")
        t = np.concatenate(([0.0], g["time_h"].to_numpy(float)))
        D = np.concatenate(([0.0], g[col].to_numpy(float)))
        if len(t) > 1:
            rows.append({"set_id": sid, "distance_m": float(d), "dosis_msv": float(np.interp(min(horas, t[-1]), t, D))})
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
                periodo=crit.periodo, color=crit.color, magnitud=crit.magnitud, escenarios=crit.escenarios)
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


def radio_registros(registros, limite_msv: float):
    """radio() without pandas, on the envelope stored in zonas_emergencia.json
    ([{distance_m, dosis_msv, set_id}, …]). Returns (radio_m, estado)."""
    pts = sorted((float(r["distance_m"]), float(r["dosis_msv"])) for r in registros)
    if not pts:
        return None, "sin_datos"
    exceed = [i for i, (_, D) in enumerate(pts) if D > limite_msv]
    if not exceed:
        return pts[0][0], "menor_que_minimo"
    k = exceed[-1]
    if k == len(pts) - 1:
        return None, "mayor_que_maximo"
    (d1, D1), (d2, D2) = pts[k], pts[k + 1]
    if D1 > 0 and D2 > 0:
        f = (math.log(D1) - math.log(limite_msv)) / (math.log(D1) - math.log(D2))
    else:
        f = (D1 - limite_msv) / (D1 - D2)
    return d1 + f * (d2 - d1), "interpolado"


def _leer_escenario(postprocess: Path):
    """(worst 2-h EAB doses, cumulative series) of one scenario's postprocess folder."""
    acc_csv = postprocess / "post_timeseries_accum.csv"
    # If Sets_Worst2h.xlsx was open in Excel, PIPELINE.py saved Sets_Worst2h_01.xlsx, _02…:
    # take the newest one, and ignore it if it is older than this run's time series.
    found = sorted(postprocess.glob("Sets_Worst2h*.xlsx"), key=lambda f: f.stat().st_mtime)
    w2h_xlsx = found[-1] if found else None
    acc = leer_acumulada(acc_csv) if acc_csv.exists() else None
    if w2h_xlsx and acc_csv.exists() and w2h_xlsx.stat().st_mtime < acc_csv.stat().st_mtime - 60:
        logging.warning("%s is older than %s (from a previous run): using the time series",
                        w2h_xlsx.name, acc_csv.name)
        w2h_xlsx = None
    if w2h_xlsx:
        logging.info("Worst 2-h EAB doses from %s", w2h_xlsx.name)
        eab = leer_worst2h(w2h_xlsx)
    elif acc is not None:
        eab = worst2h_desde_acumulada(acc)
    else:
        raise FileNotFoundError(f"No RADTRAD post-processing found in {postprocess}")
    if acc is None:
        raise FileNotFoundError(f"{acc_csv} is required for the cumulative doses")
    return eab, acc


def _dosis(crit: Criterio, datos: Dict) -> pd.DataFrame:
    """Dose per (set, distance) for a criterion: worst 2 h at the EAB, or the cumulative TEDE or thyroid
    dose at the criterion's time; with "E1+E2", the most unfavourable of both scenarios."""
    partes = []
    for esc in crit.escenarios.split("+"):
        if esc not in datos:
            continue
        eab, acc = datos[esc]
        if crit.horas is None:
            df = eab
        else:
            col = "tiroides_msv" if crit.magnitud == "Tiroides" else "dosis_msv"
            df = lpz_desde_acumulada(acc, crit.horas, col)
        partes.append(df.assign(escenario=esc))
    if not partes:
        return pd.DataFrame(columns=["set_id", "distance_m", "dosis_msv", "escenario"])
    return pd.concat(partes, ignore_index=True)


def calcular_zonas(postprocess: Path, e2: Optional[Path] = None) -> Dict:
    """Zones of Table 4 of the memoria. `postprocess` holds E1; `e2` the E2 postprocess folder, if run.
    Without E2, the criteria assigned to E2 are evaluated with E1 and flagged."""
    datos = {"E1": _leer_escenario(postprocess)}
    if e2 is not None and Path(e2).exists():
        datos["E2"] = _leer_escenario(Path(e2))
    zonas, envs, avisos = [], {}, []
    for k, crit in CRITERIOS.items():
        c = crit
        if "E2" in crit.escenarios and "E2" not in datos:
            c = Criterio(**{**asdict(crit), "escenarios": "E1"})
            avisos.append(f"{k}: E2 no calculado, se usa E1")
        df = _dosis(c, datos)
        if df.empty:
            continue
        env = envolvente(df)
        envs[k] = env
        zonas.append(radio(env, c))
    eab1 = datos["E1"][0]
    return {
        "n_sets": int(eab1["set_id"].nunique()),
        "escenarios": sorted(datos),
        "avisos": avisos,
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
    # Leaflet goes inside the page, so mapa_zonas.html works on its own and offline
    leaflet = VISOR.parent / "vendor" / "leaflet" / "leaflet.js"
    tag = '<script src="vendor/leaflet/leaflet.js"></script>'
    if leaflet.exists() and tag in page:
        page = page.replace(tag, "<script>/* Leaflet 1.9.4, BSD-2-Clause, (c) Volodymyr Agafonkin */\n"
                            + leaflet.read_text(encoding="utf-8") + "\n</script>")
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
    R = max([z["radio_m"] for z in zonas] + [resultado.get("eslora_m", SHIP_LENGTH_M)]) * 1.1
    fig, ax = plt.subplots(figsize=(6.5, 6.5), dpi=150)
    ax.set_facecolor("#eef3f7")
    for z in sorted(zonas, key=lambda z: -z["radio_m"]):
        ax.add_patch(Circle((0, 0), z["radio_m"], facecolor=z["color"], alpha=0.12, edgecolor="none", zorder=2))
        ax.add_patch(Circle((0, 0), z["radio_m"], fill=False, edgecolor=z["color"], lw=2, zorder=3,
                            label="%s: %s%.0f m (%.0f mSv, %s)" % (
                                z["clave"], "≤ " if z["estado"] == "menor_que_minimo" else "",
                                z["radio_m"], z["limite_msv"], z["periodo"])))
    a = math.radians(resultado.get("rumbo", 0.0))
    eslora = resultado.get("eslora_m", SHIP_LENGTH_M)
    manga = resultado.get("manga_m", SHIP_BEAM_M)
    yr = reactor_y(eslora, resultado.get("reactor_desde_popa_m", REACTOR_FROM_STERN_M))
    # Origin at the reactor: hull points relative to it, rotated to east/north
    pts = [(x * math.cos(a) + (y - yr) * math.sin(a), -x * math.sin(a) + (y - yr) * math.cos(a))
           for x, y in casco(eslora, manga)]
    ax.add_patch(Polygon(pts, closed=True, facecolor="#1f4e79", edgecolor="white", lw=0.8, alpha=0.85, zorder=1,
                         label="Buque a escala (%.1f × %.1f m)" % (eslora, manga)))
    ax.plot([0], [0], marker="o", ms=6, mfc="#f1c40f", mec="black", zorder=6, ls="none",
            label="Reactor (%.0f m de la popa): centro de las zonas" % resultado.get("reactor_desde_popa_m", REACTOR_FROM_STERN_M))
    ax.annotate("N", xy=(0.93, 0.95), xytext=(0.93, 0.85), xycoords="axes fraction",
                ha="center", arrowprops=dict(arrowstyle="-|>", color="#333"))
    ax.set_xlim(-R, R)
    ax.set_ylim(-R, R)
    ax.set_aspect("equal")
    ax.set_xlabel("Distancia E–O al reactor [m]")
    ax.set_ylabel("Distancia N–S al reactor [m]")
    ax.set_title("%s\nReactor en (%.5f, %.5f)" % (titulo, resultado.get("reactor_lat", resultado.get("lat", 0)),
                                                resultado.get("reactor_lon", resultado.get("lon", 0))), fontsize=10)
    ax.legend(loc="lower left", fontsize=8, framealpha=0.9)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(png)
    plt.close(fig)
    return png


def generar(postprocess: Path, lat: float = DEFAULT_LAT, lon: float = DEFAULT_LON,
            rumbo: float = DEFAULT_HEADING, e2: Optional[Path] = None) -> Dict:
    """Compute the zones and write zonas_emergencia.json and mapa_zonas.html (in the E1 folder)."""
    res = calcular_zonas(postprocess, e2)
    rlat, rlon = posicion_reactor(lat, lon, rumbo)
    res.update(lat=lat, lon=lon, rumbo=rumbo, eslora_m=SHIP_LENGTH_M, manga_m=SHIP_BEAM_M, buque=SHIP_NAME,
               reactor_desde_popa_m=REACTOR_FROM_STERN_M, reactor_lat=rlat, reactor_lon=rlon,
               atraque=DEFAULT_BERTH if (lat, lon) == (DEFAULT_LAT, DEFAULT_LON) else "Posición personalizada")
    (postprocess / "zonas_emergencia.json").write_text(
        json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
    try:
        escribir_mapa(res, postprocess / "mapa_zonas.html", str(postprocess))
    except OSError as e:
        logging.error("mapa_zonas.html not written (%s): keep visor_zonas.html next to this script", e)
    escribir_png(res, postprocess / "mapa_zonas.png")
    for z in res["zonas"]:
        if z["radio_m"] is None:
            logging.warning("%s: criterion exceeded at the largest distance (%s m) — extend the range",
                            z["clave"], z["distancia_critica_m"])
        else:
            logging.info("%-4s %-55s %s%.0f m  (%s %g mSv, %s, %s)", z["clave"], z["nombre"],
                         "≤ " if z["estado"] == "menor_que_minimo" else "", z["radio_m"],
                         z["magnitud"], z["limite_msv"], z["periodo"], z["escenarios"])
    for a in res.get("avisos", []):
        logging.warning(a)
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("postprocess", type=Path, help="PIPELINE postprocess folder")
    ap.add_argument("--lat", type=float, default=DEFAULT_LAT)
    ap.add_argument("--lon", type=float, default=DEFAULT_LON)
    ap.add_argument("--rumbo", type=float, default=DEFAULT_HEADING, help="ship heading [deg]")
    ap.add_argument("--e2", type=Path, default=None,
                    help="postprocess folder of scenario E2 (default: <postprocess>/../E2/postprocess if it exists)")
    a = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)-8s %(message)s")
    e2 = a.e2 or (a.postprocess.parent / "E2" / "postprocess")
    generar(a.postprocess, a.lat, a.lon, a.rumbo, e2 if e2.exists() else None)


if __name__ == "__main__":
    main()
