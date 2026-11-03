#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
completar_inp.py — add tritium (H-3) to RADTRAD's dose conversion factor file

RADTRAD's fgr11&12.inp has 60 nuclides and no H-3, which dominates the KP-FHR source term.
This script writes a copy with an H-3 entry:
  * inhaled (chronic column): 1.73E-11 Sv/Bq for every organ and the effective dose,
    FGR 11 value for tritiated water vapour (tritium is distributed uniformly in body water;
    taking the HTO form is conservative, elemental tritium is about 10^4 times less
    radiotoxic);
  * ingestion: same value;
  * cloudshine and ground shine: 0 (beta emitter of 18.6 keV maximum energy, no
    penetrating radiation); skin: 0.
The "INHALED ACUTE" column keeps the -1 flag used by every other nuclide of the file.

Usage: python completar_inp.py [input.inp] [output.inp]
       (default: Defaults/fgr11&12_original.inp -> Defaults/fgr11&12.inp)
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
H3_SV_PER_BQ = 1.73e-11
ORGANS = ["GONADS", "BREAST", "LUNGS", "RED MARR", "BONE SUR", "THYROID", "REMAINDER", "EFFECTIVE", "SKIN(FGR)"]


def h3_block():
    lines = ["H-3     "]
    for org in ORGANS:
        inh = 0.0 if org == "SKIN(FGR)" else H3_SV_PER_BQ
        vals = [0.0, 0.0, 0.0, 0.0]
        row = f"{org:<10s}" + "".join(f" {v:9.3E}" for v in vals) + "-1.000E+00" + f" {inh:9.3E} {inh:9.3E}"
        lines.append(row)
    return lines


def main(src, dst):
    raw = Path(src).read_bytes()
    nl = "\r\n" if b"\r\n" in raw else "\n"
    lines = raw.decode("latin-1").split(nl)
    if any(l.startswith("H-3 ") for l in lines):
        print("H-3 already present; nothing to do")
        Path(dst).write_bytes(raw)
        return
    i = next(k for k, l in enumerate(lines) if "NUCLIDES DEFINED IN THIS FILE" in l)
    n = int(lines[i].split()[0])
    lines[i] = lines[i].replace(str(n), str(n + 1), 1).rjust(len(lines[i]))
    lines.insert(i + 1, "H-3".ljust(len(lines[i + 1])))
    j = next(k for k, l in enumerate(lines) if l.startswith("Co-58") and k > i + n + 1)
    lines[j:j] = h3_block()
    Path(dst).write_bytes(nl.join(lines).encode("latin-1"))
    print(f"{dst}: {n + 1} nuclides (H-3 added, {H3_SV_PER_BQ:.2E} Sv/Bq inhaled)")


if __name__ == "__main__":
    a = sys.argv[1:]
    main(a[0] if a else HERE / "Defaults" / "fgr11&12_original.inp",
         a[1] if len(a) > 1 else HERE / "Defaults" / "fgr11&12.inp")
