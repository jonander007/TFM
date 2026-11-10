# v13: last full reading before delivery as PDF only. Slips left by earlier passes, a cross-reference that
# _renumber() had broken, references to files the reader of a PDF will not have, and the user manual of
# Anexo F brought up to date with the tool (installation type, PSF generator).
_FAIL13 = []


def _s13(fn):
    def w(*a, **k):
        try:
            return fn(*a, **k)
        except (SystemExit, Exception) as e:
            _FAIL13.append("%s%r: %s" % (fn.__name__, tuple(str(x)[:50] for x in a[:2]), e))
    w.__name__ = fn.__name__
    return w


def _rrv(sub, old, new):
    """Tracked replacement in the first paragraph whose visible text contains `sub` and `old`."""
    p = next((p for p in paras() if sub in visible(p) and old in visible(p) and p not in _bibp), None)
    if p is None:
        raise SystemExit("not found")
    RRo(p, old, new)
    return p


V = _s13(_rrv)
_ap13 = _s13(_append)

# ------------------------------------------------------------- wording slips
V("dentro del combinación energética", "dentro del combinación energética", "dentro de la combinación energética")
V("no solo propone una metodología robusta", "una metodología robusta", "una metodología")
V("objeto de estudio del presente informe", "del presente informe, y que se definen de la siguiente manera",
  "del presente trabajo, y que se definen de la siguiente manera:")
V("operación de la carga LNG", "carga LNG", "carga de GNL")
_s13(lambda: RRo(P("Características principales del buque LNG de referencia", style="Descripcin"), "buque LNG de referencia", "metanero de referencia"))()
V("La dosis efectiva total (TEDE) es la suma", "La dosis efectiva total (TEDE)", "El equivalente de dosis efectiva total (TEDE)")
V("El equivalente de dosis efectiva total (TEDE) es la suma", "las peores 2 horas en el EAB", "cualquier ventana de 2 horas en el EAB")
V("las dosis calculadas sobrestiman las que produciría", "sobrestiman", "tienden a sobrestimar")
V("fue de 7,2 mSv (0,716 rem)", "7,2 mSv (0,716 rem)", "7,16 mSv (0,716 rem)")
V("que constituye el isotópico de partida", "el isotópico de partida", "el inventario isotópico de partida")
V("para la definición del isotópico de partida", "del isotópico de partida", "del inventario isotópico de partida")
V("se adoptan los valores de dicha tabla sin modificaciones", "de dicha tabla", "de dicha figura")
V("manteniendo el resto de las barreras según la tabla", "según la tabla", "según la figura")
V("Otra característica que es necesaria abordar", "que es necesaria abordar", "que es necesario abordar")
V("para calcular las zonas de exclusión: con la actividad", "las zonas de exclusión", "las zonas de emergencia")
V("para obtener resultados confiables", "confiables", "fiables")
V("Piscina superpuesta (overlay pool)", "overlay pool", "overlying pool")
V("Los ficheros correspondientes se encuentran en la carpeta de la herramienta",
  "Los ficheros correspondientes se encuentran en la carpeta de la herramienta (template_kpfhr.psf y la carpeta Defaults).",
  "Los ficheros correspondientes se reproducen en el Anexo D.")
V("«≤ 10 m» expresa la resolución del estudio", "«≤ 10 m» expresa la resolución del estudio y no permite",
  "ese valor expresa la resolución del estudio y no permite")
V("con unos 101–103 mSv a tiroides a 10 m", "con unos 101–103 mSv a tiroides a 10 m",
  "con unos 101 mSv a tiroides a 10 m en E1 y 103 mSv en E2,")
V("el criterio de 250 mSv del EAB y la LPZ se cumple ya a 10 m. Las conclusiones", "se cumple ya a 10 m",
  "se cumple ya en la distancia mínima calculada, 10 m")
