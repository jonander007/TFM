# v11: second, deeper pass (after v10.py): consistent capitals and units, thousands separator, list of
# abbreviations, every table and figure cited in the text.
_src13 = open(HERE / "cap13.py", encoding="utf-8").read()
exec(_src13.split("# ===================================================== chapter 3 updates")[0])
exec(_src13.split("# ------------------------------------------------- renumber SEQ fields ---")[1].split("_counts = _renumber()")[0])
_bib = next(t for t in body.iter(q("tbl")) if "".join(x.text or "" for x in t.iter(q("t"))).lstrip().startswith("[1]"))
_bibp = set(_bib.iter(q("p")))


def _all_replace(pairs, skip_caption_start=False):
    n = 0
    for p in paras():
        if p in _bibp:
            continue
        for old, new in pairs:
            guard = 0
            while old in visible(p) and old in ptext(p) and guard < 20:
                guard += 1
                if skip_caption_start and visible(p).startswith(("Figura", "Tabla")) and \
                        visible(p).split(": ", 1)[-1].startswith(old):
                    break
                try:
                    RRo(p, old, new); n += 1
                except ValueError:
                    break
    return n


_n = 0
_n += _all_replace([
    ("Directriz Básica de Planificación de Protección Civil ante el Riesgo Radiológico",
     "Directriz básica de planificación de protección civil ante el riesgo radiológico"),
    ("Directriz Básica ante el Riesgo Radiológico", "Directriz básica ante el riesgo radiológico"),
    ("Directriz Básica", "Directriz básica"),
    ("en el Puerto de Bilbao", "en el puerto de Bilbao"), ("del Puerto de Bilbao", "del puerto de Bilbao"),
    ("para el Puerto de Bilbao", "para el puerto de Bilbao"),
    ("Límite de la Zona de Exclusión (EAB) y la Zona de Baja Población (LPZ)",
     "límite del área de exclusión (EAB) y la zona de baja población (LPZ)"),
    ("(Zona de Baja Población)", "(zona de baja población)"), ("(Límite del Área de Exclusión)", "(límite del área de exclusión)"),
    ("LPZ, Sala de Control)", "LPZ, sala de control)"),
    ("1000 MWth", "1.000 MWₜₕ"), ("MWth", "MWₜₕ"), ("MWe", "MWₑ"), (" MWt ", " MWₜₕ "), (" MWt/", " MWₜₕ/"),
    ("(1418 mSv", "(1.418 mSv"), ("vale 1418 mSv", "vale 1.418 mSv"), ("con 6368 Ci", "con 6.368 Ci"),
    ("1426,7", "1.426,7"), ("1435,0", "1.435,0"), ("1418,1", "1.418,1"),
    ("En el cálculo de ejemplo de Kairos, el inventario", "En el cálculo de ejemplo de Kairos Power, el inventario"),
])
print("consistency replacements:", _n)

# --------------------------------------------- abbreviations list ----
_sig = next(t for t in body.iter(q("tbl")) if _cell_text(t.find(q("tr")).find(q("tc"))) == "Sigla")
_rows = _sig.findall(q("tr"))
_NEW = [
    ("EPR-NPP", "Emergency Preparedness and Response – Nuclear Power Plant (publicación del OIEA sobre medidas de protección)"),
    ("GSR", "General Safety Requirements (requisitos generales de seguridad del OIEA)"),
    ("HT / HTO", "Tritio gaseoso / agua tritiada"),
    ("INL", "Idaho National Laboratory"),
    ("JFD", "Joint Frequency Distribution (distribución de frecuencias conjuntas de viento y estabilidad)"),
    ("MCNP", "Monte Carlo N-Particle (código de transporte de partículas)"),
    ("OPSMAN", "Defence Operations Manual (manual de operaciones de Defensa de Australia)"),
    ("PAVAN", "Código de la NRC de dispersión atmosférica para el EAB y la LPZ"),
    ("PENAR", "Plan de Emergencia Nuclear de la Armada"),
    ("SCRAM", "Parada rápida del reactor por inserción de las barras de control"),
    ("SMART", "Selection Methodology for Advanced Reactor Technologies (herramienta de selección de IDOM)"),
    ("SNAP", "Symbolic Nuclear Analysis Package (interfaz gráfica de los códigos de la NRC)"),
    ("TFM", "Trabajo Fin de Máster"),
]


def _key(s):
    return s.replace("χ", "X").upper()


for sig, txt in _NEW:
    rows = _sig.findall(q("tr"))[1:]
    model = rows[0]
    new = copy.deepcopy(model); _strip14(new)
    for tc, val in zip(new.findall(q("tc")), (sig, txt)):
        p = tc.find(q("p"))
        rpr = copy.deepcopy(p.find(".//" + q("rPr"))) if p.find(".//" + q("rPr")) is not None else None
        for x in list(p):
            if x.tag != q("pPr"):
                p.remove(x)
        ppr = p.find(q("pPr"))
        if ppr.find(q("rPr")) is None:
            ppr.append(el("rPr"))
        ppr.find(q("rPr")).insert(0, track_attrs(el("ins")))
        ins = track_attrs(el("ins")); ins.append(_mk_run(val, rpr)); p.append(ins)
    trpr = new.find(q("trPr"))
    if trpr is None:
        trpr = el("trPr"); new.insert(0, trpr)
    trpr.append(track_attrs(el("ins")))
    after_row = next((r for r in rows if _key(_cell_text(r.find(q("tc")))) > _key(sig)), None)
    if after_row is not None:
        after_row.addprevious(new)
    else:
        rows[-1].addnext(new)
