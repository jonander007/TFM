# v10: on the author's TFM_JGL.docx (v9 with χ/Q written as X/Q). Uniform format of every data table,
# leftovers of the χ → X replacement (XX/Q, "(, en Bq/m³", TEDE/Q), equations and figures in X/Q, small fixes.
import re as _re, shutil as _sh
_V10 = HERE.parent / "v10"
_M = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"
_WP = "{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}"


def RRo(p, old, new):
    """Tracked replacement in a given paragraph object."""
    runs_ = _isolate(p, old)
    rpr = runs_[0].find(q("rPr"))
    d = _to_del(runs_)
    if new:
        ins = track_attrs(el("ins"))
        for r_ in runs_from(new, rpr):
            ins.append(r_)
        d.addnext(ins)


def visible(p):
    """Text of a paragraph without tracked deletions."""
    return "".join(t.text or "" for t in p.iter(q("t")) if not any(a.tag == q("del") for a in t.iterancestors()))


# ------------------------------------------------- leftovers of χ → X ----
_n_fix = 0
for p in paras():
    for old, new in (("XXX/Q", "X/Q"), ("XX/Q", "X/Q"), ("TEDE/X/Q", "TEDE/(X/Q)"), ("TEDE/Q (", "TEDE/(X/Q) ("),
                     ("contaminante (, en", "contaminante (X, en")):
        while old in visible(p) and old in ptext(p):
            try:
                RRo(p, old, new)
                _n_fix += 1
            except ValueError:
                break
print("X/Q fixes:", _n_fix)
# equations (OMML) still had χ: same notation as the text
_n_m = 0
for mt in body.iter(_M + "t"):
    if mt.text and "χ" in mt.text:
        mt.text = mt.text.replace("χ", "X"); _n_m += 1
print("equations:", _n_m)
# figures with χ/Q in the image: redrawn with X/Q (same size), alt text updated
for d in body.iter(_WP + "docPr"):
    if d.get("descr") and "χ" in d.get("descr"):
        d.set("descr", d.get("descr").replace("χ", "X"))
_rels = (UN / "word/_rels/document.xml.rels").read_text(encoding="utf-8")
for name, src in (("c13_xq_distancia.png", "xq_distancia.png"), ("c13_flujo_radio.png", "flujo_radio.png")):
    dp = next(d for d in body.iter(_WP + "docPr") if d.get("name") == name)
    rid = next(b.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed")
               for b in dp.getparent().iter("{http://schemas.openxmlformats.org/drawingml/2006/main}blip"))
    tgt = _re.search(r'Id="%s"[^>]*Target="([^"]+)"' % rid, _rels) or _re.search(r'Target="([^"]+)"[^>]*Id="%s"' % rid, _rels)
    _sh.copy(_V10 / "fig" / src, UN / "word" / tgt.group(1))

# ------------------------------------------------------- small fixes ----
RR("Lista de reactores recogidos en el catálogo de la IAEA", "de la IAEA", "del OIEA", nth=1)
RR("Lista de reactores recogidos en el catálogo de la IAEA", "de la IAEA", "del OIEA", nth=0)      # list of tables
for p in paras():                                   # SMART category labels in Anexo B: m3 -> m³
    for _m3 in ("100 m3", "300 m3"):
        while _m3 in visible(p) and _m3 in ptext(p):
            try:
                RRo(p, _m3, _m3.replace("m3", "m³"))
            except ValueError:
                break
# caption of Figura 15 lives in a text box (twice: DrawingML and its VML fallback)
for p in body.iter(q("p")):
    if "Ejemplo del input de ARCON96" in visible(p):
        if in_fallback(p):
            for t in p.iter(q("t")):
                if t.text and "input" in t.text:
                    t.text = t.text.replace("del input", "de fichero de entrada").replace("input", "fichero de entrada")
        else:
            try:
                RRo(p, "del input de ARCON96", "de fichero de entrada de ARCON96")
            except ValueError:
                pass

# ------------------------------------------- uniform format of tables ----
_NUM = _re.compile(r"^[\s≤≥<>~≈±+\-–−×]*(\d[\d.,·⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺eE+\-×/ ]*)(\s*(%|m|km|mSv|Sv|MW\S*|MWₜₕ|MWₑ|m³|ft³|kW|nudos|h|horas|d|días|a|Ci|s|min|°C|t|m/s|cfm|kg/h))?\s*$")
_CODE = _re.compile(r"^([A-G]|[CE]\d{1,2}|\d{2}|—|-|Sí|No)$")
_HDR_FILL = "1F3864"
_n_tbl = 0
_skipped = []


def _set(parent, tag, attrs, first=False):
    x = parent.find(q(tag))
    if x is None:
        x = el(tag)
        if first:
            parent.insert(0, x)
        else:
            parent.append(x)
    for k, v in attrs.items():
        x.set(q(k), v)
    return x