V("Su verificación con ejecutables sustitutos ha permitido además detectar",
  "Su verificación con ejecutables sustitutos ha permitido además detectar y corregir dos errores del procedimiento "
  "de cálculo inicial: la lectura de las columnas de la distribución acumulada de ARCON96 y la construcción de la "
  "tabla de X/Q que recibe RADTRAD. La ejecución con los códigos reales ha descubierto otros tres, entre ellos la "
  "escala de la distribución acumulada de ARCON96, que multiplicaba por diez el X/Q de los periodos largos en "
  "algunas distancias.",
  "Su verificación con ejecutables sustitutos y las ejecuciones con los códigos reales han permitido detectar y "
  "corregir cinco errores del procedimiento de cálculo inicial (capítulo 12), entre ellos la lectura de la "
  "distribución acumulada de ARCON96, el formato de la tabla de X/Q que recibe RADTRAD y la escala de esa "
  "distribución, que multiplicaba por diez el X/Q de los periodos largos en algunas distancias.")
# translated quotations and terms in angle quotes, as in the rest of the memoria
_nq = 0
for _p in paras():
    if _p in _bibp or "Afrikantov" in visible(_p) or "Kurchatov" in visible(_p):
        continue
    for _o, _n_ in (("“", "«"), ("”", "»")):
        _g = 0
        while _o in visible(_p) and _o in ptext(_p) and _g < 6:
            _g += 1
            try:
                RRo(_p, _o, _n_); _nq += 1
            except ValueError:
                break
print("quotes:", _nq)
# headings with stray blanks (" RESULTADOS ", " CONCLUSIONES")
for _p in paras():
    _st = _p.find(q("pPr") + "/" + q("pStyle"))
    if _st is not None and _st.get(q("val")) == "Ttulo1":
        _ts = [t for t in _p.iter(q("t"))]
        if _ts and "".join(t.text or "" for t in _ts) != "".join(t.text or "" for t in _ts).strip():
            _ts[0].text = (_ts[0].text or "").lstrip(); _ts[-1].text = (_ts[-1].text or "").rstrip()

# ------------------------------------------- references to files outside the PDF
V("El modelo es el fichero datos/ahp/TFM_KP-FHR_final_v2.smt",
  "El modelo es el fichero datos/ahp/TFM_KP-FHR_final_v2.smt y el cálculo se reproduce con datos/ahp/ahp.py, que da "
  "los mismos pesos, intensidades y puntuaciones que SMART.",
  "El cálculo se ha reproducido además de forma independiente con un programa propio, que da los mismos pesos, "
  "intensidades y puntuaciones que SMART.")
V("Son los del paquete de ejecución de la herramienta (carpeta Defaults)",
  "Son los del paquete de ejecución de la herramienta (carpeta Defaults), y con ellos",
  "Se reproducen aquí porque el código de la herramienta no forma parte de este documento; con ellos")
V("calculados con ARCON96 con los cinco años de meteorología adaptada (hoja «Maximun»",
  " (hoja «Maximun» del fichero 99_5th_PERCENTILE_XQ_VALUES_Sector_BY_HOUR.xlsx)", "")

# ------------------------------------------------------------ bibliography
for _old, _new in (("«NUREG-0800, Standard Review Plan, Section 2.3.3: Onsite Meteorological Measurements Programs,» "
                    "Washington, DC.", "«NUREG-0800, Standard Review Plan, Section 2.3.3: Onsite Meteorological "
                    "Measurements Programs, Rev. 3,» Washington, DC, 2007."),
                   ("for the KP-FHR (Public Release)».", "for the KP-FHR (Public Release)», s. f.")):
    _pb = next((p for p in _bibp if _old in visible(p)), None)
    if _pb is None:
        _FAIL13.append("bib: " + _old[:40])
    else:
        RRo(_pb, _old, _new)

