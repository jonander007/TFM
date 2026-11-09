"""Revisions on top of the author's v8 (memoria/TFM_v8.docx), with tracked changes and comments.

Each module in MODULES edits one chapter. Text may carry fields:
  @CITE:Tag|n@        citation field (CITATION Tag), cached result [n]
  @REF:Bookmark|txt@  cross-reference (REF Bookmark \\h), cached result txt
  @REFN:Bookmark|n@   paragraph-number reference (REF Bookmark \\r \\h), e.g. a chapter number
Outputs: memoria/TFM_v11_revisado.docx (tracked) and memoria/TFM_v11_limpia.docx (accepted, no comments).
"""
import copy, re, shutil, subprocess, sys
from pathlib import Path
from lxml import etree

HERE = Path(__file__).resolve().parent
LIBDIR = HERE.parent / "memoria"
sys.path.insert(0, str(LIBDIR))
from lib import (W, q, el, ptext, in_fallback, track_replace, track_insert, track_append, delete_paragraph,  # noqa
                 make_para, run, field_runs, track_attrs, Commenter, _isolate, _to_del, _mk_run)

SRC = Path("/home/user/TFM/memoria/TFM_JGL.docx")
OUT_REV = Path("/home/user/TFM/memoria/TFM_v11_revisado.docx")
OUT_CLEAN = Path("/home/user/TFM/memoria/TFM_v11_limpia.docx")
UN = HERE / "work_v11"
SK = "/mnt/skills/public/docx/scripts"
MODULES = ["v10.py", "v11.py"]

shutil.rmtree(UN, ignore_errors=True)
subprocess.run(["unzip", "-q", str(SRC), "-d", str(UN)], check=True)
subprocess.run([sys.executable, SK + "/merge_runs.py", str(UN)], check=True, capture_output=True)
tree = etree.parse(str(UN / "word/document.xml"))
body = tree.getroot().find(q("body"))
# lastRenderedPageBreak is only a layout cache; dropping it lets split w:t pieces merge
for lr in list(body.iter(q("lastRenderedPageBreak"))):
    lr.getparent().remove(lr)
for r in body.iter(q("r")):
    ts = r.findall(q("t"))
    if len(ts) > 1 and all(c.tag in (q("rPr"), q("t")) for c in r):
        ts[0].text = "".join(t.text or "" for t in ts)
        ts[0].set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        for t in ts[1:]:
            r.remove(t)
# merge_runs.py can put fldChar / instrText / text of a field in one run: give each its own run again
# (LibreOffice and some Word versions misread fields otherwise)
for r in list(body.iter(q("r"))):
    content = [c for c in r if c.tag != q("rPr")]
    if len(content) <= 1 or all(c.tag == q("t") for c in content):
        continue
    rpr = r.find(q("rPr"))
    pos = r.getparent().index(r)
    for k, c in enumerate(content[1:], 1):
        nr = el("r")
        if rpr is not None:
            nr.append(copy.deepcopy(rpr))
        nr.append(c)
        r.getparent().insert(pos + k, nr)
# consecutive w:t in one run that the split left apart (t, t) are joined by merging adjacent simple runs
def _same_fmt(a, b):
    ra, rb = a.find(q("rPr")), b.find(q("rPr"))
    return (etree.tostring(ra) if ra is not None else b"") == (etree.tostring(rb) if rb is not None else b"")
for par in list(body.iter(q("p"))):
    kids = list(par)
    for a, b_ in zip(kids, kids[1:]):
        if (a.tag == q("r") and b_.tag == q("r") and a.getparent() is par and b_.getparent() is par
                and [c.tag for c in a if c.tag != q("rPr")] == [q("t")]
                and [c.tag for c in b_ if c.tag != q("rPr")] == [q("t")] and _same_fmt(a, b_)):
            ta, tb = a.find(q("t")), b_.find(q("t"))
            tb.text = (ta.text or "") + (tb.text or "")
            tb.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
            par.remove(a)
C = Commenter(UN)
WARN = []


def in_txbx(p):
    return any(a.tag == q("txbxContent") for a in p.iterancestors())


def paras():
    return [p for p in body.iter(q("p")) if not in_fallback(p)]


def P(sub, nth=None, style=None):
    hits = [p for p in paras() if sub in ptext(p) and not in_txbx(p)
            and (style is None or (p.find(q("pPr") + "/" + q("pStyle")) is not None
                                   and p.find(q("pPr") + "/" + q("pStyle")).get(q("val")) == style))]
    if nth is not None:
        return hits[nth]
    if len(hits) != 1:
        raise SystemExit("P(%r) -> %d hits" % (sub, len(hits)))
    return hits[0]


