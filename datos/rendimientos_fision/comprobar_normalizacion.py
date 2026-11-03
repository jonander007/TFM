#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
comprobar_normalizacion.py — check the core inventory against the reactor power

For short-lived fission products (half-life of days) the core activity at equilibrium
is fixed by the fission rate: A_i = Y_i · F, with Y_i the cumulative fission yield and
F = P / E_f the fission rate. Comparing that with the activity obtained from the Kairos
number densities and the reference volume tells whether that volume is right.

The densities of the Kairos ECC data set are those of the fuel material (the UCO kernel
of the TRISO particles), so multiplying them by the whole core cylinder overestimates
the inventory. factor_normalizacion() returns the ratio, computed from the densities
themselves (not from the workbook activity column, which already carries the fix).

Yields: ENDF/B-VIII.0, U-235, thermal (0.0253 eV), MT459 (U235_nfy_endfb80.endf, extracted
from the nfpy_endfb_80 archive distributed with the SANDY package). Pu-239 fissions are
ignored, so nuclides with very different Pu yields (Rh-105, Ru-103) scatter more.

Usage: python comprobar_normalizacion.py [--potencia 320]
"""
import argparse, math, statistics, sys
from pathlib import Path
from openpyxl import load_workbook

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "nubase2020"))
from endf_nfy import yields  # noqa: E402
from nubase import half_life  # noqa: E402

BOOK = HERE.parent / "inventario" / "Calculosfueradelacontencion_NUBASE2020.xlsx"
SHEET = "AZ6 RZ1 (ACCIDENT)"
E_FISSION_J = 200 * 1.602176634e-13      # 200 MeV recoverable energy per fission
CLEAN = {"Xe-133", "Ba-140", "Pr-143", "Nd-147", "Pm-149"}   # short-lived, similar U/Pu yields


def cumulative_yields():
    """{(ZZAAA, state): cumulative yield per fission}, U-235 thermal, ENDF/B-VIII.0."""
    th = yields(HERE / "U235_nfy_endfb80.endf", 9228, 459)[0.0253]
    return {key: v for key, (v, dv) in th.items()}


def fission_rate(power_mwth):
    return power_mwth * 1e6 / E_FISSION_J


def factor_normalizacion(power_mwth=320.0, book=BOOK, verbose=False):
    """Ratio between the density-based activity (whole core cylinder) and Y·F."""
    F = fission_rate(power_mwth)
    cum = cumulative_yields()
    ws = load_workbook(book, data_only=True)[SHEET]
    V = math.pi * ws["K97"].value ** 2 * ws["K98"].value
    ratios = {}
    if verbose:
        print(f"Power {power_mwth:g} MWth -> {F:.3e} fissions/s; core cylinder "
              f"r = {ws['K97'].value} cm, h = {ws['K98'].value} cm ({V / 1e6:.2f} m3)\n")
        print(f"{'nuclide':8s} {'T1/2 (d)':>9s} {'A densities (Bq)':>17s} {'Y·F (Bq)':>11s} {'ratio':>7s}")
    for r in range(4, ws.max_row + 1):
        name, zz, nb = ws.cell(r, 2).value, ws.cell(r, 3).value, ws.cell(r, 5).value
        if not (isinstance(zz, int) and isinstance(nb, (int, float))) or (zz, 0) not in cum:
            continue
        try:
            T, _ = half_life(zz)
        except KeyError:
            continue
        if T is None or T > 120 * 86400:
            continue
        A = nb * 1e24 * V * math.log(2) / T
        ratios[name] = A / (cum[(zz, 0)] * F)
        if verbose:
            print(f"{name:8s} {T / 86400:9.2f} {A:17.3e} {cum[(zz, 0)] * F:11.3e} {ratios[name]:7.1f}")
    k = statistics.median(ratios[n] for n in CLEAN if n in ratios)
    if verbose:
        print(f"\nMedian ratio for {', '.join(sorted(CLEAN))}: {k:.1f}")
        print(f"Densities × core cylinder correspond to about {k * power_mwth / 1000:.0f} GWth.")
        print(f"Fuel material consistent with {power_mwth:g} MWth: {V / k / 1e6:.4f} m3 "
              f"({1 / k:.3%} of the core cylinder).")
    return k


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--potencia", type=float, default=320.0, help="thermal power [MWth]")
    factor_normalizacion(ap.parse_args().potencia, verbose=True)