# -------------------------------------------- chapter 12: what the interface covers
_p_ifz = P("El buque se dibuja a escala, con la eslora y la manga del buque de referencia")
after(_p_ifz, [
    T("La interfaz permite además elegir el tipo de instalación. Con «Embarcación», que es el caso de este trabajo, se "
      "indican la posición del centro del buque y el rumbo, y las zonas se centran en el reactor, a popa. Con «Planta "
      "terrestre» se indican las coordenadas del reactor, no se dibuja casco y se propone un barrido de 50 a 1.200 m, "
      "el intervalo en el que se validó ARCON96. El modelo de RADTRAD y los criterios de dosis son los mismos en los "
      "dos casos, de modo que la cadena puede aplicarse a un emplazamiento en tierra sin modificarla."),
    T("La segunda pestaña es un generador de escenarios de RADTRAD, para modelos distintos de la plantilla empleada "
      "aquí. Escribe compartimentos con filtros de recirculación y deposición natural, caminos con filtro, por fuga "
      "de aire o a través de una piscina de supresión, y receptores con sus tablas de X/Q, tasas de respiración y "
      "factores de ocupación; no escribe rociadores, piscinas superpuestas ni las tablas de los caminos por tubería, y "
      "avisa si se le piden. Sus dos preajustes reproducen línea a línea la plantilla validada con RADTRAD, salvo los "
      "valores de X/Q, que la cadena sustituye en cada caso. Antes de usar un escenario, la herramienta comprueba "
      "que los dos primeros receptores están en el ambiente exterior y tienen tabla de X/Q, porque en ellos escribe "
      "el X/Q de ARCON96.")])
V("Su núcleo son dos módulos: PIPELINE.py", "Está escrita en Python.",
  "Está escrita en Python; su código no forma parte de este documento, que recoge sus ficheros de entrada "
  "(Anexo D), sus resultados (capítulo 13 y Anexo E) y su manual de uso (Anexo F).")

# ------------------------------------------------------------ Anexo F, user manual
V("Es la pestaña de cálculo (Figura", "El panel izquierdo tiene dos secciones que se activan con su interruptor; el "
  "derecho muestra el registro de la ejecución. Pasos:",
  "El panel izquierdo tiene, arriba, el tipo de instalación y, debajo, dos secciones que se activan con su "
  "interruptor; el derecho muestra el registro de la ejecución. Pasos:")
_p_met = P("Datos meteorológicos: los ficheros MET01 a MET05 de INPUT")
_new_inst = new_para_like(_p_met, "Tipo de instalación: «Embarcación (reactor a bordo)», con la latitud y la longitud "
                          "del centro del buque y el rumbo de la proa, o «Planta terrestre», con las coordenadas del "
                          "reactor. Al cambiarlo se propone el barrido de distancias de cada caso (de 10 a 400 m cada "
                          "10 m, o de 50 a 1.200 m cada 50 m). La potencia térmica indicada se escribe en todos los "
                          "escenarios de RADTRAD.", lead=True)
_p_met.addprevious(_new_inst)
V("RADTRAD: escenario (plantilla template_kpfhr.psf o el creado con el generador)",
  "escenario (plantilla template_kpfhr.psf o el creado con el generador)",
  "escenario (plantilla template_kpfhr.psf o el creado con el generador y enviado con «Usar en el cálculo»)")
V("Permite crear escenarios de RADTRAD distintos de la plantilla",
  "La pestaña «Vista previa» muestra el esquema de compartimentos y el fichero resultante.",
  "La barra superior tiene los preajustes («Embarcación» y «Planta terrestre», que cargan el modelo validado del "
  "KP-FHR, y «Vacío»), «Guardar config» y «Cargar config», que guardan y recuperan todo el contenido en un fichero "
  ".json, «Guardar PSF» y «Usar en el cálculo», que valida el escenario, lo guarda en INPUT\\PSF\\generated.psf y lo "
  "selecciona en la pestaña de cálculo. La pestaña «Vista previa» muestra el esquema de compartimentos y el fichero "
  "resultante. El generador no escribe rociadores, piscinas superpuestas ni las tablas de los caminos por tubería: "
  "si se activan, lo indica en lugar de generar el fichero. Los receptores 1 y 2 deben estar en el ambiente exterior "
  "con tabla de X/Q de usuario, porque la cadena escribe en ellos el X/Q de cada distancia.")
V("Buque: latitud, longitud y rumbo (dirección de la proa) del centro del buque, eslora, manga",
  "Buque: latitud, longitud y rumbo (dirección de la proa) del centro del buque, eslora, manga y distancia del "
  "reactor a la popa;",
  "Instalación: embarcación o planta terrestre. Para una embarcación, latitud, longitud y rumbo (dirección de la "
  "proa) del centro del buque, eslora, manga y distancia del reactor a la popa; para una planta terrestre, latitud "
  "y longitud del reactor;")
