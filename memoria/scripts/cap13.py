# Results (chapter 13), conclusions (14), updates of chapters 3, 7 and 12, abstract, and annexes D–F
# (RADTRAD input files, design χ/Q, user manual). Data: run of 5-6 Nov 2026 (10–400 m every 10 m,
# 5 MET years, 1 iodine fraction set, E1 and E2).
import math as _m, re as _re, shutil as _sh, json as _js
from xml.sax.saxutils import escape as _xesc
import openpyxl as _ox

_U = Path("/root/.claude/uploads/0cb8cd87-e1eb-574f-9a4c-14d35de5c2f8")
_HT = Path("/home/user/TFM/herramienta")
_FIG = HERE.parent / "res" / "fig"
_XQ_XLSX = _U / "fb2fb6fa-99_5th_PERCENTILE_XQ_VALUES_Sector_BY_HOUR.xlsx"
_DOSE_XLSX = _U / "a0b8f97f-Sets_Worst2h.xlsx"
_W14 = "{http://schemas.microsoft.com/office/word/2010/wordml}"


def _f(x, d=1):                       # Spanish decimal comma
    return ("%.*f" % (d, x)).replace(".", ",")


def _e(x, d=2):                       # 7,02·10⁻²
    s = "%.*e" % (d, x)
    mant, ex = s.split("e")
    sup = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")
    return mant.replace(".", ",") + "·10" + str(int(ex)).translate(sup)


# ------------------------------------------------------------------ data --
_H = [1, 2, 4, 8, 12, 24, 96, 168, 360, 720]
_wb = _ox.load_workbook(_XQ_XLSX, data_only=True)
_X = {}
for _h in _H:
    _rows = list(_wb["H%dh" % _h].iter_rows(values_only=True))
    _hdr = _rows[1]
    for _r in _rows[2:]:
        if _r[0] is not None:
            _X.setdefault(int(_r[0]), {})[_h] = dict(zip(_hdr, _r))
_V = sorted(_X)
_M = {v: {h: _X[v][h]["Maximun"] for h in _H} for v in _V}


def _iv(v, t1, t2):
    return (t2 * _M[v][t2] - t1 * _M[v][t1]) / (t2 - t1)


_STD = {v: [max(_M[v][1], _M[v][2]), _iv(v, 2, 8), _iv(v, 8, 24), _iv(v, 24, 96), _iv(v, 96, 720)] for v in _V}
_ws = _ox.load_workbook(_DOSE_XLSX, data_only=True)["Set01"]
_D = {int(r[0]): r[3] for r in list(_ws.iter_rows(values_only=True))[1:] if r[0]}
# interval table written in the .psf (PIPELINE.interval_xq)
import sys as _sys
_sys.path.insert(0, str(_HT))
import logging as _lg
_lg.disable(_lg.CRITICAL)
from PIPELINE import interval_xq as _ivxq
_lg.disable(_lg.NOTSET)
_PSF = {v: _ivxq(_H, [_M[v][h] for h in _H], "") for v in _V}

# ------------------------------------------------------------ models -----
_m_body = P("Este capítulo presenta los resultados de la cadena de cálculo")
_m_bul = P("El análisis considera el buque atracado y no las fases de aproximación")
_m_h2 = P("Coeficientes de dispersión atmosférica", style="Ttulo2")
_m_anx = P("Anexo C: Actividad de los radionucleidos tras cada barrera", style="Ttulo2")
_cap_m = [p for p in paras() if ptext(p).startswith("Tabla") and "Primer criterio de exclusión" in ptext(p)
          and p.find(q("pPr") + "/" + q("pStyle")) is not None
          and p.find(q("pPr") + "/" + q("pStyle")).get(q("val")) == "Descripcin"][0]
_tbl_m = _cap_m.getnext()
assert _tbl_m.tag == q("tbl")
_bm_id = [880000]
_pic_id = [94000]
_rid = [0]


def _strip14(e):
    for x in e.iter():
        for a in list(x.attrib):
            if a.startswith(_W14):
                del x.attrib[a]
    return e


def T(text, model=None):
    return new_para_like(model if model is not None else _m_body, text)


def B(text):
    return new_para_like(_m_bul, text, lead=True)


def HEAD(text, model=None):
    return new_para_like(model if model is not None else _m_h2, text)


def SUB(text):
    """Bold run-in subheading paragraph (inside annexes, where Título 3 would be numbered)."""
    p = new_para_like(_m_body, text)
    for r in p.iter(q("r")):
        rpr = r.find(q("rPr"))
        if rpr is None:
            rpr = el("rPr"); r.insert(0, rpr)
        rpr.insert(0, el("b"))
    ppr = p.find(q("pPr"))
    ppr.insert(0, el("keepNext"))
    return p


def CAP(kind, text, bm):
    """Caption like the existing ones (style Descripcin, centred, SEQ field, bookmark on 'Tabla N')."""
    p = el("p")
    p.append(el("pPr", None, el("pStyle", {"val": "Descripcin"}), el("keepNext"), el("jc", {"val": "center"}),
                el("rPr", None, track_attrs(el("ins")))))
    _bm_id[0] += 1
    bid = str(_bm_id[0])
    p.append(el("bookmarkStart", {"id": bid, "name": bm}))
    ins = track_attrs(el("ins"))
    ins.append(_mk_run(kind + " "))
    for r_ in field_runs(" SEQ %s \\* ARABIC " % kind, "0"):
        ins.append(r_)
    p.append(ins)
    p.append(el("bookmarkEnd", {"id": bid}))
    ins2 = track_attrs(el("ins"))
    for r_ in runs_from(": " + text):
        ins2.append(r_)
    p.append(ins2)
    return p


def TABLE(header, rows, widths, sz=18, jc_cols=None):
    """Table with the format of the existing ones (dark blue header, 9 pt, grey borders), tracked."""
    tbl = copy.deepcopy(_tbl_m)
    _strip14(tbl)
    for x in list(tbl):
        if x.tag in (q("tr"), q("tblGrid")):
            tbl.remove(x)
    tbl.find(q("tblPr")).find(q("tblW")).set(q("w"), str(sum(widths)))
    tbl.insert(1, el("tblGrid", None, *[el("gridCol", {"w": str(w)}) for w in widths]))
    mrows = _tbl_m.findall(q("tr"))
    for ri, row in enumerate([header] + rows):
        tr = copy.deepcopy(mrows[0 if ri == 0 else 1])
        _strip14(tr)
        tmpl = tr.findall(q("tc"))[0]
        for tc in tr.findall(q("tc")):
            tr.remove(tc)
        trpr = tr.find(q("trPr"))
        trpr.append(track_attrs(el("ins")))
        for ci, (txt, w) in enumerate(zip(row, widths)):
            tc = copy.deepcopy(tmpl)
            tc.find(q("tcPr")).find(q("tcW")).set(q("w"), str(w))
            p = tc.find(q("p"))
            rpr = copy.deepcopy(p.find(q("r")).find(q("rPr")))
            for s_ in rpr.findall(q("sz")) + rpr.findall(q("szCs")):
                s_.set(q("val"), str(sz))
            for x in list(p):
                if x.tag != q("pPr"):
                    p.remove(x)
            ppr = p.find(q("pPr"))
            # keep short tables on one page (as the existing ones): every row but the last keeps with the next
            if (len(rows) > 25 and ri > 0) or ri == len(rows):
                for k in ppr.findall(q("keepNext")):
                    ppr.remove(k)
            if jc_cols and ci in jc_cols:
                ppr.find(q("jc")).set(q("val"), jc_cols[ci])
            prp = ppr.find(q("rPr"))
            if prp is None:
                prp = el("rPr"); ppr.append(prp)
            prp.append(track_attrs(el("ins")))
            ins = track_attrs(el("ins"))
            for r_ in runs_from(str(txt), rpr):
                ins.append(r_)
            p.append(ins)
            tr.append(tc)
        tbl.append(tr)
    return tbl


