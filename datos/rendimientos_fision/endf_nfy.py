"""Minimal reader of ENDF-6 fission product yields (MF8, MT454 independent / MT459 cumulative).

yields(path, mat, mt) -> {incident energy (eV): {(ZA, isomeric state): (yield, uncertainty)}}
"""
import re, sys
def fnum(s):
    s=s.strip()
    if not s: return 0.0
    m=re.match(r'([+-]?[\d.]+)([+-]\d+)$', s)
    return float(m.group(1)+'e'+m.group(2)) if m else float(s)
def records(path, mat, mt):
    vals=[]
    for ln in open(path):
        if len(ln)<75: continue
        if int(ln[66:70] or 0)==mat and int(ln[70:72] or 0)==8 and int(ln[72:75] or 0)==mt:
            vals.append([fnum(ln[i:i+11]) for i in range(0,66,11)])
    return vals
def yields(path, mat, mt):
    rows=records(path,mat,mt)
    flat=[v for r in rows[1:] for v in r]   # skip HEAD
    out={}; i=0
    while i+6<=len(flat):
        E,_,_,_,NN,NFP=flat[i:i+6]; NN=int(NN); i+=6
        data=flat[i:i+NN]; i+= NN + ((-NN)%6)
        out[E]={(int(data[k]),int(data[k+1])):(data[k+2],data[k+3]) for k in range(0,NN,4)}
        if not NN: break
    return out
if __name__=="__main__":
    y=yields(sys.argv[1],9228,459)
    print("energies (eV):", list(y))
    th=y[min(y)]
    want={53131:"I-131",53132:"I-132",53133:"I-133",53134:"I-134",53135:"I-135",36085:"Kr-85m",36087:"Kr-87",36088:"Kr-88",54133:"Xe-133",54135:"Xe-135",54138:"Xe-138",52132:"Te-132",36083:"Kr-83m",54131:"Xe-131m"}
    for (za,s),(v,dv) in sorted(th.items()):
        if za in want: print(want[za], "iso", s, f"{v:.5e} ± {dv:.2e}")