V("clic derecho: situar el centro del buque; doble clic", "situar el centro del buque", "situar el centro del buque o "
  "el reactor de la planta")
V("Salidas: «Guardar buque y criterios»", "«Guardar buque y criterios»", "«Guardar posición y criterios»")
V("Se abre sola al terminar cada ejecución (Figura", "Se abre sola al terminar cada ejecución (",
  "Se abre sola al terminar cada ejecución (la captura corresponde a una versión anterior, en la que el panel de la "
  "instalación se llamaba «Buque»; ")
V("python zonas_emergencia.py psf_batch\\postprocess regenera solo las zonas y el mapa",
  "regenera solo las zonas y el mapa", "regenera solo las zonas y el mapa (con --instalacion terrestre, para una "
  "planta en tierra)")

# new screenshots of the calculation and generator tabs (the interface has changed)
_SH = HERE.parent / "psf"
for _rid, _png in (("rId51", "fig_pipeline.png"), ("rId52", "fig_psf_preview.png")):
    _rels = (UN / "word/_rels/document.xml.rels").read_text(encoding="utf8")
    _m = _re.search(r'<Relationship [^>]*Id="%s"[^>]*>' % _rid, _rels)
    _tg = _re.search(r'Target="([^"]+)"', _m.group(0)).group(1)
    _sh.copy(_SH / _png, UN / "word" / _tg)
    for _dr in body.iter(q("drawing")):
        _x = etree.tostring(_dr, encoding="unicode")
        if 'r:embed="%s"' % _rid not in _x:
            continue
        for _e in _dr.iter():
            if _e.tag.endswith("}extent") or _e.tag.endswith("}ext"):
                if _e.get("cx") and _e.get("cy"):
                    _e.set("cy", str(int(int(_e.get("cx")) * 900 / 1400)))



# ------------------------------------------- leftovers of editing: highlight and red text
_nh = 0
for _rp in body.iter(q("rPr")):
    for _x in _rp.findall(q("highlight")):
        _rp.remove(_x); _nh += 1
    _c = _rp.find(q("color"))
    if _c is not None and _c.get(q("val")) == "FF0000" and not any(a.tag == q("tbl") for a in _rp.iterancestors()):
        _rp.remove(_c); _nh += 1
print("highlight / red removed:", _nh)

_MM = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"
# ------------------------------------------------ equations (not tracked, as in v10)
# Words inside formulas as upright text, accents as single letters, the dot of the emission rate as a
# proper accent, units with real superscripts, and display formulas in a paragraph of their own: Word
# shows them the same, and the PDF export (LibreOffice) no longer breaks them.
import unicodedata as _ud


def _mrun(text, nor=False):
    r = etree.SubElement(etree.Element("dummy"), _MM + "r")
    if nor:
        etree.SubElement(etree.SubElement(r, _MM + "rPr"), _MM + "nor")
    t = etree.SubElement(r, _MM + "t"); t.text = text
    if text != text.strip():
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    return r


_neq = 0
for _acc in list(body.iter(_MM + "acc")):                # á written as an accent over "a"
    _chr = _acc.find(_MM + "accPr/" + _MM + "chr")
    _base = "".join(t.text or "" for t in _acc.iter(_MM + "t"))
    if _chr is not None and _chr.get(_MM + "val") in ("ˊ", "´", "́") and _base == "a":
        _nx = _acc.getnext()
        if _nx is not None and _nx.tag == _MM + "r" and _nx.find(_MM + "t") is not None:
            _nx.find(_MM + "t").text = "á" + (_nx.find(_MM + "t").text or "")
            _acc.getparent().remove(_acc); _neq += 1
for _par in list(body.iter()):                          # merge plain runs that split a word at its accent
    _rs = [c for c in _par if c.tag == _MM + "r"]
    for a, b in zip(_rs, _rs[1:]):
        if a.getnext() is b and a.find(_MM + "rPr") is None and b.find(_MM + "rPr") is None \
                and a.find(_MM + "t") is not None and b.find(_MM + "t") is not None:
            b.find(_MM + "t").text = (a.find(_MM + "t").text or "") + (b.find(_MM + "t").text or "")
            _par.remove(a)