def _add_rel(rid, typ, target):
    p_ = UN / "word/_rels/document.xml.rels"
    t_ = p_.read_text(encoding="utf8")
    if 'Id="%s"' % rid not in t_:
        t_ = t_.replace("</Relationships>", '<Relationship Id="%s" Type="http://schemas.openxmlformats.org/'
                        'officeDocument/2006/relationships/%s" Target="%s"/></Relationships>' % (rid, typ, target))
        p_.write_text(t_, encoding="utf8")


def FIG(src, width_cm, descr):
    from PIL import Image as _Im
    wpx, hpx = _Im.open(src).size
    _rid[0] += 1
    rid = "rIdC13F%d" % _rid[0]
    name = "c13_%s" % Path(src).name
    _sh.copy(src, UN / "word/media" / name)
    _add_rel(rid, "image", "media/" + name)
    _pic_id[0] += 1
    cx = int(width_cm * 360000)
    cy = cx * hpx // wpx
    r_ = etree.fromstring(
        '<w:r xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
        'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
        'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
        'xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<w:rPr><w:noProof/></w:rPr>'
        '<w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="%d" cy="%d"/>'
        '<wp:docPr id="%d" name="%s" descr="%s"/>'
        '<wp:cNvGraphicFramePr><a:graphicFrameLocks noChangeAspect="1"/></wp:cNvGraphicFramePr>'
        '<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:pic>'
        '<pic:nvPicPr><pic:cNvPr id="%d" name="%s"/><pic:cNvPicPr/></pic:nvPicPr>'
        '<pic:blipFill><a:blip r:embed="%s"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
        '<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="%d" cy="%d"/></a:xfrm>'
        '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic></a:graphicData></a:graphic>'
        '</wp:inline></w:drawing></w:r>' % (cx, cy, _pic_id[0], name, _xesc(descr, {'"': "&quot;"}),
                                             _pic_id[0], name, rid, cx, cy))
    return make_para([r_], jc="center", keep_next=True, spacing=False)


def LISTING(lines, sz=14):
    """Monospaced listing, one paragraph per line, single spacing."""
    out = []
    for i, ln in enumerate(lines):
        p = el("p")
        ppr = el("pPr", None, el("spacing", {"before": "0", "after": "0", "line": "240", "lineRule": "auto"}),
                 el("ind", {"left": "284"}), el("rPr", None, track_attrs(el("ins"))))
        if i < len(lines) - 1:
            ppr.insert(0, el("keepLines"))
        p.append(ppr)
        rpr = el("rPr", None, el("rFonts", {"ascii": "Consolas", "hAnsi": "Consolas", "cs": "Consolas"}),
                 el("noProof"), el("sz", {"val": str(sz)}), el("szCs", {"val": str(sz)}))
        ins = track_attrs(el("ins"))
        r_ = el("r", None, rpr, el("t", {"{http://www.w3.org/XML/1998/namespace}space": "preserve"},
                                    text=ln.rstrip("\r\n") or " "))
        ins.append(r_)
        p.append(ins)
        out.append(p)
    return out


def LISTCOLS(lines, per_col=72, sz=13):
    """Listing in two columns: borderless table, each row holding two blocks of `per_col` lines."""
    tbl = el("tbl", None,
             el("tblPr", None, el("tblW", {"w": "9600", "type": "dxa"}), el("jc", {"val": "center"}),
                el("tblBorders", None, *[el(b, {"val": "nil"}) for b in ("top", "left", "bottom", "right",
                                                                           "insideH", "insideV")]),
                el("tblLayout", {"type": "fixed"})),
             el("tblGrid", None, el("gridCol", {"w": "4800"}), el("gridCol", {"w": "4800"})))
    blocks = [lines[i:i + per_col] for i in range(0, len(lines), per_col)]
    for k in range(0, len(blocks), 2):
        tr = el("tr", None, el("trPr", None, el("cantSplit"), track_attrs(el("ins"))))
        for blk in blocks[k:k + 2] + ([[]] if len(blocks[k:k + 2]) == 1 else []):
            tc = el("tc", None, el("tcPr", None, el("tcW", {"w": "4800", "type": "dxa"})))
            ps = LISTING(blk, sz) if blk else [make_para([], inserted=True)]
            for p_ in ps:
                ind = p_.find(q("pPr")).find(q("ind"))
                if ind is not None:
                    ind.set(q("left"), "0")
                tc.append(p_)
            tr.append(tc)
        tbl.append(tr)
    return tbl


def EMPTY():
    return make_para([], inserted=True)


def after(anchor, items):
    for it in items:
        anchor.addnext(it)
        anchor = it
    return anchor


def replace_placeholder(sub, first_text, more=()):
    """Tracked deletion of a '[Pendiente: …]' paragraph (it may hold fields) and new paragraphs after it."""
    p = P(sub)
    last = after(p, [T(first_text)] + list(more))
    for sc in p.iter(q("sdtContent")):          # citations live in content controls
        rs = [r for r in sc if r.tag == q("r")]
        if rs:
            _to_del(rs)
    delete_paragraph(p) if False else delete_para(p)
    return last


def REF(bm, txt):
    return "@REF:%s|%s@" % (bm, txt)


# ===================================================== chapter 3 updates ==
RR("Como análisis de sensibilidad, se recomienda repetir el cálculo de dosis", "se recomienda repetir", "se repite")
RR("Así se tiene un punto de comparación directo", "Así se tiene un punto", "Sus resultados se recogen en el capítulo "
   "@REFN:_RefCap_res|13@. Así se tiene un punto")
RR("Resultado E2 (7 d, 50 mSv)", "Resultado E2 (7 d, 50 mSv)", "15 m (22 m con clase F y 1 m/s)")
RR("Resultado E1+E2 (96 h, 10 mSv)", "Resultado E1+E2 (96 h, 10 mSv)", "34 m (48 m con clase F y 1 m/s)")
RR("La normativa española sitúa un reactor embarcado de más de 100 MW", "no son representativas de un reactor de esta potencia",
   "no proceden de una caracterización radiológica del reactor")

# ===================================================== chapter 7 updates ==
RR("Para un receptor situado a una distancia d del buque", "distancia d del buque", "distancia d del reactor")
p_tab11 = P("resume la cadena, con la herramienta empleada en cada etapa")
after(p_tab11, [T("La cadena se aplica a los dos escenarios del accidente postulado (E1, con el edificio del reactor "
                  "acreditado, y E2, sin él; capítulo @REFN:_RefCap_acc|8@) y a un caso de sensibilidad con "
                  "meteorología constante de clase F y 1 m/s (capítulo @REFN:_RefCap_disp|10@). La herramienta del "
                  "capítulo @REFN:_RefCap_herr|12@ la ejecuta para un barrido de distancias, los 16 sectores de "
                  "dirección y varios juegos de fracciones químicas del yodo, y entrega los radios de las zonas y su "
                  "representación sobre el mapa del puerto. Los ficheros de entrada de RADTRAD se recogen en el "
                  "Anexo D, los χ/Q de diseño en el Anexo E y el manual de uso de la herramienta en el Anexo F.")])
p_val = P("Rango de validez. Los algoritmos de ARCON96 se basan en medidas de campo")
def BL(model, head, tail):
    """Bullet like model with a bold lead ending in a full stop ('Emisión y receptor a nivel del suelo. ')."""
    p = new_para_like(model, tail)
    ins = p.find(q("ins"))
    first = ins.find(q("r"))
    rpr = copy.deepcopy(first.find(q("rPr"))) if first.find(q("rPr")) is not None else el("rPr")
    rpr.insert(0, el("bCs")); rpr.insert(0, el("b"))
    ins.insert(0, _mk_run(head, rpr))
    return p