def _cell_text(tc):
    return "".join(t.text or "" for t in tc.iter(q("t"))).strip()


for tbl in list(body.iter(q("tbl"))):
    if in_fallback(tbl) or tbl.getparent().tag == q("tc"):
        continue
    rows = tbl.findall(q("tr"))
    if not rows:
        continue
    first = rows[0].find(q("tc"))
    shd = first.find(q("tcPr") + "/" + q("shd")) if first is not None else None
    if shd is None or (shd.get(q("fill")) or "").upper() != _HDR_FILL:
        _skipped.append(_cell_text(first)[:30] if first is not None else "?")
        continue                                  # bibliography and the .psf listing are not data tables
    _n_tbl += 1
    ncols = len(tbl.find(q("tblGrid")).findall(q("gridCol")))
    wide = ncols >= 9
    _sz = "16" if ncols >= 10 else "18"           # 8 pt only where 9 pt does not fit (Anexo E, 10–11 columns)
    # column alignment: centred if most body cells are numbers or short codes, else left
    colnum = {}
    for ci in range(ncols):
        vals = []
        for tr in rows[1:]:
            tcs = tr.findall(q("tc"))
            if ci < len(tcs):
                s = _cell_text(tcs[ci])
                if s:
                    vals.append(bool(_NUM.match(s) or _CODE.match(s)))
        colnum[ci] = bool(vals) and sum(vals) >= 0.6 * len(vals)
    # table properties
    tpr = tbl.find(q("tblPr"))
    _set(tpr, "jc", {"val": "center"})
    for x in tpr.findall(q("tblBorders")):
        tpr.remove(x)
    tpr.append(el("tblBorders", None, *[el(b, {"val": "single", "sz": "4", "space": "0", "color": "999999"})
                                        for b in ("top", "left", "bottom", "right", "insideH", "insideV")]))
    for ri, tr in enumerate(rows):
        hdr = ri == 0
        trpr = tr.find(q("trPr"))
        if trpr is None:
            trpr = el("trPr"); tr.insert(0, trpr)
        if hdr and trpr.find(q("tblHeader")) is None:
            trpr.append(el("tblHeader"))
        for ci, tc in enumerate(tr.findall(q("tc"))):
            tcpr = tc.find(q("tcPr"))
            if tcpr is None:
                tcpr = el("tcPr"); tc.insert(0, tcpr)
            for x in tcpr.findall(q("tcBorders")) + tcpr.findall(q("tcMar")) + tcpr.findall(q("vAlign")):
                tcpr.remove(x)
            lr = "45" if wide else "90"
            tcpr.append(el("tcMar", None, el("top", {"w": "60", "type": "dxa"}), el("left", {"w": lr, "type": "dxa"}),
                           el("bottom", {"w": "60", "type": "dxa"}), el("right", {"w": lr, "type": "dxa"})))
            tcpr.append(el("vAlign", {"val": "center"}))
            fill = tcpr.find(q("shd"))
            shaded = fill is not None and (fill.get(q("fill")) or "auto").upper() not in ("AUTO", "FFFFFF", _HDR_FILL)
            gs = tcpr.find(q("gridSpan"))
            jc = "left" if (gs is not None and int(gs.get(q("val"))) > 1) else ("center" if colnum.get(ci) else "left")
            for p in tc.findall(q("p")):
                ppr = p.find(q("pPr"))
                if ppr is None:
                    ppr = el("pPr"); p.insert(0, ppr)
                for x in ppr.findall(q("ind")) + ppr.findall(q("spacing")) + ppr.findall(q("jc")):
                    ppr.remove(x)
                ppr.append(el("spacing", {"before": "0", "after": "0", "line": "240", "lineRule": "auto"}))
                ppr.append(el("jc", {"val": jc}))
                rprs = [r.find(q("rPr")) for r in p.iter(q("r"))
                        if not any(a.tag.startswith(_M) for a in r.iterancestors())]
                mark = ppr.find(q("rPr"))
                for r in [r for r in p.iter(q("r")) if not any(a.tag.startswith(_M) for a in r.iterancestors())]:
                    rpr = r.find(q("rPr"))
                    if rpr is None:
                        rpr = el("rPr"); r.insert(0, rpr)
                    for x in rpr.findall(q("rFonts")):
                        if (x.get(q("ascii")) or "") not in ("Cambria Math", "Consolas"):
                            rpr.remove(x)
                    for x in rpr.findall(q("sz")) + rpr.findall(q("szCs")) + rpr.findall(q("color")):
                        rpr.remove(x)
                    if hdr:
                        if rpr.find(q("b")) is None:
                            rpr.insert(0, el("bCs")); rpr.insert(0, el("b"))
                    elif not shaded:
                        for x in rpr.findall(q("b")) + rpr.findall(q("bCs")):
                            rpr.remove(x)
                    rpr.append(el("color", {"val": "FFFFFF" if hdr else "000000"}))
                    rpr.append(el("sz", {"val": _sz})); rpr.append(el("szCs", {"val": _sz}))
                if mark is not None:
                    for x in mark.findall(q("sz")) + mark.findall(q("szCs")) + mark.findall(q("rFonts")):
                        mark.remove(x)
                    mark.append(el("sz", {"val": _sz})); mark.append(el("szCs", {"val": _sz}))
