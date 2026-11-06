exec(open('datos.py').read().split("if __name__")[0])
import math
kair = 7.2*0.98/1426.65 / STD[330]['0-2'] * 1  # χ/Q factor at ~335 m
def rr(pts, lim):
    s, r = radio(pts, lim); return (s + "%.0f" % r) if s != '>' else "> 400"
cases = {
 "base": base,
 "F1": sens,
 "E2": [(v, y*1.0023) for v, y in base],
 "H3x2": [(v, y*2) for v, y in base],
 "H3x10": [(v, y*10) for v, y in base],
 "kairos": [(v, y*kair) for v, y in base],
}
print("factor χ/Q Kairos/base a 335 m:", round(kair,1))
for k, pts in cases.items():
    print(k, {L: rr(pts, L) for L in (1000, 250, 50, 10)})
# thyroid base: ratio 1.0126 -> YODO 100 mSv
thy=[(v,y*1453.04/1434.98) for v,y in base]; print("YODO base", rr(thy,100), "YODO F1", rr([(v,y*1453.04/1434.98) for v,y in sens],100))
print("dose 335 m base", 1418.1*(STD[330]['0-2']+STD[340]['0-2'])/2, "F1", KT*xqF(335))
for v in (10,20,30,50,70,100,150,200,300,400): print(v, f"{xqF(v):.2e}", f"{xqF(v)/STD[v]['0-2']:.2f}")