after(p_val, [
    BL(p_val, "Punto de emisión. ", "Las distancias se miden desde el reactor, situado a popa en la zona de máquinas del "
       "buque de referencia (capítulo @REFN:_RefCap_buque|6@), y no desde el centro del buque."),
    BL(p_val, "Término fuente. ", "Inventario de equilibrio a 320 MWₜₕ, liberación de todo el término fuente al "
       "exterior en las dos primeras horas y sin desintegración durante el transporte (capítulo "
       "@REFN:_RefCap_acc|8@)."),
])

# ===================================================== chapter 12 updates =
replace_placeholder("[Pendiente: figura con el mapa de zonas generado",
   "La " + REF("_RefFig_guimapa", "Figura 18") + " muestra la pestaña «Mapa de zonas» con los resultados de la "
   "ejecución del capítulo @REFN:_RefCap_res|13@ sobre la imagen de satélite del puerto exterior. El Anexo F recoge "
   "el manual de uso de la herramienta.",
   [FIG(_FIG / "gui_mapa_satelite.png", 16.0,
        "Pestaña Mapa de zonas de la herramienta: tabla de radios de las zonas de la Tabla 4, datos del buque y "
        "mapa de satélite del puerto exterior de Bilbao con el buque a escala, el reactor y las zonas."),
    CAP("Figura", "Pestaña «Mapa de zonas» de la herramienta con los resultados sobre la imagen de satélite del "
                  "puerto exterior de Bilbao", "_RefFig_guimapa")])

# ===================================================== abstract ==========
RR("[Pendiente: una o dos frases con los radios obtenidos", "[Pendiente: una o dos frases con los radios obtenidos y la "
   "conclusión principal.]",
   "La dosis la domina la inhalación del tritio, el 99 % de la TEDE, y los radios son de pocas decenas de metros en torno "
   "al reactor: el criterio de 250 mSv del EAB y la LPZ se cumple ya a 10 m, la zona de evacuación (50 mSv en 7 días) "
   "alcanza 15 m y las de confinamiento y de planificación (10 mSv), 34 m; con clase de estabilidad F y viento de "
   "1 m/s se estiman 22 y 48 m. Las zonas quedan dentro del ámbito del atraque y muy por debajo de las distancias "
   "genéricas de la Directriz básica (100 y 200 m), que resultan conservadoras para este diseño.")
RR("[Pending: one or two sentences", "[Pending: one or two sentences with the radii obtained and the main conclusion.]",
   "The dose is dominated by tritium inhalation, 99 % of the TEDE, and the radii are a few tens of metres around the "
   "reactor: the 250 mSv EAB and LPZ criterion is already met at 10 m, the evacuation zone (50 mSv in 7 days) reaches "
   "15 m and the sheltering and planning zones (10 mSv) 34 m; with stability class F and a 1 m/s wind, 22 m and 48 m "
   "are estimated. The zones remain within the berth area and well below the generic distances of the Spanish "
   "radiological emergency guideline (100 m and 200 m), which are therefore conservative for this design.")
RR("[Zain: lortutako erradioak", "[Zain: lortutako erradioak eta ondorio nagusia esaldi batean edo bitan.]",
   "Dosia tritioaren arnasketak menderatzen du, TEDEaren % 99, eta erradioak erreaktorearen inguruko hamarnaka metro "
   "gutxikoak dira: EAB eta LPZko 250 mSv-eko irizpidea 10 m-tan betetzen da jada, ebakuazio-eremua (50 mSv 7 "
   "egunetan) 15 m-raino iristen da, eta konfinamendu- eta plangintza-eremuak (10 mSv) 34 m-raino; F egonkortasun-"
   "klasearekin eta 1 m/s-ko haizearekin, 22 eta 48 m kalkulatzen dira. Eremuak atrakalekuaren barruan geratzen dira, "
   "Oinarrizko Zuzentarauaren distantzia generikoen (100 eta 200 m) azpitik; horiek, beraz, kontserbadoreak dira "
   "diseinu honetarako.")

# ===================================================== chapter 13 ========
after(_m_body, [T("Los resultados corresponden a una ejecución con 40 distancias, de 10 a 400 m cada 10 m, los cinco "
                 "años de meteorología adaptada, los escenarios E1 y E2 y un juego de fracciones químicas del yodo "
                 "(aerosol 0,756; elemental 0,090; orgánico 0,154). Los ficheros de entrada se recogen en el Anexo D y "
                 "los χ/Q de diseño de todas las distancias en el Anexo E.")])

# 13.1 χ/Q
_sel = [10, 20, 30, 50, 70, 100, 150, 200, 300, 400]
_t_xq = TABLE(("Distancia (m)", "0–2 h", "2–8 h", "8–24 h", "1–4 días", "4–30 días"),
              [(str(v),) + tuple(_e(x) for x in _STD[v]) for v in _sel],
              [1600, 1600, 1600, 1600, 1600, 1600], jc_cols={i: "center" for i in range(6)})
replace_placeholder(
    "[Pendiente: χ/Q de diseño frente a la distancia",
    "La " + REF("_RefFig_xq", "Figura 19") + " muestra el χ/Q de diseño frente a la distancia al reactor para los "
    "intervalos de la RG 1.145 @CITE:USN82|40@, y la " + REF("_RefTab_xqres", "Tabla 29") + " recoge sus valores en "
    "distancias seleccionadas. En los intervalos de 1 y 2 horas el valor de diseño lo fija el percentil 99,5 del peor "
    "sector, que supera al percentil 95 global en un 3–9 %; en 4 horas lo fija el sector en 11 de las 40 distancias, y "
    "a partir de 8 horas, siempre el percentil 95 global. El sector más desfavorable es el mismo en todas las "
    "distancias: el de los receptores situados al sureste del reactor, con viento del noroeste.",
    [T("El χ/Q decrece con la distancia aproximadamente como d⁻¹·⁹, desde " + _e(_STD[10][0]) + " s/m³ a 10 m hasta "
       + _e(_STD[400][0]) + " s/m³ a 400 m en el intervalo de 0–2 h. Entre ese intervalo y el de 4–30 días baja a algo "
       "más de la tercera parte. Como comprobación independiente, el valor de 0–2 h coincide, entre 50 y 400 m y "
       "dentro de un 10 %, con el χ/Q en el eje de la pluma que dan las expresiones de ARCON96 para clase F y viento "
       "de 2 m/s: el percentil de diseño corresponde a las horas estables con viento flojo de la serie, que, al estar "
       "escalada la velocidad del viento, casi no tiene horas por debajo de 2 m/s."),
     FIG(_FIG / "xq_distancia.png", 15.0, "Gráfico logarítmico del χ/Q de diseño frente a la distancia al reactor, de "
         "10 a 400 m, para los intervalos de 0–2 h, 2–8 h, 8–24 h, 1–4 días y 4–30 días; todas las curvas decrecen "
         "como d elevado a −1,9."),
     CAP("Figura", "χ/Q de diseño frente a la distancia al reactor", "_RefFig_xq"),
     CAP("Tabla", "χ/Q de diseño (s/m³) en distancias seleccionadas", "_RefTab_xqres"),
     _t_xq, EMPTY()])

# 13.2 doses
_t_cont = TABLE(("Contribución", "Nucleidos principales", "TEDE/χQ (mSv·m³/s)", "Fracción"),
                [("Inhalación de tritio", "H-3", "1426,7", "99,4 %"),
                 ("Inmersión en la nube", "Xe-133, Kr-88, Kr-87, Kr-85m, Xe-135", "5,1", "0,36 %"),
                 ("Inhalación del resto", "Yodos, Ba-140, Sr-89, Te-132", "3,2", "0,22 %"),
                 ("Total (cálculo manual)", "", "1435,0", "100 %"),
                 ("Total (RADTRAD)", "", "1418,1", "98,8 %")],
                [2600, 3500, 2000, 1500], jc_cols={2: "center", 3: "center"})