_dba = next(r for r in _sig.findall(q("tr")) if _cell_text(r.find(q("tc"))) == "DBA")
for p in _dba.iter(q("p")):
    rs = [r for r in p if r.tag == q("r")]
    if rs:
        _to_del(rs)
_tp = _dba.find(q("trPr"))
if _tp is None:
    _tp = el("trPr"); _dba.insert(0, _tp)
_tp.append(track_attrs(el("del")))

# ------------------------------------- tables and figures cited in the text ----
def _bm_caption(prefix, name):
    """Bookmark 'Tabla N' / 'Figura N' of the caption starting with `prefix` (style Descripcin)."""
    cap = next(p for p in paras() if visible(p).startswith(prefix) and p.find(q("pPr") + "/" + q("pStyle")) is not None
               and p.find(q("pPr") + "/" + q("pStyle")).get(q("val")) == "Descripcin")
    _bm_id[0] += 1
    bid = str(_bm_id[0])
    fs = cap.find(q("fldSimple"))
    first = next(x for x in cap if x.tag == q("r"))
    first.addprevious(el("bookmarkStart", {"id": bid, "name": name}))
    if fs is not None:
        fs.addnext(el("bookmarkEnd", {"id": bid}))
    else:
        end = next(r for r in cap.iter(q("r")) if r.find(q("fldChar")) is not None
                   and r.find(q("fldChar")).get(q("fldCharType")) == "end")
        end.addnext(el("bookmarkEnd", {"id": bid}))


for prefix, name in (("Figura 3: Buque de referencia", "_RefFig_buqueref"), ("Tabla 9: Volumen del reactor", "_RefTab_vol"),
                     ("Tabla 10: Estimaciones de compatibilidad", "_RefTab_compvol"),
                     ("Tabla 14: Ajustes aplicados", "_RefTab_ajustes"), ("Tabla 15: Clasificación de la estabilidad", "_RefTab_estab"),
                     ("Tabla 18: Transformación de las estabilidades", "_RefTab_estabnum")):
    _bm_caption(prefix, name)


def _append(sub, text):
    p = P(sub)
    ins = track_attrs(el("ins"))
    for r_ in runs_from(text, next((r.find(q("rPr")) for r in p.iter(q("r")) if r.find(q("t")) is not None), None)):
        ins.append(r_)
    p.append(ins)


_append("El Real Decreto 524/2023, que aprueba la nueva Norma Básica",
        " La @REF:_RefTab_directriz|Tabla 1@ recoge los niveles de intervención de su Anexo IV.")
RR("En 2020 se elaboró para ARPANSA una revisión de este escenario", "que es el que se resume a continuación.",
   "que es el que se resume a continuación y en la @REF:_RefTab_arpansa|Tabla 2@.")
_append("La elección de este tipo de buque permite, además, disponer de volúmenes significativos",
        " La @REF:_RefFig_buqueref|Figura 3@ muestra el buque.")
_append("Este volumen puede considerarse representativo del espacio funcional inmediato",
        " La @REF:_RefTab_vol|Tabla 9@ resume ambos volúmenes.")
_append("En consecuencia, desde el punto de vista volumétrico, el reactor KP-FHR resulta compatible",
        " La @REF:_RefTab_compvol|Tabla 10@ resume las estimaciones.")
_append("Por otro lado, se observa que la velocidad media del viento en los datos originales",
        " La @REF:_RefTab_ajustes|Tabla 14@ resume los ajustes aplicados.")
RR("De acuerdo con esta guía, se definen siete clases de estabilidad atmosférica", "conforme a la siguiente tabla:",
   "conforme a la @REF:_RefTab_estab|Tabla 15@:")
RR("ARCON96 requiere un valor numérico para representar la clase de estabilidad", "deberá aplicarse la siguiente conversión:",
   "deberá aplicarse la conversión de la @REF:_RefTab_estabnum|Tabla 18@:")
_append("Teniendo en cuenta los 58 m, para adaptar la rosa de vientos",
        " Las Figuras 13 y 14 muestran las rosas de los vientos a 58 m de los datos de partida y de Bilbao.")

C.on_paragraph(P("Teniendo en cuenta los 58 m, para adaptar la rosa de vientos"),
               "Segunda pasada (v11): todas las tablas y figuras se citan ahora en el texto (faltaban las Tablas 1, 2, "
               "9, 10, 14, 15 y 18 y las Figuras 3 y 14); lista de siglas completada (EPR-NPP, GSR, HT/HTO, INL, JFD, "
               "MCNP, OPSMAN, PAVAN, PENAR, SCRAM, SMART, SNAP, TFM) y sin DBA, que no se usa; MWth/MWe → MWₜₕ/MWₑ; "
               "punto de miles (1.000, 1.418, 6.368); «puerto de Bilbao», «Directriz básica», «zona de baja "
               "población» en minúscula. Quedan sin año las referencias [28], [34] y [46].")
_counts = _renumber()
print("captions:", _counts)