print("tables formatted:", _n_tbl, "skipped:", _skipped)

C.on_paragraph(P("Este trabajo propone y aplica una metodología para delimitar"),
               "Versión 10 (sobre TFM_JGL). Tablas: todas las de datos con el mismo formato (fuente del documento a "
               "9 pt —8 pt en las dos tablas de 10 y 11 columnas del Anexo E—, cabecera azul con texto blanco en negrita repetida en cada página, cuerpo negro sin negrita, "
               "interlineado sencillo, mismos márgenes y bordes, texto a la izquierda y valores numéricos centrados). "
               "Notación X/Q: corregidos los restos del reemplazo (XX/Q, «(, en Bq/m³», TEDE/Q) y pasadas a X/Q las "
               "ecuaciones y las Figuras 6 y 17. Además, IAEA → OIEA en la Tabla 25, «input» en la Figura 15 y m3 → "
               "m³ en el Anexo B.")

# ------------------------------------------- column widths and spacing after tables ----
def _widths(tbl, widths):
    grid = tbl.find(q("tblGrid"))
    for g, w in zip(grid.findall(q("gridCol")), widths):
        g.set(q("w"), str(w))
    for tr in tbl.findall(q("tr")):
        ci = 0
        for tc in tr.findall(q("tc")):
            gs = tc.find(q("tcPr") + "/" + q("gridSpan"))
            n = int(gs.get(q("val"))) if gs is not None else 1
            tcw = tc.find(q("tcPr") + "/" + q("tcW"))
            if tcw is not None:
                tcw.set(q("w"), str(sum(widths[ci:ci + n]))); tcw.set(q("type"), "dxa")
            ci += n


def _hdr(tbl):
    return [_cell_text(tc) for tc in tbl.find(q("tr")).findall(q("tc"))]


for tbl in body.iter(q("tbl")):
    h = _hdr(tbl)
    if "Status" in h and "Diseñadores" in h:          # Tabla 25: "En construcción" was split mid-word
        _widths(tbl, [1004, 1869, 1587, 1699, 1987, 1600, 1350, 1220, 1675])
    elif h[:2] == ["Etapa", "Herramienta"]:            # Tabla 11: "zonas_emergencia.py" was split
        _widths(tbl, [1350, 2100, 1750, 1550, 1950, 600])
    if h[:2] == ["Clase", "ΔT/ΔZ (°C/100 m)"]:          # Tabla 15: "Clase" split in a too narrow column
        _widths(tbl, [1000, 2400, 3400])
        tbl.find(q("tblPr")).find(q("tblW")).set(q("w"), "6800"); tbl.find(q("tblPr")).find(q("tblW")).set(q("type"), "dxa")
    if h[:2] in (["Clase", "ΔT/ΔZ (°C/100 m)"], ["Fecha", "Min"]):   # Tablas 15 and 16: blank line after
        nx = tbl.getnext()
        if nx is not None and ptext(nx).strip():
            tbl.addnext(make_para([], inserted=True))

# --------------------------------------------- schema order of the new properties ----
_ORD = {
    "tblPr": "tblStyle tblpPr tblOverlap bidiVisual tblStyleRowBandSize tblStyleColBandSize tblW jc tblCellSpacing "
             "tblInd tblBorders shd tblLayout tblCellMar tblLook tblCaption tblDescription tblPrChange",
    "tcPr": "cnfStyle tcW gridSpan hMerge vMerge tcBorders shd noWrap tcMar textDirection tcFitText vAlign hideMark "
            "headers cellIns cellDel cellMerge tcPrChange",
    "rPr": "ins del moveFrom moveTo rStyle rFonts b bCs i iCs caps smallCaps strike dstrike outline shadow emboss imprint "
           "noProof snapToGrid vanish webHidden color spacing w kern position sz szCs highlight u effect bdr shd "
           "fitText vertAlign rtl cs em lang eastAsianLayout specVanish oMath rPrChange",
}
for tag, order in _ORD.items():
    order = order.split()
    for e in body.iter(q(tag)):
        if tag == "rPr" and not any(a.tag == q("tbl") for a in e.iterancestors()):
            continue
        kids = list(e)
        kids.sort(key=lambda c: order.index(c.tag.split("}")[1]) if c.tag.split("}")[1] in order else 99)
        for c in kids:
            e.append(c)