replace_placeholder(
    "[Pendiente: TEDE en el EAB (peores 2 h)",
    "La " + REF("_RefFig_dosis", "Figura 20") + " muestra la TEDE de las peores 2 horas frente a la distancia en el "
    "escenario E1: " + _f(_D[10]) + " mSv a 10 m, " + _f(_D[100], 2) + " mSv a 100 m y " + _f(_D[400], 2) + " mSv a "
    "400 m. Dividida por el χ/Q de 0–2 h, la dosis vale 1418 mSv·m³/s en las 40 distancias, con una dispersión del "
    "0,01 %: la dosis es proporcional al χ/Q, como corresponde a una emisión que termina en las dos primeras horas, y "
    "RADTRAD ha leído correctamente la tabla de χ/Q de cada caso.",
    [T("La " + REF("_RefTab_contrib", "Tabla 30") + " desglosa esa dosis por unidad de χ/Q con el inventario del "
       "Anexo D, la tasa de respiración de 3,5·10⁻⁴ m³/s de la RG 1.183 y los factores de dosis del fichero de "
       "RADTRAD. La inhalación del tritio, con 6368 Ci y un factor de 1,73·10⁻¹¹ Sv/Bq, aporta el 99,4 % de la TEDE; "
       "la inmersión en la nube de los gases nobles, el 0,36 %, y la inhalación del resto de nucleidos, el 0,22 %. "
       "El cálculo manual coincide con RADTRAD dentro del 1,2 %, y la dosis por inmersión que da RADTRAD "
       "(5,10 mSv·m³/s) coincide con la del cálculo manual (5,12 mSv·m³/s)."),
     CAP("Tabla", "Contribuciones a la TEDE por unidad de χ/Q (escenario E1)", "_RefTab_contrib"),
     _t_cont, EMPTY(),
     T("Como la emisión termina a las 2 horas, la dosis acumulada en 48 horas, 7 días y 30 días es prácticamente la de "
       "las dos primeras horas, y las zonas con el mismo límite, confinamiento y planificación (10 mSv), tienen el "
       "mismo radio. La TEDE de E2 es solo un 0,23 % mayor que la de E1: el edificio del reactor no retiene el tritio "
       "ni los gases nobles, y duplicar los yodos y las partículas apenas cambia una dosis que no depende de ellos. La "
       "dosis a tiroides es un 1,3 % mayor que la TEDE en E1, porque el tritio se reparte de manera uniforme en el "
       "organismo, y un 1,8 % mayor en E2 que en E1. Por la misma razón, las fracciones químicas del yodo apenas "
       "influyen: los yodos aportan menos del 0,2 % de la TEDE."),
     T("El capítulo @REFN:_RefCap_marco|3@ advertía de que distancias de pocas decenas de metros obligaban a comprobar "
       "que E2 recoge la pérdida de retención del recinto. Lo hace: su inventario duplica el de los yodos y las "
       "partículas (Anexo D). La dosis apenas cambia porque la gobierna el tritio, que ninguno de los dos escenarios "
       "retiene."),
     FIG(_FIG / "dosis_distancia.png", 15.0, "Gráfico logarítmico de la TEDE de las peores 2 horas frente a la "
         "distancia al reactor para el caso base calculado con RADTRAD y para la estimación con clase F y 1 m/s, con "
         "las líneas de los criterios de 1000, 250, 50 y 10 mSv."),
     CAP("Figura", "TEDE de las peores 2 horas frente a la distancia al reactor y criterios de las zonas",
         "_RefFig_dosis")])

# 13.3 radii
_t_rad = TABLE(("Zona", "Magnitud y límite", "Periodo", "Escenario", "Radio"),
               [("Límite del área de exclusión (EAB)", "TEDE, 250 mSv", "Peores 2 h", "E1", "≤ 10 m"),
                ("Zona de baja población (LPZ)", "TEDE, 250 mSv", "30 días", "E1", "≤ 10 m"),
                ("Evacuación", "TEDE, 50 mSv", "7 días", "E2", "15 m"),
                ("Confinamiento", "TEDE, 10 mSv", "48 h", "E1 y E2", "34 m"),
                ("Profilaxis con yodo", "Tiroides, 100 mSv", "7 días", "E1 y E2", "10 m"),
                ("Zona de planificación", "TEDE, 10 mSv", "96 h", "E1 y E2", "34 m"),
                ("Efectos deterministas, médula", "TEDE, 1000 mSv", "48 h", "E2", "≤ 10 m"),
                ("Efectos deterministas, tiroides", "Tiroides, 5000 mSv", "48 h", "E2", "≤ 10 m")],
               [3300, 1900, 1500, 1400, 1500], jc_cols={2: "center", 3: "center", 4: "center"})
replace_placeholder(
    "[Pendiente: tabla con el radio de cada zona",
    "La " + REF("_RefTab_radios", "Tabla 31") + " recoge el radio de cada zona de la @REF:_RefTab_criterios|Tabla 4@, "
    "medido desde el reactor. «≤ 10 m» indica que el criterio no se supera en la distancia mínima calculada. La "
    "dosis más alta del barrido, 99,6 mSv a 10 m, no llega al límite de 250 mSv del EAB y la LPZ ni a los umbrales "
    "de efectos deterministas; la evacuación alcanza 15 m, la profilaxis con yodo unos 10 m y el confinamiento y la "
    "zona de planificación, 34 m.",
    [CAP("Tabla", "Radios de las zonas de emergencia, medidos desde el reactor", "_RefTab_radios"),
     _t_rad, EMPTY(),
     T("Las zonas son pequeñas frente al propio buque (" + REF("_RefFig_zonas", "Figura 21") + " y "
       + REF("_RefFig_detalle", "Figura 22") + "). Con el reactor a 28 m de la popa y una manga de 42,5 m, la zona de "
       "evacuación queda dentro del casco, y la de confinamiento sobresale unos 6 m por la popa y unos 13 m por cada "
       "costado. Ninguna zona alcanza las instalaciones de la terminal más allá del propio muelle de atraque."),
     FIG(_FIG / "mapa_zonas_png.png", 13.0, "Esquema a escala, en metros desde el reactor, con el buque de 284,4 por "
         "42,5 m, el reactor a popa y las circunferencias de las ocho zonas de la Tabla 4."),
     CAP("Figura", "Zonas de emergencia a escala en torno al reactor (imagen estática generada por la herramienta)",
         "_RefFig_zonas"),
     FIG(_FIG / "detalle_satelite.png", 13.0, "Detalle sobre imagen de satélite del buque a escala y de las zonas de "
         "confinamiento, planificación, evacuación, EAB y LPZ en torno al reactor."),
     CAP("Figura", "Detalle de las zonas en torno al reactor sobre imagen de satélite (pestaña «Mapa de zonas»)",
         "_RefFig_detalle")])

# 13.4 comparison
replace_placeholder(
    "[Pendiente: comparación de los radios con los referentes del capítulo 3",
    "Los radios obtenidos son entre uno y dos órdenes de magnitud menores que los de los referentes de la "
    "@REF:_RefTab_sintesis|Tabla 3@: la zona de evacuación de 15 m frente a 30–130 m en Barrow y 600–800 m en el "
    "accidente de referencia de ARPANSA, y la de confinamiento de 34 m frente a 630 m en Barrow, 1,2–1,9 km en "
    "ARPANSA o la DEPZ de al menos 1,5 km de Devonport. Es lo que anticipaba el capítulo @REFN:_RefCap_marco|3@: "
    "aquellas distancias proceden de reactores de agua con fusión del núcleo, mientras que en el KP-FHR el TRISO y el "
    "FLiBe retienen casi todos los productos de fisión y la dosis la produce el tritio, cuyo factor de dosis por "
    "inhalación es unas quinientas veces menor que el del I-131.",
    [T("Con la @REF:_RefTab_sintesis|Tabla 3@ como guía, ni siquiera el caso de sensibilidad se acerca a las "
       "distancias de un submarino de 160 MWₜₕ, y las distancias genéricas de la Directriz básica, 100 m para la "
       "evacuación y 200 m para el confinamiento, envuelven los radios calculados con un margen de entre cuatro y "
       "siete veces."),
     T("El cálculo de ejemplo de Kairos Power da 7,2 mSv a 335 m, el 98 % por tritio @CITE:Kai20|25@. Este trabajo, con "
       "el mismo inventario de tritio, obtiene 0,14 mSv a esa distancia, y 0,27 mSv con clase F y 1 m/s. Como el "
       "tritio es el mismo, la diferencia está en el χ/Q: el ejemplo implica unos 5·10⁻³ s/m³ a 335 m, unas 48 veces "
       "el χ/Q de diseño de este trabajo, un valor que ni siquiera la clase F con 1 m/s alcanza con las expresiones de "
       "ARCON96. Con ese χ/Q, los radios serían de unos 47 m para el EAB, 110 m para la evacuación y 270 m para el "
       "confinamiento, del orden de las distancias genéricas de la Directriz.")])