def runs_from(text, rpr=None):
    """Runs for `text`, turning @CITE/@REF/@REFN markers into fields."""
    out = []
    for k, part in enumerate(re.split(r"(@(?:CITE|REF|REFN):[^@]+@)", text)):
        if not part:
            continue
        m = re.match(r"@(CITE|REF|REFN):([^|@]+)\|([^@]*)@", part)
        if not m:
            out.append(_mk_run(part, rpr))
            continue
        kind, tag, res = m.groups()
        if kind == "CITE":
            out += field_runs("CITATION %s \\l 3082" % tag, " [%s]" % res, rpr)
        elif kind == "REF":
            out += field_runs("REF %s \\h" % tag, res, rpr)
        else:
            out += field_runs("REF %s \\r \\h" % tag, res, rpr)
    return out


def RR(sub, old, new, nth=None):
    """Tracked replacement of `old` by `new` (which may contain fields) in the paragraph containing `sub`."""
    p = P(sub, nth)
    runs_ = _isolate(p, old)
    rpr = runs_[0].find(q("rPr"))
    d = _to_del(runs_)
    if new:
        ins = track_attrs(el("ins"))
        for r_ in runs_from(new, rpr):
            ins.append(r_)
        d.addnext(ins)
    return p


def new_para_like(model, text, lead=False):
    """Tracked new paragraph with the paragraph properties of `model` (style, list, spacing).
    Runs take the model's plain (non-bold) run format; with lead=True the text up to the first ':'
    is bold, as in the bulleted lists of the memoria."""
    p = copy.deepcopy(model)
    for a in list(p.attrib):
        if a.startswith("{http://schemas.microsoft.com/office/word/2010/wordml}"):
            del p.attrib[a]                      # w14:paraId / textId must be unique
    for x in list(p):
        if x.tag != q("pPr"):
            p.remove(x)
    ppr = p.find(q("pPr"))
    if ppr is None:
        ppr = el("pPr")
        p.insert(0, ppr)
    for x in ppr.findall(q("rPr")):
        ppr.remove(x)
    ppr.append(el("rPr", None, track_attrs(el("ins"))))
    rprs = [r.find(q("rPr")) for r in model.iter(q("r")) if r.find(q("t")) is not None]
    plain = next((r_ for r_ in rprs if r_ is None or r_.find(q("b")) is None), None)
    plain = copy.deepcopy(plain) if plain is not None else None
    ins = track_attrs(el("ins"))
    if lead and ":" in text:
        head, tail = text.split(":", 1)
        bold = copy.deepcopy(plain) if plain is not None else el("rPr")
        bold.insert(0, el("bCs"))
        bold.insert(0, el("b"))
        ins.append(_mk_run(head + ":", bold))
        text = tail
    for r_ in runs_from(text, plain):
        ins.append(r_)
    p.append(ins)
    return p


def delete_para(p):
    """Tracked deletion of a whole paragraph (runs and paragraph mark)."""
    for it in p.iter(q("instrText")):
        it.tag = q("delInstrText")
    delete_paragraph(p)


for mod in MODULES:
    exec(open(HERE / mod, encoding="utf-8").read())

# ------------------------------------------------------------------ save --
PPR_ORDER = ("pStyle keepNext keepLines pageBreakBefore framePr widowControl numPr suppressLineNumbers pBdr shd "
             "tabs suppressAutoHyphens kinsoku wordWrap overflowPunct topLinePunct autoSpaceDE autoSpaceDN bidi "
             "adjustRightInd snapToGrid spacing ind contextualSpacing mirrorIndents suppressOverlap jc textDirection "
             "textAlignment textboxTightWrap outlineLvl divId cnfStyle rPr sectPr pPrChange").split()
for ppr in body.iter(q("pPr")):
    kids = list(ppr)
    kids.sort(key=lambda c: PPR_ORDER.index(c.tag.replace(W, "")) if c.tag.replace(W, "") in PPR_ORDER else 99)
    for c in kids:
        ppr.append(c)
for rp in body.iter(q("rPr")):                      # paragraph-mark ins/del first
    if rp.getparent().tag == q("pPr"):
        for c in [c for c in rp if c.tag in (q("ins"), q("del"))][::-1]:
            rp.insert(0, c)
tree.write(str(UN / "word/document.xml"), xml_declaration=True, encoding="UTF-8", standalone=True)
st = (UN / "word/settings.xml").read_text(encoding="utf8")
if "w:updateFields" not in st:
    for anchor in ("w:hdrShapeDefaults", "w:footnotePr", "w:endnotePr", "w:compat", "w:docVars", "w:rsids"):
        if "<" + anchor in st:
            st = st.replace("<" + anchor, '<w:updateFields w:val="true"/><' + anchor, 1)
            break
    (UN / "word/settings.xml").write_text(st, encoding="utf8")
OUT_REV.unlink(missing_ok=True)
subprocess.run("cd %s && zip -Xqr %s ." % (UN, OUT_REV), shell=True, check=True)
v = subprocess.run([sys.executable, SK + "/office/validate.py", str(OUT_REV)], capture_output=True, text=True)
print(v.stdout.strip().splitlines()[-1] if v.stdout.strip() else v.stderr[-500:])
subprocess.run([str(HERE.parent / "limpia.sh"), str(OUT_REV), str(OUT_CLEAN)], check=True)
print("WARNINGS:", *WARN, sep="\n  - ")
