import openpyxl, math, json
from collections import Counter
U='/root/.claude/uploads/0cb8cd87-e1eb-574f-9a4c-14d35de5c2f8/'
H=[1,2,4,8,12,24,96,168,360,720]
wb=openpyxl.load_workbook(U+'fb2fb6fa-99_5th_PERCENTILE_XQ_VALUES_Sector_BY_HOUR.xlsx',data_only=True)
X={}
for h in H:
    rows=list(wb[f'H{h}h'].iter_rows(values_only=True)); hdr=rows[1]
    for r in rows[2:]:
        if r[0] is None: continue
        X.setdefault(r[0],{})[h]=dict(zip(hdr,r))
V=sorted(X)
secs=[k for k in X[V[0]][1] if str(k).startswith('X_')]
M={v:{h:X[v][h]['Maximun'] for h in H} for v in V}
def iv(v,t1,t2):
    return (t2*M[v][t2]-t1*M[v][t1])/(t2-t1)
STD={v:{'0-2':max(M[v][1],M[v][2]),'2-8':iv(v,2,8),'8-24':iv(v,8,24),'1-4d':iv(v,24,96),'4-30d':iv(v,96,720)} for v in V}
gov={h:sum(X[v][h]['Maximmum Sector']>X[v][h]['Maximmum Overall'] for v in V) for h in H}
worst1=Counter(max(secs,key=lambda s:X[v][1][s]) for v in V)
ratio_sec={h:(min(X[v][h]['Maximmum Sector']/X[v][h]['Maximmum Overall'] for v in V),max(X[v][h]['Maximmum Sector']/X[v][h]['Maximmum Overall'] for v in V)) for h in (1,2,8,12,720)}
# doses
ws=openpyxl.load_workbook(U+'a0b8f97f-Sets_Worst2h.xlsx',data_only=True)['Set01']
D={r[0]:(r[3],r[2]) for r in list(ws.iter_rows(values_only=True))[1:] if r[0]}
k=[D[v][0]/STD[v]['0-2'] for v in V]
# sensitivity estimate: ARCON96 formulas, class F, 1 m/s, centerline, no wake
c=(34,14.35,0.740,-0.35,62.6,0.180,-48.6)
def xqF(x,u=1.0):
    a,c1,d1,f1,c2,d2,f2=c; xk=x/1000
    sy=a*xk**0.894; sz=max((c1*xk**d1+f1) if xk<1 else (c2*xk**d2+f2),0.1)
    g=1-(1+x/1000)*math.exp(-x/1000)
    return 1/(math.pi*math.sqrt(sy**2+9.13e5*g)*math.sqrt(sz**2+6.67e2*g)*u)
KT=sum(k)/len(k)
def radio(pts,lim):
    pts=sorted(pts)
    ex=[i for i,(d,y) in enumerate(pts) if y>lim]
    if not ex: return ('≤',pts[0][0])
    i=ex[-1]
    if i==len(pts)-1: return ('>',pts[-1][0])
    (d1,y1),(d2,y2)=pts[i],pts[i+1]
    return ('',d1+(math.log(y1)-math.log(lim))/(math.log(y1)-math.log(y2))*(d2-d1))
base=[(v,D[v][0]) for v in V]
sens=[(v,KT*xqF(v)) for v in V]
out=dict(V=V,STD=STD,M=M,gov=gov,worst1=worst1.most_common(4),ratio_sec=ratio_sec,KT=(min(k),max(k),KT),
  D={v:D[v] for v in V}, sens={v:s for v,s in sens},
  radios_base={l:radio(base,l) for l in (250,50,10,1000)}, radios_sens={l:radio(sens,l) for l in (250,50,10,1000)},
  thy_base_ratio=1453.04/1434.98)
json.dump(out,open('datos.json','w'),indent=1,default=str)
if __name__=='__main__':
    print("gobierna sector (n/40):",gov); print("peor sector 1h:",worst1.most_common(4)); print("sector/overall",ratio_sec)
    print("TEDE/χQ",out['KT'])
    for v in (10,20,30,50,100,200,300,400): print(v, " ".join(f"{STD[v][k]:.2e}" for k in STD[v]), f"TEDE {D[v][0]:.3f}  sensF1 {KT*xqF(v):.3f} χ/Q F1 {xqF(v):.2e}")
    print("radios base",out['radios_base']); print("radios sens",out['radios_sens'])
    print("335 m: χ/Q base ~", STD[330]['0-2'], STD[340]['0-2'], " F1", xqF(335), " Kairos χ/Q implied", 7.2*0.98/1426.65)