# 13.5 sensitivity
_t_sens = TABLE(("Caso", "EAB / LPZ (250 mSv)", "Evacuación (50 mSv)", "Confinamiento y planificación (10 mSv)"),
                [("Caso base (E1 y E2, RADTRAD)", "≤ 10 m", "15 m", "34 m"),
                 ("Escenario E2 en todas las zonas", "≤ 10 m", "15 m", "34 m"),
                 ("Clase F y 1 m/s (estimación)", "11 m", "22 m", "48 m"),
                 ("Inventario de tritio × 2", "≤ 10 m", "21 m", "48 m"),
                 ("Inventario de tritio × 10", "21 m", "48 m", "113 m"),
                 ("χ/Q del ejemplo de Kairos Power (× 48)", "47 m", "110 m", "267 m")],
                [3700, 1900, 1900, 2100], jc_cols={1: "center", 2: "center", 3: "center"})
replace_placeholder(
    "[Pendiente: efecto sobre los radios de las fracciones de yodo",
    "La " + REF("_RefTab_sens", "Tabla 32") + " resume el efecto sobre los radios de las hipótesis más inciertas. "
    "Como la dosis es proporcional al χ/Q y al inventario de tritio, y decrece aproximadamente como d⁻¹·⁹, multiplicar "
    "la dosis por un factor k multiplica los radios por k⁰·⁵³.",
    [B("Fracciones químicas del yodo: los yodos aportan menos del 0,2 % de la TEDE y el 1,8 % de la dosis a tiroides, "
       "de modo que cualquier reparto entre aerosol, yodo elemental y orgánico cambia los radios menos de un 1 %."),
     B("Factores de atenuación: no acreditar el edificio del reactor (E2) aumenta la TEDE un 0,23 % y no cambia ningún "
       "radio. Las barreras del combustible y del FLiBe no afectan al tritio, que se libera por completo."),
     B("Meteorología: con clase F y 1 m/s todas las horas, el χ/Q de 0–2 h es unas tres veces el de diseño a 10 m y "
       "unas dos veces entre 30 y 400 m. Los radios de la tabla se han estimado con las expresiones de ARCON96, que "
       "reproducen el χ/Q de diseño del caso base, y la relación TEDE/χ/Q de RADTRAD; la herramienta calcula el caso "
       "completo con ARCON96 y RADTRAD (capítulo @REFN:_RefCap_herr|12@)."),
     B("Inventario de tritio: es la hipótesis que más pesa. Duplicarlo lleva el confinamiento a 48 m; multiplicarlo por "
       "diez, a 113 m. Su forma química también es decisiva: el factor de dosis del tritio como gas (HT) es unas "
       "diez mil veces menor que el del agua tritiada (HTO) que se ha supuesto."),
     CAP("Tabla", "Sensibilidad de los radios a las hipótesis del cálculo", "_RefTab_sens"),
     _t_sens, EMPTY()])
C.on_paragraph(P("Meteorología: con clase F y 1 m/s todas las horas"),
               "Radios del caso clase F estimados con las expresiones de ARCON96 (Pasquill–Gifford + meandro), que "
               "reproducen el χ/Q del caso base, y TEDE/χQ = 1418 mSv·m³/s de RADTRAD. Sustituir por los de la "
               "ejecución SENS_F1 cuando se disponga de ellos.")

# ===================================================== chapter 14 ========
replace_placeholder("[Pendiente: completar con los resultados numéricos del capítulo 13.",
   "Las zonas de emergencia de un buque con KP-FHR atracado en el puerto exterior de Bilbao son de pocas decenas de "
   "metros en torno al reactor: la evacuación alcanza 15 m y el confinamiento y la planificación, 34 m, y el criterio "
   "de 250 mSv del EAB y la LPZ se cumple ya a 10 m. Las conclusiones de detalle se agrupan a continuación.")
p_term = P("La revisión del inventario ha puesto de manifiesto un error del cálculo inicial")
_res_h = HEAD("Sobre las zonas de emergencia en el puerto de Bilbao")
after(p_term, [
    _res_h,
    T("La dosis la produce la inhalación del tritio, el 99,4 % de la TEDE; los productos de fisión que superan el "
      "combustible TRISO y el FLiBe aportan menos del 1 %. Por eso E1 y E2 dan las mismas zonas, las fracciones "
      "químicas del yodo no influyen y la dosis a tiroides apenas supera a la TEDE. Las distancias calculadas, 15 m "
      "para la evacuación y 34 m para el confinamiento y la planificación, quedan entre uno y dos órdenes de magnitud "
      "por debajo de las de los buques y submarinos de propulsión nuclear con reactores de agua, y también por debajo "
      "de las distancias genéricas de la Directriz básica (100 y 200 m), que las envuelven con un margen de cuatro a "
      "siete veces."),
    T("El resultado es robusto frente a las hipótesis sobre las barreras, pero sensible al χ/Q y al inventario de "
      "tritio. Con clase F y viento de 1 m/s, los radios estimados son de 22 m y 48 m; harían falta un χ/Q unas 50 "
      "veces mayor, como el implícito en el ejemplo de Kairos Power, o un inventario de tritio unas 30 veces mayor "
      "para alcanzar las distancias de la Directriz."),
    T("Las zonas apenas salen del buque: la de evacuación queda dentro del casco y la de confinamiento sobresale unos "
      "6 m por la popa y unos 13 m por los costados. En la práctica, la planificación de la escala la determinan el "
      "control del muelle y de la lámina de agua del atraque más que la protección de la población, y las distancias "
      "de la Directriz pueden adoptarse como zonas de planificación conservadoras en torno al reactor."),
    HEAD("Sobre las condiciones de escala"),
    T("Los resultados permiten concretar las condiciones de escala propuestas en el capítulo @REFN:_RefCap_marco|3@:"),
    B("Atraque: el puerto exterior y la terminal de GNL de Zierbena son adecuados; con zonas de pocas decenas de "
      "metros, ninguna zona habitada ni instalación ajena al atraque queda afectada."),
    B("Operaciones prohibidas: se mantiene la prohibición de manipular combustible y de abrir el recinto del reactor, "
      "porque los sucesos excluidos del análisis podrían liberar algo más que el tritio."),
    B("Maniobras y retirada: como la emisión del accidente base de diseño dura 2 horas, retirar el buque no reduce su "
      "dosis; los remolcadores y el plazo de retirada se justifican para los sucesos más allá del diseño."),
    B("Vigilancia radiológica: debe incluir la medida de tritio en aire (agua tritiada), que es el nucleido que "
      "determina la dosis y que los equipos habituales de tasa de dosis gamma no detectan."),
    B("Profilaxis con yodo: con un radio de unos 10 m, el reparto de yodo estable se limita a la tripulación y al "
      "personal del muelle de atraque."),
    B("Plan de emergencia: la coordinación con el plan de protección civil de Euskadi y con el CSN puede apoyarse en "
      "las distancias genéricas de la Directriz, que envuelven las calculadas."),
])
RR("La herramienta automatiza el barrido de distancias, sectores y fracciones de yodo",
   "la lectura de las columnas de la distribución acumulada de ARCON96 y la construcción de la tabla de χ/Q que recibe "
   "RADTRAD.",
   "la lectura de las columnas de la distribución acumulada de ARCON96 y la construcción de la tabla de χ/Q que recibe "
   "RADTRAD. La ejecución con los códigos reales ha descubierto otros tres, entre ellos la escala de la distribución "
   "acumulada de ARCON96, que multiplicaba por diez el χ/Q de los periodos largos en algunas distancias. La "
   "herramienta comprueba ahora en cada caso que el percentil 95 que calcula coincide con el de ARCON96, y la "
   "proporcionalidad entre dosis y χ/Q en todas las distancias confirma que RADTRAD recibe los datos correctos. La "
   "interfaz gráfica reúne el cálculo, el generador de escenarios de RADTRAD y el mapa de las zonas sobre la "
   "cartografía del puerto (Anexo F).")
