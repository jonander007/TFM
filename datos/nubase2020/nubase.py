#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
nubase.py — half-lives from NUBASE2020 (datos/nubase2020/nubase_4.mas20.txt)

F.G. Kondev, M. Wang, W.J. Huang, S. Naimi, G. Audi,
"The NUBASE2020 evaluation of nuclear physics properties", Chin. Phys. C 45, 030001 (2021).
The file is the original AMDC distribution (sha256 1585a5ee…9859).

half_life(zzaaa) -> (seconds | None for stable, text as written in NUBASE)
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional, Tuple

NUBASE_FILE = Path(__file__).resolve().parent / "nubase_4.mas20.txt"

# NUBASE2020 uses 1 y = 365.2422 d (Kondev et al. 2021, section 2)
YEAR_S = 365.2422 * 86400.0
UNITS = {"ys": 1e-24, "zs": 1e-21, "as": 1e-18, "fs": 1e-15, "ps": 1e-12, "ns": 1e-9, "us": 1e-6,
         "ms": 1e-3, "s": 1.0, "m": 60.0, "h": 3600.0, "d": 86400.0, "y": YEAR_S,
         "ky": 1e3 * YEAR_S, "My": 1e6 * YEAR_S, "Gy": 1e9 * YEAR_S, "Ty": 1e12 * YEAR_S,
         "Py": 1e15 * YEAR_S, "Ey": 1e18 * YEAR_S, "Zy": 1e21 * YEAR_S, "Yy": 1e24 * YEAR_S}

_cache: Dict[int, Tuple[Optional[float], str]] = {}


def _load() -> None:
    for ln in NUBASE_FILE.read_text(encoding="latin-1").splitlines():
        if ln.startswith("#") or len(ln) < 80:
            continue
        a, zi = int(ln[0:3]), ln[4:8]
        if zi[3] != "0":                       # ground states only
            continue
        z = int(zi[:3])
        t, unit = ln[69:78].strip(), ln[78:80].strip()
        if t == "stbl":
            _cache[z * 1000 + a] = (None, "estable")
            continue
        try:
            value = float(t.replace("#", "").replace(">", "").replace("<", "").replace("~", ""))
        except ValueError:                      # p-unst, blank, …
            continue
        if unit not in UNITS:
            continue
        _cache[z * 1000 + a] = (value * UNITS[unit], f"{t} {unit}")


def half_life(zzaaa: int) -> Tuple[Optional[float], str]:
    """(T½ in s or None if stable, original NUBASE text). KeyError if not in NUBASE."""
    if not _cache:
        _load()
    return _cache[int(zzaaa)]


if __name__ == "__main__":
    for zz in (55137, 53131, 54133, 95243, 92237, 56138):
        print(zz, half_life(zz))
