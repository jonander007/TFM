import json, math
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
exec(open('datos.py').read().split("if __name__")[0])
plt.rcParams.update({"font.size": 10, "font.family": "DejaVu Sans"})
# --- χ/Q
fig, ax = plt.subplots(figsize=(7, 4.6), dpi=200)
lab = {'0-2': '0–2 h', '2-8': '2–8 h', '8-24': '8–24 h', '1-4d': '1–4 días', '4-30d': '4–30 días'}
sty = {'0-2': ('#1f4e79', '-'), '2-8': ('#2e86c1', '-'), '8-24': ('#7f8c8d', '-'), '1-4d': ('#d35400', '--'), '4-30d': ('#8e44ad', ':')}
for kk in lab:
    ax.loglog(V, [STD[v][kk] for v in V], sty[kk][1], color=sty[kk][0], lw=1.8, label=lab[kk])
ax.set_xlabel("Distancia al reactor (m)"); ax.set_ylabel("χ/Q de diseño (s/m³)")
ax.grid(True, which="both", alpha=.3); ax.legend(title="Intervalo", fontsize=9)
ax.set_xlim(10, 400)
fig.tight_layout(); fig.savefig("fig/xq_distancia.png"); plt.close(fig)
# --- dose
fig, ax = plt.subplots(figsize=(7, 4.8), dpi=200)
ax.loglog(V, [D[v][0] for v in V], "-", color="#1f4e79", lw=2.2, label="Caso base (RADTRAD), TEDE peores 2 h")
ax.loglog(V, [KT * xqF(v) for v in V], "--", color="#c0392b", lw=1.8, label="Clase F, 1 m/s (estimación)")
for lim, txt, c in ((1000, "1 Gy médula (aprox. TEDE)", "#000000"), (250, "EAB / LPZ: 250 mSv", "#c0392b"),
                    (50, "Evacuación: 50 mSv", "#8e44ad"), (10, "Confinamiento / planificación: 10 mSv", "#2471a3")):
    ax.axhline(lim, color=c, lw=1, alpha=.7); ax.text(395, lim * 1.08, txt, ha="right", va="bottom", fontsize=8, color=c)
ax.set_xlabel("Distancia al reactor (m)"); ax.set_ylabel("TEDE (mSv)")
ax.set_xlim(10, 400); ax.set_ylim(0.05, 2000)
ax.grid(True, which="both", alpha=.3); ax.legend(loc="lower left", fontsize=9)
fig.tight_layout(); fig.savefig("fig/dosis_distancia.png"); plt.close(fig)
print("ok")