p_lim_last = P("El análisis considera el buque atracado y no las fases de aproximación")
after(p_lim_last, [
    B("Los resultados se han obtenido con un juego de fracciones químicas del yodo, y el caso con clase F y 1 m/s se ha "
      "estimado con las expresiones de ARCON96; como el tritio domina la dosis, ninguna de las dos simplificaciones "
      "cambia las conclusiones."),
    B("Las distancias calculadas son del orden de las dimensiones del buque. A esa escala la emisión real no es "
      "puntual, y la estela del buque y del muelle, que no se acredita, aumentaría la dispersión."),
    B("La posición del atraque y la del reactor dentro del buque son aproximadas; las zonas se desplazan con ellas, "
      "pero sus radios no cambian."),
])
p_fut_last = P("Contrastar los resultados de ARCON96 con PAVAN para las distancias mayores")
after(p_fut_last, [
    B("Calcular el caso de sensibilidad meteorológica completo con ARCON96 y RADTRAD y varios juegos de fracciones del "
      "yodo, y fijar sobre la cartografía la posición exacta del atraque y del reactor."),
    B("Estudiar la forma química del tritio liberado (HT o HTO) y su conversión en el ambiente, que puede cambiar la "
      "dosis en varios órdenes de magnitud."),
])

C.on_paragraph(_res_h, "Capítulos 13 y 14 completados con la ejecución del 5-6 de noviembre (10–400 m, E1 y E2, un "
               "juego de fracciones). Radios: EAB/LPZ ≤ 10 m, EVAC 15 m, CONF/PLAN 34 m, YODO 10 m. Caso clase F "
               "estimado (22 y 48 m), pendiente de la ejecución SENS_F1. Se añaden los anexos D (ficheros de entrada), "
               "E (χ/Q de diseño) y F (manual de usuario).")

# ===================================================== annexes ===========
_body_sect = body.find(q("sectPr"))
_ct_path = UN / "[Content_Types].xml"
_last_par = _body_sect.getprevious()


def _footer_for(letra):
    src = (UN / "word/footer8.xml").read_text(encoding="utf8")
    name = "footer_anexo%s.xml" % letra
    (UN / "word" / name).write_text(src.replace("Anexo C – ", "Anexo %s – " % letra), encoding="utf8")
    _add_rel("rIdFtr%s" % letra, "footer", name)
    ct = _ct_path.read_text(encoding="utf8")
    if name not in ct:
        ct = ct.replace("</Types>", '<Override PartName="/word/%s" ContentType="application/vnd.openxmlformats-'
                        'officedocument.wordprocessingml.footer+xml"/></Types>' % name)
        _ct_path.write_text(ct, encoding="utf8")
    return "rIdFtr%s" % letra


_cursor = [_last_par]


def ANEXO(letra, titulo, contenido):
    """Close the current section with the current properties and start annex <letra> in a new one."""
    sp = el("p")
    ppr = el("pPr", None, copy.deepcopy(_body_sect))
    ppr.append(el("rPr", None, track_attrs(el("ins"))))
    sp.append(ppr)
    for x in sp.iter(q("sectPr")):
        for a in list(x.attrib):
            del x.attrib[a]
    _cursor[0] = after(_cursor[0], [sp])
    _body_sect.find(q("footerReference")).set(
        "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id", _footer_for(letra))
    h = new_para_like(_m_anx, "Anexo %s: %s" % (letra, titulo))
    _cursor[0] = after(_cursor[0], [h] + contenido)
    return h


# ---- Annex D: RADTRAD input files
_GRUPOS = {1: "Gases nobles", 2: "Yodo", 3: "Cesio", 4: "Telurio", 5: "Estroncio", 6: "Bario", 7: "Rutenio",
           8: "Cerio", 9: "Lantano"}


def _nif(p):
    t = p.read_text(encoding="latin-1").splitlines()
    out, i = [], 0
    while i < len(t):
        if _re.match(r"\s*Nuclide \d+:", t[i]):
            out.append((t[i + 1].strip(), int(t[i + 2]), float(t[i + 3]), float(t[i + 5])))
            i += 6
        else:
            i += 1
    return out


def _semivida(s):
    for f_, u in ((365.25 * 86400, "a"), (86400, "d"), (3600, "h"), (60, "min")):
        if s >= f_:
            v = s / f_
            return (_f(v, 1) if v < 100 else "{:,.0f}".format(v).replace(",", ".")) + " " + u
    return _f(s, 0) + " s"


_n1 = _nif(_HT / "Defaults/kpfhr_terminofuente.nif")
_n2 = dict((n, c) for n, g, s, c in _nif(_HT / "Defaults/kpfhr_terminofuente_E2.nif"))
_t_nif = TABLE(("Nucleido", "Grupo", "Semivida", "E1 (Ci/MWₜₕ)", "E1 (Ci)", "E2 (Ci)"),
               [(n, _GRUPOS[g], _semivida(s), _e(c), _e(c * 320), _e(_n2[n] * 320)) for n, g, s, c in _n1],
               [1300, 1600, 1500, 1800, 1700, 1700], sz=16, jc_cols={2: "right", 3: "right", 4: "right", 5: "right"})
_rft = (_HT / "Defaults/kpfhr_directo.rft").read_text(encoding="latin-1").splitlines()
_psf = (_HT / "template_kpfhr.psf").read_text(encoding="latin-1").splitlines()
# dose factors of the inventory nuclides
_inp = (_HT / "Defaults/fgr11&12.inp").read_text(encoding="latin-1").splitlines()
_dcf, _cur = {}, None
for _ln in _inp:
    _s = _ln.strip()
    if _re.fullmatch(r"[A-Z][a-z]?-\d{1,3}m?", _s) and not _ln.startswith(" "):
        _cur = _s; _dcf[_cur] = {}
    elif _cur and _ln[:10].strip() in ("EFFECTIVE", "THYROID"):
        _dcf[_cur][_ln[:10].strip()] = [float(x) for x in _re.findall(r"-?\d\.\d+E[+-]\d+", _ln)]
_t_dcf = TABLE(("Nucleido", "Inhalación, efectiva (Sv/Bq)", "Inhalación, tiroides (Sv/Bq)",
                "Inmersión, efectiva (Sv·m³/(Bq·s))"),
               [(n, _e(_dcf[n]["EFFECTIVE"][5]), _e(_dcf[n]["THYROID"][5]), _e(_dcf[n]["EFFECTIVE"][0]))
                for n, g, s, c in _n1], [1500, 2700, 2700, 2700], sz=16,
               jc_cols={1: "right", 2: "right", 3: "right"})
