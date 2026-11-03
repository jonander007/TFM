#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
preparar_met.py — check and repair the ARCON96 hourly meteorological files

ARCON96 needs one record per hour (KP-TR-012 §7.8.3) in fixed columns. The layout is the
one written by the author's RADTRAD_ENGINE.py (_met_build_line):
  " MET01 0100100  2250020 07  2670066"
    id    YYDDDHH  lower dir (3) + speed (4, 0.1 m/s)  stability  upper dir + speed
i.e. (1-based) lower direction 17-19, lower speed 20-23, stability 25-26, upper direction
29-31, upper speed 32-35. It reproduces, hour by hour, what ARCON96 printed in its QA output
(subroutine METREAD) for previous versions of the files. The original files had 3-digit
speeds and no leading blank, so ARCON96 read the stability out of range in every hour and
stopped with a division by zero.
This script reads datos/arcon/met_original/MET0n.MET and writes herramienta/MET0n.MET:
  * the year is written with two digits (MET01 used one), speeds with four digits and a
    leading blank, so every field falls in the columns ARCON96 reads;
  * direction 000 is written as 360 (ARCON96 takes north as 360, not 0);
  * a record whose day/hour breaks the sequence and duplicates a later one is relabelled
    with the hour it fills (MET05: "251 23" between 250 22 and 251 00 is 250 23);
  * missing hours (gaps of up to 11 h) are filled by interpolation between the records
    on both sides: circular for direction, linear for speed, nearest for stability. With
    --codigo-ausente they get 999/999/99 instead; ARCON96 stopped with rc=1 on files
    written that way, so it is not the default;
  * a summary (data recovery, calms, stability classes) is printed and written to
    datos/arcon/resumen_met.csv for the memoria.

Usage: python preparar_met.py [--codigo-ausente]
"""
import argparse, csv
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "datos" / "arcon" / "met_original"
MISSING = (999, 999, 99, 999, 999)
CALM = 5            # 0.5 m/s, ARCON96 minimum wind speed (KP-TR-012 §7.8.3.3)


def read(path):
    recs = []
    for ln in path.read_text(encoding="latin-1").splitlines():
        t = ln.split()
        if len(t) != 5:
            continue
        d = t[1]
        recs.append([t[0], int(d[:-5]), int(d[-5:-2]), int(d[-2:]),
                     (int(t[2][:3]), int(t[2][3:]), int(t[3]), int(t[4][:3]), int(t[4][3:]))])
    return recs


def fix_sequence(recs):
    """Relabel a record whose hour duplicates another and sits where an hour is missing."""
    notes = []
    keys = Counter((r[2], r[3]) for r in recs)
    for i in range(1, len(recs) - 1):
        k = (recs[i][2], recs[i][3])
        if keys[k] < 2:
            continue
        prev = (recs[i - 1][2] - 1) * 24 + recs[i - 1][3]
        nxt = (recs[i + 1][2] - 1) * 24 + recs[i + 1][3]
        if nxt - prev == 2:                                   # exactly one hour between neighbours
            h = prev + 1
            notes.append(f"day {k[0]} h{k[1]} -> day {h // 24 + 1} h{h % 24}")
            recs[i][2], recs[i][3] = h // 24 + 1, h % 24
            keys[k] -= 1
    return notes


def interpolate(a, b, f):
    da = (b[0] - a[0] + 180) % 360 - 180
    db = (b[3] - a[3] + 180) % 360 - 180
    return (round(a[0] + f * da) % 360 or 360, round(a[1] + f * (b[1] - a[1])), a[2] if f < 0.5 else b[2],
            round(a[3] + f * db) % 360 or 360, round(a[4] + f * (b[4] - a[4])))


def process(n, interp, outdir=HERE):
    recs = read(SRC / f"MET{n:02d}.MET")
    sid, year = recs[0][0], recs[0][1]
    notes = fix_sequence(recs)
    north = sum((r[4][0] == 0) + (r[4][3] == 0) for r in recs)
    for r in recs:
        v = r[4]
        r[4] = (v[0] or 360, v[1], v[2], v[3] or 360, v[4])
    if north:
        notes.append(f"{north} direcciones 000 -> 360")
    data = {(r[2], r[3]): r[4] for r in recs}
    ndays = max(r[2] for r in recs)
    hours = [(d, h) for d in range(1, ndays + 1) for h in range(24)]
    missing = [k for k in hours if k not in data]
    filled = dict(data)
    for k in missing:
        val = MISSING
        if interp:
            i = hours.index(k)
            lo = next((j for j in range(i - 1, -1, -1) if hours[j] in data), None)
            hi = next((j for j in range(i + 1, len(hours)) if hours[j] in data), None)
            if lo is not None and hi is not None and hi - lo - 1 <= 12:
                val = interpolate(data[hours[lo]], data[hours[hi]], (i - lo) / (hi - lo))
        filled[k] = val
    out = outdir / f"MET{n:02d}.MET"
    with out.open("w", encoding="latin-1", newline="\r\n") as f:
        for d, h in hours:
            v = filled[(d, h)]
            f.write(f" {sid} {year:02d}{d:03d}{h:02d}  {v[0]:03d}{v[1]:04d} {v[2]:02d}  {v[3]:03d}{v[4]:04d}\n")
    valid = [v for v in data.values()]
    st = Counter(v[2] for v in valid)
    summary = dict(fichero=out.name, horas=len(hours), registros_validos=len(data),
                   horas_faltantes=len(missing), recuperacion_pct=round(100 * len(data) / len(hours), 2),
                   calmas_pct=round(100 * sum(v[1] < CALM for v in valid) / len(valid), 2),
                   **{f"clase_{'ABCDEFG'[c - 1]}_pct": round(100 * st[c] / len(valid), 1) for c in range(1, 8)},
                   velocidad_media_10m=round(sum(v[1] for v in valid) / len(valid) / 10, 2),
                   correcciones="; ".join(notes + ([f"año con 2 cifras"] if n == 1 else [])))
    return summary


def check_columns(path):
    """Read a file back with ARCON96's columns and return the number of invalid hours."""
    bad = 0
    for ln in path.read_text(encoding="latin-1").splitlines():
        ln = ln.ljust(35)                       # blanks are ignored, as ARCON96 does (BN)
        d1, s1, st, d2, s2 = (int(ln[a:b].replace(" ", "") or 0) for a, b in ((16, 19), (19, 23), (24, 26), (28, 31), (31, 35)))
        bad += not (1 <= d1 <= 360 and 1 <= d2 <= 360 and 1 <= st <= 7 and s1 < 9999 and s2 < 9999)
    return bad


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--codigo-ausente", action="store_true",
                    help="fill gaps with 999/999/99 instead of interpolating")
    a = ap.parse_args()
    rows = [process(n, not a.codigo_ausente) for n in range(1, 6)]
    with (HERE.parent / "datos" / "arcon" / "resumen_met.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    for r in rows:
        print(r)
    for n in range(1, 6):
        f = HERE / f"MET{n:02d}.MET"
        print(f"{f.name}: {check_columns(f)} hours invalid when read with ARCON96 columns")


if __name__ == "__main__":
    main()
