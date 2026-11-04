"""Accept all tracked changes directly in the XML (no LibreOffice round trip).
usage: accept_xml.py SRC.docx DST.docx"""
import sys, zipfile
from lxml import etree

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
SRC, DST = sys.argv[1], sys.argv[2]
TRACK_PROPS = ("pPrChange", "rPrChange", "sectPrChange", "tblPrChange", "trPrChange", "tcPrChange",
               "tblGridChange", "numberingChange")


def mark(p, kind):
    ppr = p.find(W + "pPr")
    rpr = ppr.find(W + "rPr") if ppr is not None else None
    return rpr.find(W + kind) if rpr is not None else None


def accept(root):
    # property changes: keep the new properties
    for tag in TRACK_PROPS:
        for e in list(root.iter(W + tag)):
            e.getparent().remove(e)
    # deleted rows / tables
    for tr in list(root.iter(W + "tr")):
        trpr = tr.find(W + "trPr")
        if trpr is not None and trpr.find(W + "del") is not None:
            tbl = tr.getparent()
            tbl.remove(tr)
            if tbl.find(W + "tr") is None:
                tbl.getparent().remove(tbl)
        elif trpr is not None:
            for x in trpr.findall(W + "ins"):
                trpr.remove(x)
    # deleted paragraph marks: content joins the next paragraph (which keeps its own properties)
    for p in list(root.iter(W + "p")):
        if p.getparent() is None:
            continue
        if mark(p, "del") is not None:
            nxt = p.getnext()
            content = [c for c in p if c.tag != W + "pPr"]
            ppr = p.find(W + "pPr")
            if ppr is not None and ppr.find(W + "sectPr") is not None:
                ppr.find(W + "rPr").remove(mark(p, "del"))      # never drop a section break
                continue
            if nxt is not None and nxt.tag == W + "p":
                npp = nxt.find(W + "pPr")
                pos = 1 if npp is not None else 0
                for c in reversed(content):
                    nxt.insert(pos, c)
                p.getparent().remove(p)
            else:
                live = [t for t in p.iter(W + "t", W + "drawing", W + "instrText")
                        if not any(a.tag == W + "del" for a in t.iterancestors())]
                if not live and p.getparent().tag == W + "body":
                    p.getparent().remove(p)
                else:
                    ppr.find(W + "rPr").remove(mark(p, "del"))
    # deleted runs / inserted runs
    for d in list(root.iter(W + "del", W + "moveFrom")):
        par = d.getparent()
        if par is not None and par.tag != W + "rPr" and par.tag != W + "trPr":
            par.remove(d)
    for i in list(root.iter(W + "ins", W + "moveTo")):
        par = i.getparent()
        if par is None:
            continue
        if par.tag in (W + "rPr", W + "trPr"):
            par.remove(i)
            continue
        idx = par.index(i)
        for c in list(i):
            par.insert(idx, c)
            idx += 1
        par.remove(i)
    for e in list(root.iter(W + "rPr")):          # leftover paragraph-mark markers
        for x in e.findall(W + "del") + e.findall(W + "ins"):
            e.remove(x)
    for tag in ("moveFromRangeStart", "moveFromRangeEnd", "moveToRangeStart", "moveToRangeEnd"):
        for e in list(root.iter(W + tag)):
            e.getparent().remove(e)
    # paragraphs left with nothing but a deleted mark already handled; empty w:ins paragraphs
    # created for insertions stay as normal paragraphs


zin = zipfile.ZipFile(SRC)
zout = zipfile.ZipFile(DST, "w", zipfile.ZIP_DEFLATED)
for item in zin.infolist():
    data = zin.read(item.filename)
    if item.filename.startswith("word/") and item.filename.endswith(".xml") and (
            "document" in item.filename or "header" in item.filename or "footer" in item.filename
            or "footnotes" in item.filename or "endnotes" in item.filename):
        t = etree.fromstring(data)
        accept(t)
        data = etree.tostring(t, xml_declaration=True, encoding="UTF-8", standalone=True)
    zout.writestr(item, data)
zout.close()
