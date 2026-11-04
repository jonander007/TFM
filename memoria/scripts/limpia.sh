#!/bin/bash
# tracked docx -> clean docx (changes accepted, comments removed, schema order fixed)
set -e
SRC=$1; DST=$2; W=$(mktemp -d -p "$(dirname "$0")")
python3 "$(dirname "$0")/accept_xml.py" "$SRC" "$W/acc.docx"
mkdir "$W/u" && (cd "$W/u" && unzip -q ../acc.docx)
python3 - "$W/u" <<'PY'
import re, os, sys
from lxml import etree
u=sys.argv[1]; W="{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
p=f"{u}/word/document.xml"; d=open(p,encoding="utf-8").read()
d=re.sub(r"<w:commentRange(Start|End) [^>]*/>","",d)
d=re.sub(r"<w:r(?: [^>]*)?>(?:<w:rPr>(?:(?!</w:rPr>).)*</w:rPr>)?<w:commentReference [^>]*/></w:r>","",d)
d=re.sub(r"<w:commentReference [^>]*/>","",d); open(p,"w",encoding="utf-8").write(d)
for f in os.listdir(f"{u}/word"):
    if f.startswith("comments"): os.remove(f"{u}/word/{f}")
r=f"{u}/word/_rels/document.xml.rels"; s=open(r,encoding="utf-8").read()
open(r,"w",encoding="utf-8").write(re.sub(r'<Relationship [^>]*Target="comments[^"]*"[^>]*/>',"",s))
c=f"{u}/[Content_Types].xml"; s=open(c,encoding="utf-8").read()
s=re.sub(r'<Override [^>]*PartName="/word/comments[^"]*"[^>]*/>',"",s)
if 'Extension="wmf"' not in s: s=s.replace('<Default Extension="png"','<Default Extension="wmf" ContentType="image/x-wmf"/><Default Extension="png"')
open(c,"w",encoding="utf-8").write(s)
PPR=["pStyle","keepNext","keepLines","pageBreakBefore","framePr","widowControl","numPr","suppressLineNumbers","pBdr","shd","tabs","suppressAutoHyphens","kinsoku","wordWrap","overflowPunct","topLinePunct","autoSpaceDE","autoSpaceDN","bidi","adjustRightInd","snapToGrid","spacing","ind","contextualSpacing","mirrorIndents","suppressOverlap","jc","textDirection","textAlignment","textboxTightWrap","outlineLvl","divId","cnfStyle","rPr","sectPr","pPrChange"]
LVL=["start","numFmt","lvlRestart","pStyle","isLgl","suff","lvlText","lvlPicBulletId","legacy","lvlJc","pPr","rPr"]
def reorder(path, tag, order):
    t=etree.parse(path)
    for e in t.iter(W+tag):
        kids=list(e); key=lambda c: order.index(c.tag.replace(W,"")) if c.tag.replace(W,"") in order else len(order)
        s2=sorted(kids,key=key)
        if s2!=kids:
            for k in kids: e.remove(k)
            for k in s2: e.append(k)
    t.write(path,xml_declaration=True,encoding="UTF-8",standalone=True)
reorder(p,"pPr",PPR); reorder(f"{u}/word/numbering.xml","lvl",LVL)
sp=f"{u}/word/settings.xml"; t=etree.parse(sp); r=t.getroot()
if r.find(W+"updateFields") is None:
    e=etree.Element(W+"updateFields"); e.set(W+"val","true")
    tgt=next((x for x in r if x.tag.replace(W,"") in ("hdrShapeDefaults","footnotePr","endnotePr","compat","docVars","rsids") or x.tag.endswith("mathPr")),None)
    (tgt.addprevious(e) if tgt is not None else r.append(e))
t.write(sp,xml_declaration=True,encoding="UTF-8",standalone=True)
PY
(cd "$W/u" && rm -f "$DST" && zip -Xqr "$DST" .)
rm -rf "$W"
python3 /mnt/skills/public/docx/scripts/office/validate.py "$DST" | tail -1
