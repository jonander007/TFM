import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, FancyArrowPatch
plt.rcParams["font.family"] = "DejaVu Sans"
fig, ax = plt.subplots(figsize=(9.2, 8.6), dpi=220)
ax.set_xlim(0, 100); ax.set_ylim(0, 94); ax.axis("off")
LW = 2.6
def box(cx, cy, w, h, title, sub=None):
    ax.add_patch(Rectangle((cx - w/2, cy - h/2), w, h, fill=False, lw=LW, ec="black"))
    if sub:
        ax.text(cx, cy + h*0.14, title, ha="center", va="center", fontsize=11.5, fontweight="bold", linespacing=1.15)
        ax.text(cx, cy - h*0.30, sub, ha="center", va="center", fontsize=8.6, linespacing=1.1)
    else:
        ax.text(cx, cy, title, ha="center", va="center", fontsize=11.5, fontweight="bold", linespacing=1.15)
def arrow(p, q):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=13, lw=1.4, color="black", shrinkA=0, shrinkB=0))
def line(pts):
    xs, ys = zip(*pts); ax.plot(xs, ys, color="black", lw=1.4)
# column boxes
box(50, 87, 32, 9, "TÉRMINO FUENTE\nAL EXTERIOR", "(capítulo 9)")
box(50, 72, 32, 9.5, "CALCULAR χ/Q\nCON ARCON96", "(distancias y 16 sectores)")
box(50, 56, 32, 10.5, "EJECUTAR RADTRAD", "(término fuente fijo + χ/Q\nde cada distancia)")
box(50, 41, 32, 8, "OBTENER LA DOSIS\n(TEDE Y TIROIDES)")
box(12, 56, 20, 8, "REDUCIR\nDISTANCIA")
box(88, 56, 20, 8, "AUMENTAR\nDISTANCIA")
box(50, 5.5, 38, 8, "RADIO DE LA ZONA\n(EAB, LPZ Y MEDIDAS URGENTES)")
# diamond
dy, dx, cy = 9.5, 19, 24
ax.add_patch(Polygon([(50, cy + dy), (50 + dx, cy), (50, cy - dy), (50 - dx, cy)], closed=True, fill=False, lw=LW, ec="black"))
ax.text(50, cy, "¿IGUALA EL LÍMITE\nDE LA ZONA?", ha="center", va="center", fontsize=10.5, fontweight="bold", linespacing=1.15)
arrow((50, 82.5), (50, 76.75)); arrow((50, 67.25), (50, 61.25)); arrow((50, 50.75), (50, 45)); arrow((50, 37), (50, cy + dy))
arrow((50, cy - dy), (50, 9.5)); ax.text(52, (cy - dy + 9.5) / 2, "SÍ", fontsize=11, fontweight="bold", va="center")
# loops
line([(50 - dx, cy), (12, cy)]); arrow((12, cy), (12, 52))
line([(50 + dx, cy), (88, cy)]); arrow((88, cy), (88, 52))
arrow((22, 56), (34, 56)); arrow((78, 56), (66, 56))
ax.text(14, 33.5, "LA DOSIS ESTÁ POR\nDEBAJO DEL LÍMITE", ha="left", va="center", fontsize=9.5, fontweight="bold")
ax.text(86, 33.5, "LA DOSIS SUPERA\nEL LÍMITE", ha="right", va="center", fontsize=9.5, fontweight="bold")
fig.tight_layout(pad=0.3); fig.savefig("fig/flujo_radio.png", facecolor="white")