for _t in list(body.iter(_MM + "t")):
    _r = _t.getparent()
    _t.text = _ud.normalize("NFC", _t.text or "") if "̇" not in (_t.text or "") else _t.text
    _rp = _r.find(_MM + "rPr")
    _nor = _rp is not None and _rp.find(_MM + "nor") is not None
    if _nor and _re.fullmatch(r"\s*c?m3\s*", _t.text or ""):
        _t.text = _t.text.replace("m3", "m³"); _neq += 1
    if not _nor and _re.search(r"[áéíóúñ]", _t.text or ""):          # a word, not a symbol
        if _rp is None:
            _rp = etree.Element(_MM + "rPr"); _r.insert(0, _rp)
        _rp.insert(0, etree.Element(_MM + "nor")); _neq += 1
    if "Q̇" in (_t.text or ""):                                # Q with a dot above
        _parts = _t.text.split("Q̇")
        _pos = _r.getparent().index(_r)
        _new = []
        for k, part in enumerate(_parts):
            if part:
                _new.append(_mrun(part))
            if k < len(_parts) - 1:
                acc = etree.Element(_MM + "acc")
                etree.SubElement(etree.SubElement(acc, _MM + "accPr"), _MM + "chr").set(_MM + "val", "̇")
                e_ = etree.SubElement(acc, _MM + "e"); e_.append(_mrun("Q"))
                _new.append(acc)
        _parent = _r.getparent(); _parent.remove(_r)
        for k, x in enumerate(_new):
            _parent.insert(_pos + k, x)
        _neq += 1
for _ss in list(body.iter(_MM + "sSub")):               # Q + (dot)_i  ->  (Q with dot)_i ;  DC + F_x -> DCF_x
    _e = _ss.find(_MM + "e")
    _bt = "".join(t.text or "" for t in _e.iter(_MM + "t"))
    _pv = _ss.getprevious()
    if _pv is None or _pv.tag != _MM + "r" or _pv.find(_MM + "t") is None:
        continue
    _pt = _pv.find(_MM + "t")
    for _base, _tail in (("\u0307", "Q"), ("F", "DC")):
        if _bt == _base and (_pt.text or "").endswith(_tail):
            _pt.text = _pt.text[:-len(_tail)]
            if _pt.text and _pt.text != _pt.text.strip():
                _pt.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
            for _c in list(_e):
                _e.remove(_c)
            if _base == "F":
                _e.append(_mrun("DCF"))
            else:
                acc = etree.SubElement(_e, _MM + "acc")
                etree.SubElement(etree.SubElement(acc, _MM + "accPr"), _MM + "chr").set(_MM + "val", "\u0307")
                etree.SubElement(acc, _MM + "e").append(_mrun("Q"))
            if not _pt.text:
                _pv.getparent().remove(_pv)
            _neq += 1
for _t in body.iter(_MM + "t"):                         # m3 written as plain text in a unit
    _rp = _t.getparent().find(_MM + "rPr")
    if _rp is not None and _rp.find(_MM + "nor") is not None and _re.search(r"\bc?m3\b", _t.text or ""):
        _t.text = _re.sub(r"\b(c?m)3\b", "\\1³", _t.text); _neq += 1
for _p in list(body.iter(q("p"))):                      # display formula sharing a paragraph with text
    if in_fallback(_p):
        continue
    _mp = [c for c in _p if c.tag == _MM + "oMathPara"]
    _tx = [c for c in _p if c.tag == q("r") and "".join(t.text or "" for t in c.iter(q("t"))).strip()]
    if len(_mp) == 1 and _tx:
        _np = el("p", None, el("pPr", None, el("jc", {"val": "center"})))
        _first = _p.index(_mp[0]) < _p.index(_tx[0])
        _np.append(_mp[0])
        (_p.addprevious if _first else _p.addnext)(_np); _neq += 1
