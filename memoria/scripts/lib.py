"""Helpers to edit a WordprocessingML body with lxml: tracked changes, fields, comments."""
import copy, re, sys
from lxml import etree

SK = "/root/.claude/skills/synced/e2f38660-d5fc-4f77-b7f6-d7c9d30f708e_549700b7-96db-4d4d-aae1-b07acf3b6bc4/docx/scripts"
sys.path.insert(0, SK)
from comment import add_comment  # noqa: E402

WNS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
MCNS = "http://schemas.openxmlformats.org/markup-compatibility/2006"
W = "{%s}" % WNS
XMLSPACE = "{http://www.w3.org/XML/1998/namespace}space"
AUTHOR = "Claude"
DATE = "2026-10-20T00:00:00Z"
_next_id = [90000]


def q(tag):
    return W + tag


def nid():
    _next_id[0] += 1
    return str(_next_id[0])


def el(tag, attrib=None, *children, text=None):
    e = etree.Element(q(tag))
    for k, v in (attrib or {}).items():
        e.set(q(k) if ":" not in k and not k.startswith("{") else k, v)
    for c in children:
        e.append(c)
    if text is not None:
        e.text = text
        if text != text.strip() or "  " in text:
            e.set(XMLSPACE, "preserve")
    return e


def in_fallback(e):
    for a in e.iterancestors():
        if a.tag == "{%s}Fallback" % MCNS:
            return True
    return False


def ptext(p):
    """Visible text of a paragraph (ignores deleted text and mc:Fallback duplicates)."""
    out = []
    for t in p.iter(q("t")):
        if not in_fallback(t):
            out.append(t.text or "")
    return "".join(out)


def track_attrs(e):
    e.set(q("id"), nid())
    e.set(q("author"), AUTHOR)
    e.set(q("date"), DATE)
    return e


# ---------------------------------------------------------------- runs ----
def _simple_run(r):
    """A run whose only content is rPr + one w:t (+ lastRenderedPageBreak)."""
    ts = [c for c in r if c.tag == q("t")]
    others = [c for c in r if c.tag not in (q("rPr"), q("t"), q("lastRenderedPageBreak"))]
    return len(ts) == 1 and not others


def _eligible_runs(p):
    res = []
    for r in p.iter(q("r")):
        par = r.getparent()
        if par.tag not in (q("p"), q("hyperlink"), q("ins")) or in_fallback(r):
            continue
        if par.tag == q("ins") and par.getparent().tag != q("p"):
            continue
        owner = next(a for a in r.iterancestors() if a.tag == q("p"))
        if owner is not p:
            continue
        res.append(r)
    return res


def _split_run(r, pos):
    """Split simple run r at text offset pos; returns (left, right)."""
    t = r.find(q("t"))
    txt = t.text or ""
    right = copy.deepcopy(r)
    for lr in right.findall(q("lastRenderedPageBreak")):
        right.remove(lr)
    t.text = txt[:pos]
    t.set(XMLSPACE, "preserve")
    rt = right.find(q("t"))
    rt.text = txt[pos:]
    rt.set(XMLSPACE, "preserve")
    r.addnext(right)
    return r, right


def _locate(p, old, occurrence=1):
    runs = _eligible_runs(p)
    segs, s = [], ""
    for r in runs:
        if _simple_run(r):
            txt = r.find(q("t")).text or ""
        else:
            txt = None
        segs.append((r, len(s), txt))
        s += txt if txt is not None else "\x00"
    idx = -1
    for _ in range(occurrence):
        idx = s.find(old, idx + 1)
        if idx < 0:
            return None
    return segs, idx


