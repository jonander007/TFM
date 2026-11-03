#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
normalizar_inventario.py — normalize the core inventory to the reactor power and add the
short-lived iodines and noble gases

Run after datos/nubase2020/actualizar_semividas.py, on its output:
  python datos/rendimientos_fision/normalizar_inventario.py [workbook] [--potencia 320]

1. Fuel-material fraction. The Kairos ECC number densities are those of the fuel material
   (UCO kernel of the TRISO particles). The workbook multiplied them by the whole core
   cylinder (K97, K98), which gives about 156 times the activity that corresponds to
   320 MWth (comprobar_normalizacion.py). A new cell K99 holds the fraction of the
   cylinder occupied by fuel material, 1/k, and the volume column P is multiplied by it.
   k is the median ratio between that activity and Y·F for Xe-133, Ba-140, Pr-143,
   Nd-147 and Pm-149.

2. Short-lived fission products missing from the public data set (I-131 to I-135, Te-132,
   Kr-85m, Kr-87, Kr-88, Xe-133m, Xe-135m, Xe-138) are added below the core data block
   with their equilibrium activity A = Y·F (cumulative yield, ENDF/B-VIII.0, U-235 thermal,
   column BJ; fission rate in K101 from the power in K100). Their attenuation factors and
   per-barrier formulas are copied from a nuclide of the same chemical group (I-129 for
   iodine and tellurium, Xe-133 for noble gases).