ANEXO("D", "Ficheros de entrada de RADTRAD", [
    T("Este anexo recoge los ficheros de entrada con los que la herramienta del capítulo @REFN:_RefCap_herr|12@ ejecuta "
      "RADTRAD. Son los del paquete de ejecución de la herramienta (carpeta Defaults), y con ellos se han obtenido los "
      "resultados del capítulo @REFN:_RefCap_res|13@."),
    SUB("D.1 Inventario (kpfhr_terminofuente.nif y kpfhr_terminofuente_E2.nif)"),
    T("El inventario se expresa en Ci por MWₜₕ, y RADTRAD lo multiplica por la potencia de 320 MWₜₕ que fija el "
      "escenario. La " + REF("_RefTab_nif", "Tabla 33") + " lista los 33 nucleidos con su grupo químico y su semivida, "
      "la actividad de E1 (fuera del edificio del reactor) y la de E2 (a la salida del FLiBe). Los yodos y las "
      "partículas de E2 duplican los de E1, y los gases nobles y el tritio son iguales en ambos."),
    CAP("Tabla", "Inventario liberado al exterior en los escenarios E1 y E2", "_RefTab_nif"),
    _t_nif, EMPTY(),
    SUB("D.2 Fracciones y tiempos de liberación (kpfhr_directo.rft)"),
    T("Todo el inventario de cada grupo químico se libera en la primera fase, de 0 a 2 horas, y las fases siguientes "
      "no liberan nada:"),
] + LISTING(_rft) + [EMPTY(),
    SUB("D.3 Escenario de RADTRAD (template_kpfhr.psf)"),
    T("La plantilla define un compartimento de 3,892·10⁵ ft³ que descarga directamente al ambiente con un caudal de "
      "10⁶ cfm, de modo que el término fuente sale al exterior a medida que se libera; la potencia de 320 MWₜₕ; los "
      "ficheros de inventario, liberación y factores de dosis; las fracciones químicas del yodo (aerosol, elemental y "
      "orgánico), y dos receptores, el EAB y la LPZ, con las tasas de respiración de la RG 1.183. Para cada distancia y "
      "juego de fracciones, la herramienta sustituye el nombre del inventario, la línea de fracciones del yodo y las "
      "tablas de χ/Q de los dos receptores, que se escriben en el formato de columnas que lee RADTRAD con los valores "
      "por intervalo del Anexo E; los valores de χ/Q que figuran en la plantilla son solo de ejemplo. El control room "
      "del modelo original se conserva sin uso."),
LISTCOLS(_psf), EMPTY(),
    SUB("D.4 Factores de conversión de dosis (fgr11&12.inp)"),
    T("El fichero contiene los factores de FGR 11 y FGR 12 de 61 nucleidos, incluido el H-3 añadido para este trabajo "
      "(agua tritiada, 1,73·10⁻¹¹ Sv/Bq por inhalación). RADTRAD asigna los factores por posición, por lo que la "
      "herramienta genera para cada inventario una copia con los mismos nucleidos y en el mismo orden. La "
      + REF("_RefTab_dcf", "Tabla 34") + " recoge los factores de los nucleidos del inventario que intervienen en la "
      "TEDE y en la dosis a tiroides."),
    CAP("Tabla", "Factores de conversión de dosis de los nucleidos del inventario", "_RefTab_dcf"),
    _t_dcf,
])

# ---- Annex E: design χ/Q
_t_xq0 = TABLE(("d (m)",) + tuple("%d h" % h for h in _H),
               [(str(v),) + tuple(_e(_M[v][h], 2) for h in _H) for v in _V],
               [800] + [880] * 10, sz=14, jc_cols={i: "center" for i in range(11)})
_t_xqp = TABLE(("d (m)", "0–2 h", "2–4 h", "4–8 h", "8–12 h", "12–24 h", "1–4 d", "4–7 d", "7–15 d", "15–30 d"),
               [(str(v),) + tuple(_e(x, 2) for x in _PSF[v][1]) for v in _V],
               [800] + [975] * 9, sz=14, jc_cols={i: "center" for i in range(10)})
ANEXO("E", "Coeficientes de dispersión de diseño", [
    T("La " + REF("_RefTab_xq0", "Tabla 35") + " recoge el χ/Q de diseño de cada distancia y periodo de promediado: el "
      "mayor entre el percentil 99,5 del peor sector y el percentil 95 global, calculados con ARCON96 con los cinco "
      "años de meteorología adaptada (hoja «Maximun» del fichero 99_5th_PERCENTILE_XQ_VALUES_Sector_BY_HOUR.xlsx). Son "
      "medias desde el inicio de la emisión hasta cada periodo."),
    CAP("Tabla", "χ/Q de diseño (s/m³) promediado desde el inicio de la emisión", "_RefTab_xq0"),
    _t_xq0, EMPTY(),
    T("RADTRAD aplica cada valor de χ/Q desde su instante hasta el siguiente, por lo que necesita el valor de cada "
      "intervalo y no la media desde el inicio. La " + REF("_RefTab_xqpsf", "Tabla 36") + " recoge los valores por "
      "intervalo que la herramienta escribe en el escenario de cada distancia, obtenidos de la tabla anterior con "
      "X/Q(t₁→t₂) = (t₂·X/Q(0→t₂) − t₁·X/Q(0→t₁)) / (t₂ − t₁), con el máximo de 1 y 2 horas en el primer intervalo; "
      "el último valor se mantiene hasta 720 horas."),
    CAP("Tabla", "χ/Q por intervalo (s/m³) escrito en el escenario de RADTRAD", "_RefTab_xqpsf"),
    _t_xqp,
])