_t12 = next((m for m in body.iter(_MM + "oMath") if "".join(t.text or "" for t in m.iter(_MM + "t")) == "T1/2"
             and m.getparent().tag == q("p")), None)
for _m in list(body.iter(_MM + "oMath")):
    if _t12 is not None and "".join(t.text or "" for t in _m.iter(_MM + "t")) == "T12" and _m.getparent().tag == q("p"):
        _m.addprevious(copy.deepcopy(_t12)); _m.getparent().remove(_m); _neq += 1
print("equation fixes:", _neq)

# ------------------------------ Figura 15: floating picture and caption -> in line with the text
_WP = "{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}"
_pf = next((p for p in body.findall(q("p")) if any("Figura 15: Ejemplo de fichero" in "".join(t.text or "" for t in d.iter(q("t")))
                                                    for d in p.iter(_WP + "anchor"))), None)
if _pf is None:
    _FAIL13.append("Figura 15 not found")
else:
    _anc = [a for a in _pf.iter(_WP + "anchor") if not in_fallback(a)]
    _pic = next(a for a in _anc if a.find(".//{http://schemas.openxmlformats.org/drawingml/2006/picture}pic") is not None)
    _box = next(a for a in _anc if a is not _pic)
    _cap = copy.deepcopy(next(p for p in _box.iter(q("p"))))
    _ppr = _cap.find(q("pPr"))
    if _ppr is None:
        _ppr = el("pPr"); _cap.insert(0, _ppr)
    for _x in _ppr.findall(q("jc")) + _ppr.findall(q("keepNext")):
        _ppr.remove(_x)
    _ppr.append(el("keepNext")); _ppr.append(el("jc", {"val": "center"}))
    _inl = etree.Element(_WP + "inline", {"distT": "0", "distB": "0", "distL": "0", "distR": "0"})
    for _tag in ("extent", "effectExtent", "docPr", "cNvGraphicFramePr"):
        _e = _pic.find(_WP + _tag)
        if _e is not None:
            _inl.append(_e)
    _inl.append(_pic.find("{http://schemas.openxmlformats.org/drawingml/2006/main}graphic"))
    _dr = el("drawing"); _dr.append(_inl)
    _pp = el("p", None, el("pPr", None, el("jc", {"val": "center"})), el("r", None, _dr))
    _nxt = _pf.getnext()
    _pf.addnext(_pp); _pf.addnext(_cap)
    while _nxt is not None and _nxt.tag == q("p") and not "".join(t.text or "" for t in _nxt.iter(q("t"))).strip() \
            and _nxt.find(".//" + q("drawing")) is None:
        _n2 = _nxt.getnext(); body.remove(_nxt); _nxt = _n2
    body.remove(_pf)

# --------- Figura 7: picture floating beside Tabla 13, caption in a text box -> in line, before the table
_MC = "{http://schemas.openxmlformats.org/markup-compatibility/2006}"
_pa = next((p for p in body.findall(q("p")) if "A partir de este inventario isotópico de referencia" in ptext(p)), None)
_pt13 = next((p for p in body.findall(q("p")) if any("Figura 7: Sección" in "".join(t.text or "" for t in d.iter(q("t")))
                                                      for d in p.iter(_WP + "anchor"))), None)
if _pa is None or _pt13 is None:
    _FAIL13.append("Figura 7 not found")