def _isolate(p, old, occurrence=1):
    """Split runs so that `old` is covered by whole runs; return that run list."""
    loc = _locate(p, old, occurrence)
    if loc is None:
        raise ValueError("text not found in paragraph: %r\n  in: %r" % (old, ptext(p)[:200]))
    segs, idx = loc
    end = idx + len(old)
    covered = []
    for r, start, txt in segs:
        if txt is None:
            if start < end and start + 1 > idx:
                raise ValueError("match spans a complex run: %r" % old)
            continue
        rs, re_ = start, start + len(txt)
        if re_ <= idx or rs >= end:
            continue
        cur = r
        if idx > rs:
            _, cur = _split_run(cur, idx - rs)
            rs = idx
        if end < re_:
            cur, _ = _split_run(cur, end - rs)
        covered.append(cur)
    return covered


def _mk_run(text, rpr=None):
    r = el("r")
    if rpr is not None:
        r.append(copy.deepcopy(rpr))
    r.append(el("t", text=text))
    return r


def _to_del(runs):
    d = track_attrs(el("del"))
    runs[0].addprevious(d)
    for r in runs:
        for lr in r.findall(q("lastRenderedPageBreak")):
            r.remove(lr)
        for t in r.findall(q("t")):
            t.tag = q("delText")
            t.set(XMLSPACE, "preserve")
        d.append(r)
    return d


def track_replace(p, old, new, occurrence=1):
    runs = _isolate(p, old, occurrence)
    rpr = runs[0].find(q("rPr"))
    d = _to_del(runs)
    if new:
        ins = track_attrs(el("ins"))
        ins.append(_mk_run(new, rpr))
        d.addnext(ins)
        return ins
    return None


def track_insert(p, anchor, new, before=False, occurrence=1, rpr_override=None):
    """Insert `new` (str or list of runs) right after (or before) `anchor`."""
    runs = _isolate(p, anchor, occurrence)
    ref = runs[0] if before else runs[-1]
    rpr = ref.find(q("rPr")) if rpr_override is None else rpr_override
    ins = track_attrs(el("ins"))
    if isinstance(new, str):
        ins.append(_mk_run(new, rpr))
    else:
        for r in new:
            ins.append(r)
    (ref.addprevious if before else ref.addnext)(ins)
    return ins


def track_append(p, new_runs):
    ins = track_attrs(el("ins"))
    for r in new_runs:
        ins.append(r)
    p.append(ins)
    return ins


def delete_paragraph(p):
    runs = [r for r in p if r.tag == q("r")]
    if runs:
        _to_del(runs)
    ppr = p.find(q("pPr"))
    if ppr is None:
        ppr = el("pPr")
        p.insert(0, ppr)
    rpr = ppr.find(q("rPr"))
    if rpr is None:
        rpr = el("rPr")
        sect = ppr.find(q("sectPr"))
        (sect.addprevious(rpr) if sect is not None else ppr.append(rpr))
    rpr.insert(0, track_attrs(el("del")))


# ------------------------------------------------------------ paragraphs --
def make_para(runs, style=None, unnumbered=False, ind=None, spacing=True, inserted=True,
              keep_next=False, jc=None, page_break_before=False, numpr=None):
    p = el("p")
    ppr = el("pPr")
    if style:
        ppr.append(el("pStyle", {"val": style}))
    if keep_next:
        ppr.append(el("keepNext"))
    if page_break_before:
        ppr.append(el("pageBreakBefore"))
    if unnumbered:
        ppr.append(el("numPr", None, el("ilvl", {"val": "0"}), el("numId", {"val": "0"})))
    elif numpr is not None:
        ppr.append(copy.deepcopy(numpr))
    if spacing and not style:
        ppr.append(el("spacing", {"line": "360", "lineRule": "auto"}))
    if ind:
        ppr.append(el("ind", ind))
    if jc:
        ppr.append(el("jc", {"val": jc}))
    if inserted:
        ppr.append(el("rPr", None, track_attrs(el("ins"))))
    p.append(ppr)
    if isinstance(runs, str):
        runs = [_mk_run(runs)]
    if inserted:
        ins = track_attrs(el("ins"))
        for r in runs:
            ins.append(r)
        p.append(ins)
    else:
        for r in runs:
            p.append(r)
    return p