# ---- Annex F: user manual
ANEXO("F", "Manual de usuario de la herramienta", [
    T("La herramienta, RADTRAD Tool, ejecuta la cadena de cálculo del capítulo @REFN:_RefCap_marcocalc|7@ desde una "
      "interfaz gráfica con tres pestañas: el pipeline de ARCON96 y RADTRAD, el generador de escenarios de RADTRAD y "
      "el mapa de las zonas. Este anexo explica cómo instalarla, lanzarla e interpretar sus resultados."),
    SUB("F.1 Requisitos e instalación"),
    B("Sistema: Windows con ARCON96 y RADTRAD 3.03 en modo batch. Rutas por defecto: C:\\ARCON96\\arcon96f.exe y "
      "C:\\RADTRAD\\RADTRAD3.03x\\Distribution0203\\BatchModeVersion\\radtrad.exe; pueden cambiarse en la interfaz."),
    B("Python: versión 3.10 o posterior, instalada desde python.org marcando «Add python to PATH». Las librerías "
      "(pandas, numpy, openpyxl y matplotlib) se instalan con python -m pip install -r requirements.txt."),
    B("Carpeta: el paquete TFM_ejecucion se copia a una ruta sin espacios ni acentos, por ejemplo C:\\TFM_ejecucion. "
      "Contiene los programas, los datos de entrada en INPUT (MET, NIF, RFT, INP y PSF) y los ficheros por defecto en "
      "Defaults."),
    B("Internet: solo hace falta para descargar la cartografía del mapa; el cálculo funciona sin conexión."),
    SUB("F.2 Lanzamiento"),
    T("La interfaz se abre con doble clic en LANZAR_RADTRAD.bat, que ejecuta RADTRAD_GUI.py y, si algo falla, deja la "
      "ventana de consola abierta con el mensaje de error. El botón «Ayuda» muestra la ayuda integrada."),
    SUB("F.3 Pestaña «Pipeline ARCON96 + RADTRAD»"),
    T("Es la pestaña de cálculo (" + REF("_RefFig_guipipe", "Figura 23") + "). El panel izquierdo tiene dos secciones "
      "que se activan con su interruptor; el derecho muestra el registro de la ejecución. Pasos:"),
    B("Datos meteorológicos: los ficheros MET01 a MET05 de INPUT\\MET se cargan solos; también pueden arrastrarse o "
      "generarse desde la plantilla Excel, una hoja por año. Número de ficheros: 5."),
    B("ARCON96: distancia mínima, máxima y paso del barrido (por defecto, de 10 a 400 m cada 10 m) y ruta de "
      "arcon96f.exe. La casilla «Sensibilidad meteorológica (clase F, 1 m/s)» añade el caso de sensibilidad tras el "
      "caso base."),
    B("RADTRAD: escenario (plantilla template_kpfhr.psf o el creado con el generador), inventario (.nif; el de E2 se "
      "detecta solo si está junto al de E1), fichero de liberación (.rft), factores de dosis (.inp), ruta de "
      "radtrad.exe y número y valores de los juegos de fracciones del yodo."),
    B("Ejecución: «EJECUTAR PIPELINE». Con los interruptores puede lanzarse solo ARCON96, o solo RADTRAD con el χ/Q de "
      "una ejecución anterior. «Guardar config» y «Cargar config» guardan y recuperan todos los parámetros."),
    FIG(_FIG / "gui_pipeline.png", 15.5, "Pestaña Pipeline ARCON96 más RADTRAD: sección de datos meteorológicos y "
        "parámetros de ARCON96 a la izquierda y registro de la ejecución a la derecha."),
    CAP("Figura", "Pestaña «Pipeline ARCON96 + RADTRAD» de la herramienta", "_RefFig_guipipe"),
    SUB("F.4 Pestaña «Generador PSF»"),
    T("Permite crear escenarios de RADTRAD distintos de la plantilla: compartimentos, caminos de transporte, filtros, "
      "receptores y tasas de respiración (" + REF("_RefFig_guipsf", "Figura 24") + "). Pide volúmenes en m³, caudales "
      "en m³/s y fugas en 1/s, y los escribe en las unidades de RADTRAD (ft³, cfm y %/día). La pestaña «Vista "
      "previa» muestra el esquema de compartimentos y el fichero resultante."),
    FIG(_FIG / "gui_psf.png", 15.5, "Pestaña Generador PSF de la herramienta con los datos generales del escenario."),
    CAP("Figura", "Pestaña «Generador PSF» de la herramienta", "_RefFig_guipsf"),
    SUB("F.5 Pestaña «Mapa de zonas»"),
    T("Se abre sola al terminar cada ejecución (" + REF("_RefFig_guimapa", "Figura 18") + "):"),
    B("Resultados: selector con todas las ejecuciones (caso base y sensibilidad) y botón para abrir un "
      "zonas_emergencia.json."),
    B("Zonas: casilla para mostrar cada zona, límite editable en mSv y radio, que se recalcula al cambiar el límite."),
    B("Buque: latitud, longitud y rumbo (dirección de la proa) del centro del buque, eslora, manga y distancia del "
      "reactor a la popa; «Atraque por defecto (BBG)» recupera la posición del pantalán de GNL."),
    B("Mapa: OpenStreetMap, callejero o satélite, con el buque, el reactor y las zonas a escala, la cuadrícula de "
      "coordenadas y la latitud y longitud del cursor. Rueda: zoom; arrastrar: mover; clic derecho: situar el centro "
      "del buque; doble clic: ajustar la vista."),
    B("Salidas: «Guardar buque y criterios» reescribe zonas_emergencia.json, mapa_zonas.html y mapa_zonas.png; "
      "«Exportar PNG» guarda la imagen para informes y «Abrir mapa en el navegador» abre el visor web completo."),
    SUB("F.6 Resultados"),
    T("Cada ejecución crea una carpeta RUN_N con tres subcarpetas: INPUT_USED (copia de los datos empleados), WORK "
      "(casos de ARCON96 y RADTRAD, que pueden borrarse) y OUTPUT, con:"),
    B("χ/Q: 99_5th_PERCENTILE_XQ_VALUES_Sector_BY_HOUR.xlsx (χ/Q de diseño, Anexo E), TOTAL_XQs_BY_HOUR.xlsx y los "
      "registros de ARCON96."),
    B("Dosis: Sets_Worst2h.xlsx (TEDE de las peores 2 horas por juego de fracciones y distancia) y "
      "post_timeseries_accum.csv (dosis acumuladas)."),
    B("Zonas: zonas_emergencia.json, mapa_zonas.html y mapa_zonas.png."),
    B("Escenarios y sensibilidad: subcarpetas E2 y SENS_F1 con la misma estructura; pipeline.log, registro completo."),
    SUB("F.7 Uso por consola"),
    T("Sin interfaz, python PIPELINE.py pide todos los parámetros al principio y ejecuta la cadena completa; "
      "python sensibilidad_met.py ejecuta el caso de sensibilidad; python zonas_emergencia.py psf_batch\\postprocess "
      "regenera solo las zonas y el mapa, y VER_MAPA.bat abre el mapa más reciente en el navegador."),
    SUB("F.8 Problemas frecuentes"),
    B("La ventana no se abre: lanzar LANZAR_RADTRAD.bat para ver el error; si falta una librería, instalarla con pip."),
    B("ARCON96 termina con error: comprobar la ruta del ejecutable y los ficheros MET; la herramienta conserva la "
      "carpeta del primer caso fallido y copia el mensaje de ARCON96 en pipeline.log."),
    B("Aviso «differs from ARCON96's» en pipeline.log: el percentil leído del fichero de distribución no coincide con "
      "el de ARCON96; no debe aparecer, y si aparece hay que revisar ese caso."),
    B("El mapa no muestra cartografía: sin conexión a internet se dibujan solo las zonas; las teselas descargadas se "
      "guardan en cache_teselas y se reutilizan."),
])

# ------------------------------------------------- renumber SEQ fields ---
def _renumber():
    """Cached results of SEQ Tabla/Figura fields in document order and of REF fields to caption bookmarks."""
    cnt, bm_num = {}, {}
    open_bm = {}
    order = list(body.iter())
    for i, e in enumerate(order):
        if e.tag == q("bookmarkStart"):
            open_bm[e.get(q("id"))] = e.get(q("name"))
        if any(a.tag == q("del") for a in e.iterancestors()) or in_fallback(e):
            continue
        kind = None
        if e.tag == q("fldSimple"):
            m_ = _re.match(r"\s*SEQ (\w+)", e.get(q("instr")) or "")
            if m_:
                kind = m_.group(1)
                res_t = [t for t in e.iter(q("t"))]
        elif e.tag == q("instrText") and _re.match(r"\s*SEQ (\w+)", e.text or ""):
            kind = _re.match(r"\s*SEQ (\w+)", e.text).group(1)
            # result text: first w:t after the 'separate' fldChar of this field
            res_t, sep = [], False
            for x in order[i + 1:]:
                if x.tag == q("fldChar") and x.get(q("fldCharType")) == "separate":
                    sep = True
                elif x.tag == q("fldChar") and x.get(q("fldCharType")) == "end":
                    break
                elif sep and x.tag == q("t"):
                    res_t.append(x)
        if kind in ("Tabla", "Figura"):
            cnt[kind] = cnt.get(kind, 0) + 1
            if res_t:
                res_t[0].text = str(cnt[kind])
                for t_ in res_t[1:]:
                    t_.text = ""
            p_ = e if e.tag == q("p") else next(a for a in e.iterancestors() if a.tag == q("p"))
            for bs in p_.iter(q("bookmarkStart")):
                if bs.get(q("name")).startswith("_Ref"):
                    bm_num[bs.get(q("name"))] = "%s %d" % (kind, cnt[kind])
    # REF fields
    for it in list(body.iter(q("instrText"))):
        m_ = _re.match(r"\s*REF (\S+)( \\h)?\s*$", it.text or "")
        if not m_ or m_.group(1) not in bm_num:
            continue
        res_t, sep = [], False
        r0 = it.getparent()
        x = r0.getnext()
        # walk following siblings (also across ins wrappers)
        seq = list(r0.itersiblings())
        if not seq and r0.getparent().tag == q("ins"):
            seq = list(r0.getparent().itersiblings())
        flat = []
        for s_ in [r0] + list(r0.itersiblings()):
            flat.append(s_)
        for s_ in flat[1:]:
            fc = s_.find(q("fldChar"))
            if fc is not None and fc.get(q("fldCharType")) == "separate":
                sep = True; continue
            if fc is not None and fc.get(q("fldCharType")) == "end":
                break
            if sep:
                res_t += list(s_.iter(q("t")))
        if res_t:
            res_t[0].text = bm_num[m_.group(1)]
            for t_ in res_t[1:]:
                t_.text = ""
    return cnt


_counts = _renumber()
print("captions:", _counts)
