#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sensibilidad_met.py — meteorological sensitivity case (memoria, chapter 10)

The adapted meteorological series has class A (very unstable) in about 27 % of the hours with
winds of about 7 m/s, a combination that favours dilution and may underestimate χ/Q. This
script repeats the whole chain with deterministic, unfavourable meteorology: Pasquill class F
(moderately stable) and 1 m/s every hour, the conditions of the first 12 h of ARPANSA's 2000
reference accident. With a constant wind the 95th percentile of the 360° window and the
99.5th percentile of the sector that contains the wind are the χ/Q of those conditions.

  * writes MET01.MET (one year, 8760 hours, same format and columns as preparar_met.py);
  * runs PIPELINE.run() with that file in separate folders (ARCON96 in <base>/ARCON_F1,
    RADTRAD in <out_root>_F1, with E1 and E2 if the E2 inventory is in Defaults);
  * the zones and the map of the sensitivity case are in <out_root>_F1/postprocess.

Usage (console): python sensibilidad_met.py   — asks the same questions as PIPELINE.py
(the number of MET files is ignored) and runs the sensitivity case.
The graphical interface runs it after the base case when "Sensibilidad meteorológica" is ticked.
"""
from __future__ import annotations

import logging
from pathlib import Path

CLASE_F = 6          # ARCON96 stability code: 1..7 = A..G
VIENTO = 1.0         # m/s, at both measurement heights
DIRECCION = 270      # deg (any: the 360° window ignores it and one sector contains it)


def escribir_met(out_dir: Path, clase: int = CLASE_F, viento: float = VIENTO, direccion: int = DIRECCION,
                 dias: int = 365) -> Path:
    """One year of hourly records with constant class and wind, in ARCON96's fixed columns."""
    out_dir.mkdir(parents=True, exist_ok=True)
    met = out_dir / "MET01.MET"
    v = int(round(viento * 10))
    with met.open("w", encoding="latin-1", newline="\r\n") as f:
        for d in range(1, dias + 1):
            for h in range(24):
                f.write(f" MET01 01{d:03d}{h:02d}  {direccion:03d}{v:04d} {clase:02d}  {direccion:03d}{v:04d}\n")
    return met


def ejecutar(params: dict, base: Path, out_root: Path, arcon_exe=None, radtrad_exe=None,
             defaults_dir=None) -> int:
    """Run PIPELINE.run() with the deterministic meteorology. `params` are those of the base case."""
    import PIPELINE as P
    met_dir = base / "MET_F1"
    escribir_met(met_dir)
    logging.info("=" * 62)
    logging.info("METEOROLOGICAL SENSITIVITY: class F, %.1f m/s every hour (%s)", VIENTO, met_dir)
    logging.info("=" * 62)
    P.configure(arcon_dir=base / "ARCON_F1", met_dir=met_dir, defaults_dir=defaults_dir,
                arcon_exe=arcon_exe, radtrad_exe=radtrad_exe)
    p = dict(params)
    p.update(num_met=1, out_root=Path(out_root), out_action="1", run_arcon=True, run_radtrad=True)
    return P.run(p)


def main():
    import PIPELINE as P
    P.setup_logging()
    params = P.ask_all_params()
    out_root = Path(str(params["out_root"]) + "_F1")
    return ejecutar(params, Path.cwd(), out_root)


if __name__ == "__main__":
    raise SystemExit(main())