def run(text, b=False, i=False, sz=None, color=None, sub=False):
    rpr = el("rPr")
    if b:
        rpr.append(el("b"))
        rpr.append(el("bCs"))
    if i:
        rpr.append(el("i"))
        rpr.append(el("iCs"))
    if color:
        rpr.append(el("color", {"val": color}))
    if sz:
        rpr.append(el("sz", {"val": str(sz)}))
        rpr.append(el("szCs", {"val": str(sz)}))
    if sub:
        rpr.append(el("vertAlign", {"val": "subscript"}))
    return _mk_run(text, rpr if len(rpr) else None)


def field_runs(instr, result, rpr=None):
    """Complex field as a list of runs (can live inside w:ins)."""
    def r_(*kids):
        r = el("r")
        if rpr is not None:
            r.append(copy.deepcopy(rpr))
        for k in kids:
            r.append(k)
        return r
    return [r_(el("fldChar", {"fldCharType": "begin"})),
            r_(el("instrText", text=" %s " % instr.strip())),
            r_(el("fldChar", {"fldCharType": "separate"})),
            r_(el("t", text=result)),
            r_(el("fldChar", {"fldCharType": "end"}))]


def set_style(p, style, unnumbered=False, record=True, drop_run_format=True):
    ppr = p.find(q("pPr"))
    if ppr is None:
        ppr = el("pPr")
        p.insert(0, ppr)
    old = copy.deepcopy(ppr)
    for tag in ("pStyle", "numPr", "ind", "spacing", "keepNext"):
        for e in ppr.findall(q(tag)):
            ppr.remove(e)
    if style:
        ppr.insert(0, el("pStyle", {"val": style}))
        if unnumbered:
            ppr.insert(1, el("numPr", None, el("ilvl", {"val": "0"}), el("numId", {"val": "0"})))
    if record:
        ch = track_attrs(el("pPrChange"))
        for e in old.findall(q("pPrChange")):
            old.remove(e)
        old.tag = q("pPr")
        for e in old.findall(q("rPr")) + old.findall(q("sectPr")):
            old.remove(e)
        ch.append(old)
        ppr.append(ch)
    if drop_run_format:
        for r in p.iter(q("r")):
            rpr = r.find(q("rPr"))
            if rpr is not None:
                for tag in ("b", "bCs", "i", "iCs", "sz", "szCs"):
                    for e in rpr.findall(q(tag)):
                        rpr.remove(e)


def add_spacing(p):
    ppr = p.find(q("pPr"))
    if ppr is None:
        ppr = el("pPr")
        p.insert(0, ppr)
    if ppr.find(q("spacing")) is None:
        st = ppr.find(q("pStyle"))
        sp = el("spacing", {"line": "360", "lineRule": "auto"})
        if st is not None:
            st.addnext(sp)
        else:
            ppr.insert(0, sp)


# --------------------------------------------------------------- comments --
class Commenter:
    def __init__(self, unpacked):
        self.dir = unpacked

    def on_paragraph(self, p, text, first=None, last=None):
        """Anchor a comment on a whole paragraph (or from first to last paragraph)."""
        cid, _, _ = add_comment(self.dir, text, author=AUTHOR, initials="C")
        first = first if first is not None else p
        last = last if last is not None else p
        start = el("commentRangeStart", {"id": str(cid)})
        ppr = first.find(q("pPr"))
        if ppr is not None:
            ppr.addnext(start)
        else:
            first.insert(0, start)
        last.append(el("commentRangeEnd", {"id": str(cid)}))
        ref = el("r", None, el("rPr", None, el("rStyle", {"val": "Refdecomentario"})),
                 el("commentReference", {"id": str(cid)}))
        last.append(ref)
        return cid

    def on_element(self, e, text):
        """Comment anchored to a table: use its first and last paragraphs."""
        ps = list(e.iter(q("p")))
        return self.on_paragraph(ps[0], text, ps[0], ps[-1])