else:
    _pic = next(a for a in _pa.iter(_WP + "anchor") if not in_fallback(a))
    _box = next(a for a in _pt13.iter(_WP + "anchor") if not in_fallback(a))
    _cap = copy.deepcopy(next(p for p in _box.iter(q("p"))))
    _ppr = _cap.find(q("pPr"))
    if _ppr is None:
        _ppr = el("pPr"); _cap.insert(0, _ppr)
    for _x in _ppr.findall(q("jc")):
        _ppr.remove(_x)
    _ppr.append(el("jc", {"val": "center"}))
    _inl = etree.Element(_WP + "inline", {"distT": "0", "distB": "0", "distL": "0", "distR": "0"})
    _ext = _pic.find(_WP + "extent")
    _k = 0.8                                              # a little smaller than beside the table
    _cx, _cy = int(int(_ext.get("cx")) * _k), int(int(_ext.get("cy")) * _k)
    _ext.set("cx", str(_cx)); _ext.set("cy", str(_cy))
    for _tag in ("extent", "effectExtent", "docPr", "cNvGraphicFramePr"):
        _e = _pic.find(_WP + _tag)
        if _e is not None:
            _inl.append(_e)
    _gr = _pic.find("{http://schemas.openxmlformats.org/drawingml/2006/main}graphic")
    for _e in _gr.iter("{http://schemas.openxmlformats.org/drawingml/2006/main}ext"):
        if _e.get("cx") and _e.getparent().tag.endswith("}xfrm"):
            _e.set("cx", str(_cx)); _e.set("cy", str(_cy))
    _inl.append(_gr)
    _dr = el("drawing"); _dr.append(_inl)
    _pp = el("p", None, el("pPr", None, el("keepNext"), el("jc", {"val": "center"})), el("r", None, _dr))
    for _a in (_pic, _box):                               # runs that held the floating objects
        _r = next((x for x in _a.iterancestors() if x.tag == q("r")), None)
        if _r is not None and _r.getparent() is not None:
            _r.getparent().remove(_r)
    _pa.addprevious(_pp); _pa.addprevious(_cap)

# --------------------------- heading numbers: room for two-digit chapters ("10.1Conceptos")
_np_ = UN / "word/numbering.xml"
_nx_ = _np_.read_text(encoding="utf8")
for _a, _b in (('<w:tab w:val="num" w:pos="432"/></w:tabs><w:ind w:left="432" w:hanging="432"/>',
                '<w:tab w:val="num" w:pos="560"/></w:tabs><w:ind w:left="560" w:hanging="560"/>'),
               ('<w:tab w:val="num" w:pos="576"/></w:tabs><w:ind w:left="576" w:hanging="576"/>',
                '<w:tab w:val="num" w:pos="740"/></w:tabs><w:ind w:left="740" w:hanging="740"/>'),
               ('<w:tab w:val="num" w:pos="1050"/></w:tabs><w:ind w:left="1050" w:hanging="720"/>',
                '<w:tab w:val="num" w:pos="1190"/></w:tabs><w:ind w:left="1190" w:hanging="860"/>')):
    if _a not in _nx_:
        _FAIL13.append("numbering level not found: " + _a[30:60])
    _nx_ = _nx_.replace(_a, _b, 1)
_np_.write_text(_nx_, encoding="utf8")

# --------------------------------------------- cross-references: fixed renumbering
def _renumber13():
    """As _renumber(), but a caption only gives its number to the bookmarks of its own paragraph, not to those of
    text boxes anchored in it (Tabla 13 had overwritten the reference to Figura 7)."""
    cnt, bm_num = {}, {}
    order = list(body.iter())
    for i, e in enumerate(order):
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
            p_ = next(a for a in e.iterancestors() if a.tag == q("p"))
            for bs in p_.iter(q("bookmarkStart")):
                own = next(a for a in bs.iterancestors() if a.tag == q("p")) is p_
                if own and bs.get(q("name")).startswith("_Ref"):
                    bm_num[bs.get(q("name"))] = "%s %d" % (kind, cnt[kind])
    for it in list(body.iter(q("instrText"))):
        m_ = _re.match(r"\s*REF (\S+)( \\h)?\s*$", it.text or "")
        if not m_ or m_.group(1) not in bm_num:
            continue
        p_ = next(a for a in it.iterancestors() if a.tag == q("p"))
        seq = list(p_.iter())
        k = seq.index(it)
        sep, done = False, False
        for x in seq[k + 1:]:
            if x.tag == q("fldChar") and x.get(q("fldCharType")) == "separate":
                sep = True
            elif x.tag == q("fldChar") and x.get(q("fldCharType")) == "end":
                break
            elif sep and x.tag == q("t"):
                x.text = "" if done else bm_num[m_.group(1)]
                done = True
    return cnt, bm_num


_cnt13, _bm13 = _renumber13()
print("captions:", _cnt13)
print("V13 FAILURES:", len(_FAIL13), *_FAIL13, sep="\n  ")
