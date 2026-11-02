#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
comprobar_normalizacion.py — check the core inventory against the reactor power

For short-lived fission products (half-life of days) the core activity at equilibrium
is fixed by the fission rate: A_i = Y_i · F, with Y_i the cumulative fission yield and
F = P / E_f the fission rate. Comparing that with the activity in the inventory workbook
(number density × reference volume × λ) tells whether the reference volume is right.

Yields: ENDF/B-VIII.0, U-235, thermal (0.0253 eV), MT459 (U235_nfy_endfb80.endf, extracted
from the nfpy_endfb_80 archive distributed with the SANDY package). Pu-239 fissions are
ignored, so nuclides with very different Pu yields (Rh-105, Ru-103) scatter more.

Usage: python comprobar_normalizacion.py [--potencia 320]
"""
import argparse, statistics, sys
from pathlib import Path
from openpyxl import load_workbook

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from endf_nfy import yields  # noqa: E402

BOOK = HERE.parent / "inventario" / "Calculosfueradelacontencion_NUBASE2020.xlsx"
SHEET = "AZ6 RZ1 (ACCIDENT)"
E_FISSION_J = 200 * 1.602176634e-13      # 200 MeV recoverable energy per fission
CLEAN = {"Xe-133", "Ba-140", "Pr-143", "Nd-147", "Pm-149"}   # short-lived, similar U/Pu yields


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--potencia", type=float, default=320.0, help="thermal power [MWth]")
    a = ap.parse_args()
    F = a.potencia * 1e6 / E_FISSION_J
    th = yields(HERE / "U235_nfy_endfb80.endf", 9228, 459)[0.0253]
    cum = {za: v for (za, iso), (v, dv) in th.items() if iso == 0}
    ws = load_workbook(BOOK, data_only=True)[SHEET]
    vol = ws["K97"].value, ws["K98"].value
    ratios = {}
    print(f"Power {a.potencia:g} MWth -> {F:.3e} fissions/s; core cylinder r = {vol[0]} cm, h = {vol[1]} cm\n")
    print(f"{'nuclide':8s} {'T1/2 (d)':>9s} {'A workbook (Bq)':>16s} {'Y·F (Bq)':>11s} {'ratio':>7s}")
    for r in range(4, ws.max_row + 1):
        name, zz, T, A = ws.cell(r, 2).value, ws.cell(r, 3).value, ws.cell(r, 13).value, ws.cell(r, 19).value
        if not (isinstance(zz, int) and isinstance(T, (int, float)) and isinstance(A, (int, float))):
            continue
        if A <= 0 or T > 120 * 86400 or zz not in cum:
            continue
        ratio = A / (cum[zz] * F)
        ratios[name] = ratio
        print(f"{name:8s} {T / 86400:9.2f} {A:16.3e} {cum[zz] * F:11.3e} {ratio:7.1f}")
    k = statistics.median(ratios[n] for n in CLEAN if n in ratios)
    V = 3.141592653589793 * vol[0] ** 2 * vol[1]
    print(f"\nMedian ratio for {', '.join(sorted(CLEAN))}: {k:.0f}")
    print(f"The workbook inventory corresponds to about {k * a.potencia / 1000:.0f} GWth.")
    print(f"Volume consistent with {a.potencia:g} MWth: {V / k / 1e6:.4f} m3 of fuel material "
          f"(vs {V / 1e6:.2f} m3 used), i.e. {1 / k:.2%} of the core cylinder.")


if __name__ == "__main__":
    main()
