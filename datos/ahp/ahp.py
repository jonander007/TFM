#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ahp.py — weights, consistency and scores of the SMART / AHP model (Nuproship.smt)

Reads the SMART project file (JSON) and reproduces the AHP calculation (Saaty, 1980):
  * each pairwise comparison matrix is built from the upper-triangle entries
    ("('A', 'B')": v means A is v times as important as B) and its reciprocals;
  * priorities = normalized principal eigenvector; consistency index
    CI = (λmax − n)/(n − 1) and ratio CR = CI/RI, with Saaty's random index RI;
  * rating scales: intensities from their own comparison matrices, idealized
    (divided by the largest), as in the ratings mode of AHP;
  * global score of each alternative = Σ (global weight of subcriterion × intensity
    of its rating).
Writes resultados_ahp.json and prints the tables used in Anexo B of the memoria.

Usage: python ahp.py [Nuproship.smt]
"""
import ast, json, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
RI = {1: 0.0, 2: 0.0, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}


def matrix(items, comparisons):
    n = len(items)
    A = np.ones((n, n))
    for key, v in comparisons.items():
        a, b = ast.literal_eval(key)
        i, j = items.index(a), items.index(b)
        A[i, j], A[j, i] = v, 1.0 / v
    return A


def priorities(A):
    vals, vecs = np.linalg.eig(A)
    k = int(np.argmax(vals.real))
    w = np.abs(vecs[:, k].real)
    w /= w.sum()
    n = len(A)
    lmax = float(vals[k].real)
    ci = (lmax - n) / (n - 1) if n > 2 else 0.0
    cr = ci / RI[n] if RI.get(n) else 0.0
    return w, lmax, cr


def main(path):
    smt = json.loads(Path(path).read_text(encoding="utf-8"))
    goal, = smt["Criteria"]["Criteria"]
    tree = {list(c)[0]: list(c.values())[0]["children"] for c in smt["Criteria"]["Criteria"][goal]["children"]}
    comp = smt["Criteria Comparison"]["Criteria Comparison"]
    crit = list(tree)
    wc, lmax, cr = priorities(matrix(crit, comp[goal]))
    out = {"criterios": {}, "consistencia": {goal: cr}, "subcriterios": {}, "intensidades": {}, "puntuaciones": {}}
    for c, w in zip(crit, wc):
        out["criterios"][c] = w
        subs = tree[c]
        ws, _, crs = priorities(matrix(subs, comp.get(c, {}))) if len(subs) > 1 else (np.array([1.0]), 1, 0)
        out["consistencia"][c] = crs
        for s, v in zip(subs, ws):
            out["subcriterios"][s] = {"criterio": c, "local": v, "global": w * v}
    scales = smt["Alternative Rating"]["Rating Scales Creation"]
    scomp = smt["Alternative Rating"]["Rating Scales Comparison"]
    for s, levels in scales.items():
        levels = [l for l in levels if l is not False]
        wl, _, crl = priorities(matrix(levels, scomp[s]))
        out["intensidades"][s] = dict(zip(levels, wl / wl.max()))
        out["consistencia"]["escala " + s] = crl
    for alt, ratings in smt["Alternative Rating"]["Rating Table"].items():
        out["puntuaciones"][alt] = sum(out["subcriterios"][s]["global"] * out["intensidades"][s][r]
                                       for s, r in ratings.items())
    (HERE / "resultados_ahp.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Criteria (λmax = {lmax:.3f}, CR = {cr:.3f}):")
    for c, w in sorted(out["criterios"].items(), key=lambda x: -x[1]):
        print(f"  {c:35s} {w:.3f}   CR sub = {out['consistencia'][c]:.3f}")
        for s, d in out["subcriterios"].items():
            if d["criterio"] == c:
                print(f"      {s:32s} local {d['local']:.3f}  global {d['global']:.3f}")
    print("Max CR of rating scales:", max(v for k, v in out["consistencia"].items() if k.startswith("escala")))
    tot = sum(out["puntuaciones"].values())
    for a, v in sorted(out["puntuaciones"].items(), key=lambda x: -x[1]):
        print(f"  {a:10s} ideal {v:.3f}   normalized {v / tot:.3f}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else HERE / "Nuproship.smt")