The Hoja1 sheet (Anexo C) is rebuilt with the new rows. Open and save the workbook in
Excel/LibreOffice (or run the xlsx recalc script) so the cached values are updated before
running herramienta/generar_nif.py.
"""
import argparse, math, re, sys
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.comments import Comment
from openpyxl.styles import Font

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "nubase2020"))
from comprobar_normalizacion import BOOK, SHEET, cumulative_yields, factor_normalizacion, fission_rate  # noqa: E402
from nubase import half_life  # noqa: E402
import actualizar_semividas as au  # noqa: E402

COL_YIELD, COL_STATE = 62, 63          # BJ, BK
MARKER = "Productos de fisión de vida corta añadidos (A = Y·F)"
FIRST_NEW_ROW = 106
# (ZZAAA, isomeric state, group reference nuclide)
SHORT_LIVED = [(52132, 0, "I-129"), (53131, 0, "I-129"), (53132, 0, "I-129"), (53133, 0, "I-129"),
               (53134, 0, "I-129"), (53135, 0, "I-129"),
               (36085, 1, "Xe-133"), (36087, 0, "Xe-133"), (36088, 0, "Xe-133"),
               (54133, 1, "Xe-133"), (54135, 1, "Xe-133"), (54138, 0, "Xe-133")]
CELL_REF = re.compile(r"(\$?[A-Z]{1,3})(\$?)(\d+)")


def name_of(zz, state):
    return au.name_of(zz) + ("m" if state else "")


def shift_formula(f, src_row, dst_row):
    """Point the relative references to src_row at dst_row ($-anchored rows stay)."""
    return CELL_REF.sub(lambda m: m.group(0) if m.group(2) or int(m.group(3)) != src_row
                        else f"{m.group(1)}{dst_row}", f)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("libro", nargs="?", type=Path, default=BOOK)
    ap.add_argument("--potencia", type=float, default=320.0)
    a = ap.parse_args()

    k = factor_normalizacion(a.potencia, a.libro)
    cum = cumulative_yields()
    wb = load_workbook(a.libro)
    ws = wb[SHEET]

    # 1. fuel-material fraction, power and fission rate next to the core dimensions
    for r, label, value, note in (
            (99, "Fracción de material combustible", round(1 / k, 7),
             f"Las densidades del ECC son del material combustible (núcleo UCO de las TRISO). "
             f"Fracción del cilindro del núcleo que ocupa: 1/{k:.1f}, obtenida igualando la actividad "
             f"de Xe-133, Ba-140, Pr-143, Nd-147 y Pm-149 a Y·F a {a.potencia:g} MWth "
             f"(datos/rendimientos_fision/comprobar_normalizacion.py)."),
            (100, "Potencia térmica (MWth)", a.potencia, None),
            (101, "Tasa de fisiones (1/s)", "=K100*1E6/(200*1.602176634E-13)", "200 MeV por fisión")):
        ws.cell(r, 10, label)
        ws.cell(r, 11, value)
        if note:
            ws.cell(r, 10).comment = Comment(note, "TFM")
    ws.cell(3, 16, "Volumen de material combustible (cm3)")
    for r in range(4, ws.max_row + 1):
        f = ws.cell(r, 16).value
        if isinstance(f, str) and f.startswith("=PI()*$K$97^2*$K$98"):
            ws.cell(r, 16, "=PI()*$K$97^2*$K$98*$K$99")

    # 2. short-lived fission products
    old = next((r for r in range(4, ws.max_row + 1) if ws.cell(r, 2).value == MARKER), None)
    if old:
        ws.delete_rows(old, ws.max_row - old + 1)
    ref = {ws.cell(r, 2).value: r for r in range(4, 93) if ws.cell(r, 2).value}
    ws.cell(3, COL_YIELD, "Rendimiento acumulado (ENDF/B-VIII.0, U-235 térmico)").font = Font(bold=True)
    ws.cell(3, COL_STATE, "Estado isomérico").font = Font(bold=True)
    ws.cell(FIRST_NEW_ROW - 1, 2, MARKER).font = Font(bold=True)
    rows = []
    for i, (zz, state, ref_name) in enumerate(SHORT_LIVED):
        r, s = FIRST_NEW_ROW + i, ref[ref_name]
        T, txt = half_life(zz, state)
        name = name_of(zz, state)
        ws.cell(r, 2, name)
        ws.cell(r, 3, zz)
        ws.cell(r, 4, ws.cell(s, 4).value)
        ws.cell(r, 13, f"=IF(ISNUMBER(BG{r}),BG{r},\"\")")
        ws.cell(r, 14, f"=IF(ISNUMBER(M{r}),LN(2)/M{r},0)")
        ws.cell(r, 19, f"=BJ{r}*$K$101")
        ws.cell(r, 20, f"=S{r}*0.000000000027")
        ws.cell(r, 21, f"=D{r}")
        for c in au.AF_VALUES:
            ws.cell(r, c, ws.cell(s, c).value)
        for c in au.AF_FORMULAS:
            f = ws.cell(s, c).value
            ws.cell(r, c, shift_formula(f, s, r) if isinstance(f, str) else f)
        ws.cell(r, au.COL_TXT, txt)
        ws.cell(r, au.COL_S, T)
        ws.cell(r, COL_YIELD, cum[(zz, state)])
        ws.cell(r, COL_STATE, state)
        ws.cell(r, au.COL_OLD + 1, f"Añadido: A = Y·F; factores de atenuación del grupo de {ref_name}")
        rows.append((r, name, cum[(zz, state)] * fission_rate(a.potencia)))

    # 3. Anexo C with the normalized core rows and the new ones
    core = []
    for r in range(4, 93):
        zz, nb = ws.cell(r, 3).value, ws.cell(r, 5).value
        if not isinstance(zz, int) or not isinstance(nb, (int, float)):
            continue
        try:
            T, _ = half_life(zz)
        except KeyError:
            continue
        if T and T <= au.PRACTICALLY_STABLE_S:
            V = math.pi * ws["K97"].value ** 2 * ws["K98"].value / k
            core.append((r, ws.cell(r, 2).value, nb * 1e24 * V * math.log(2) / T))
    n = au.rebuild_annex(wb, SHEET, core + rows)
    wb.save(a.libro)
    print(f"{a.libro.name}: fuel-material fraction 1/{k:.1f} = {1 / k:.4%}; "
          f"{len(rows)} short-lived nuclides added; Hoja1 rebuilt with {n} nuclides")


if __name__ == "__main__":
    main()