# ------------------------------------------------------------------ math --
MNS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
M = "{%s}" % MNS


def _m(tag, *kids, **attrs):
    e = etree.Element(M + tag)
    for k, v in attrs.items():
        e.set(M + k, v)
    for c in kids:
        e.append(c)
    return e


def _mr(text, plain=False):
    r = _m("r")
    if plain:
        r.append(_m("rPr", _m("sty", val="p")))
    t = _m("t")
    t.text = text
    t.set(XMLSPACE, "preserve")
    r.append(t)
    return r


def _parse(expr):
    """'Σ_y^2 + x_{a b}' -> list of OMML elements (handles _x, _{..}, ^x, ^{..}; 'rm:' = upright)."""
    out, i, buf = [], 0, ""

    def flush():
        nonlocal buf
        if buf:
            out.append(_mr(buf))
            buf = ""

    def grab(j):
        if expr[j] == "{":
            k = expr.index("}", j)
            return expr[j + 1:k], k + 1
        return expr[j], j + 1
    while i < len(expr):
        ch = expr[i]
        if ch in "_^":
            base = buf[-1] if buf else ""
            buf = buf[:-1]
            flush()
            arg, i = grab(i + 1)
            if ch == "_" and i < len(expr) and expr[i] == "^":
                sup, i = grab(i + 1)
                out.append(_m("sSubSup", _m("e", _mr(base)), _m("sub", _mr(arg, plain=True)),
                              _m("sup", _mr(sup))))
            elif ch == "_":
                out.append(_m("sSub", _m("e", _mr(base)), _m("sub", _mr(arg, plain=True))))
            else:
                out.append(_m("sSup", _m("e", _mr(base)), _m("sup", _mr(arg))))
            continue
        buf += ch
        i += 1
    flush()
    return out


def _items(x):
    if isinstance(x, str):
        return _parse(x)
    if isinstance(x, list):
        res = []
        for y in x:
            res += _items(y)
        return res
    return [x]


def mF(num, den):
    return _m("f", _m("num", *_items(num)), _m("den", *_items(den)))


def mD(body, beg="(", end=")"):
    return _m("d", _m("dPr", _m("begChr", val=beg), _m("endChr", val=end)), _m("e", *_items(body)))


def mN(chr_, sub, sup, body):
    pr = _m("naryPr", _m("chr", val=chr_))
    if not sub:
        pr.append(_m("subHide", val="1"))
    if not sup:
        pr.append(_m("supHide", val="1"))
    return _m("nary", pr, _m("sub", *_items(sub or "")), _m("sup", *_items(sup or "")), _m("e", *_items(body)))


def mRad(body):
    return _m("rad", _m("radPr", _m("degHide", val="1")), _m("deg"), _m("e", *_items(body)))


def equation_para(parts, label=None, inserted=True):
    """Centered display equation; whole content tracked as an insertion."""
    p = el("p")
    ppr = el("pPr", None, el("spacing", {"before": "120", "after": "120"}), el("jc", {"val": "center"}))
    if inserted:
        ppr.append(el("rPr", None, track_attrs(el("ins"))))
    p.append(ppr)
    om = _m("oMath")
    holder = track_attrs(el("ins")) if inserted else om
    for x in _items(parts):
        holder.append(x)
    if inserted:
        om.append(holder)
    p.append(_m("oMathPara", om))
    if label:
        ins = track_attrs(el("ins")) if inserted else p
        ins.append(_mk_run("\t(%s)" % label))
        if inserted:
            p.append(ins)
    return p


def inline_math(parts):
    om = _m("oMath")
    for x in _items(parts):
        om.append(x)
    return om


def mSub(base, sub):
    return _m("sSub", _m("e", *_items(base)), _m("sub", *[_mr(sub, plain=True)]))
