# v9: proofreading of the author's TFM_v8_limpia_2.docx as an examiner would, plus the layout fixes asked for
# (floating tables of chapter 10, flow chart of the end of chapter 11).
_src13 = open(HERE / "cap13.py", encoding="utf-8").read()
exec(_src13.split("# ===================================================== chapter 3 updates")[0])
exec(_src13.split("# ------------------------------------------------- renumber SEQ fields ---")[1].split("_counts = _renumber()")[0])
_V9 = HERE.parent / "v9"


def RRp(sub, old, new):
    """RR that also accepts several occurrences of `sub` (first one)."""
    return RR(sub, old, new, nth=0)


def REPLACE_PARA(sub, texts, model=None, nth=None):
    """Tracked deletion of a whole paragraph (fields included) and new paragraphs with `texts` after it."""
    p = P(sub, nth)
    m = model if model is not None else p
    news = [new_para_like(m, t) for t in texts]
    after(p, news)
    for sc in p.iter(q("sdtContent")):
        rs = [r for r in sc if r.tag == q("r")]
        if rs:
            _to_del(rs)
    delete_para(p)
    return news


# =================================================================== layout
# Floating tables of chapter 10 (Tablas 15 and 16): inline, with the caption above as in the rest of the memoria
for key in ("Extremadamente inestable", "2023-01-01 00:10:00"):
    tbl = next(t for t in body.iter(q("tbl")) if key in "".join(x.text or "" for x in t.iter(q("t"))))
    tpp = tbl.find(q("tblPr")).find(q("tblpPr"))
    if tpp is not None:
        tpp.getparent().remove(tpp)
    cap = tbl.getnext()
    if cap is not None and cap.tag == q("p") and ptext(cap).startswith("Tabla"):
        tbl.addprevious(cap)                        # caption before the table (moved, not retyped)
        ppr = cap.find(q("pPr"))
        if ppr.find(q("keepNext")) is None:
            ppr.insert(1, el("keepNext"))
    for tr in tbl.findall(q("tr"))[:-1]:            # keep the table on one page
        for p_ in tr.iter(q("p")):
            ppr = p_.find(q("pPr"))
            if ppr is None:
                ppr = el("pPr"); p_.insert(0, ppr)
            if ppr.find(q("keepNext")) is None:
                ppr.insert(0, el("keepNext"))
C.on_paragraph(P("Clasificación de la estabilidad atmosférica", style="Descripcin"),
               "Tablas 15 y 16: eran tablas flotantes (posición fija en la página), con el texto alrededor; ahora van en "
               "línea, con la leyenda encima como el resto de tablas y sin partirse entre páginas.")

# Flow chart at the end of chapter 11: redrawn (typos fixed, any zone, not only EAB/LPZ) and moved to 7.1
_old_fig = [p for p in paras() if p.find(".//" + q("drawing")) is not None
            and p.getnext() is not None and ptext(p.getnext()).strip() == ""
            and p.getprevious() is not None and "La plantilla conserva la sala de control" in ptext(p.getprevious())][0]
delete_para(_old_fig)
_eq_rz = P("A partir de la curva TEDE(d), el radio de cada zona").getnext()      # equation paragraph R_Z
after(_eq_rz, [
    T("La " + REF("_RefFig_flujo", "Figura 6") + " representa esta búsqueda: para cada zona se ajusta la distancia "
      "hasta que la dosis iguala su límite. La herramienta del capítulo @REFN:_RefCap_herr|12@ no itera: calcula la "
      "dosis en un barrido de distancias y obtiene el radio interpolando entre las dos distancias que encierran el "
      "límite, lo que equivale a la búsqueda del diagrama para todas las zonas a la vez."),
    FIG(_V9 / "fig" / "flujo_radio.png", 12.5, "Diagrama de flujo de la determinación del radio de una zona: término "
        "fuente, χ/Q con ARCON96, RADTRAD, dosis y comparación con el límite; si la dosis queda por debajo se reduce "
        "la distancia y si lo supera se aumenta, hasta igualarlo."),
    CAP("Figura", "Determinación del radio de cada zona de emergencia", "_RefFig_flujo"),
])
C.on_paragraph(P("representa esta búsqueda: para cada zona se ajusta la distancia"),
               "Diagrama trasladado desde el final del capítulo 11, donde estaba sin leyenda ni referencia en el texto. "
               "Redibujado con las tildes corregidas (ATMOSFÉRICO, MÚLTIPLES, ESTÁ, LÍMITE) y generalizado a cualquier "
               "zona, no solo al EAB y la LPZ; se aclara que la herramienta lo resuelve con un barrido de distancias.")

# ================================================================ abstract
RRp("Los radios del límite del área de exclusión (EAB) y de la zona de baja población (LPZ) se obtienen",
    "Los radios del límite del área de exclusión (EAB) y de la zona de baja población (LPZ) se obtienen comparando la "
    "dosis efectiva con los criterios de 250 mSv en las peores 2 horas y en 30 días, respectivamente.",
    "Los radios del límite del área de exclusión (EAB) y de la zona de baja población (LPZ) se obtienen comparando la "
    "dosis efectiva con los criterios de 250 mSv en las peores 2 horas y en 30 días, respectivamente, y los de las "
    "zonas de medidas urgentes, con los niveles de la Directriz básica de protección civil ante el riesgo radiológico.")
RRp("The exclusion area boundary (EAB) and low population zone (LPZ) radii are obtained",
    "for the worst 2 hours and for 30 days.",
    "for the worst 2 hours and for 30 days, and the urgent protective action zones with the levels of the Spanish "
    "radiological emergency guideline.")
RRp("Bazterketa-eremuaren mugaren (EAB) eta biztanleria urriko eremuaren (LPZ) erradioak",
    "2 ordu txarrenetan eta 30 egunetan, hurrenez hurren.",
    "2 ordu txarrenetan eta 30 egunetan, hurrenez hurren, eta berehalako neurrien eremuenak, arrisku "
    "erradiologikoaren aurreko Oinarrizko Zuzentarauaren mailekin.")

# ============================================================ chapters 1–2
RR("Los SMR están diseñados bajo un enfoque modular", "mediante la adición de múltiples unidades en configuración serie",
   "mediante la adición de varias unidades")
RR("Los SMR están diseñados bajo un enfoque modular", "plazos y costos asociados", "plazos y costes asociados")
RR("Desde una perspectiva normativa y de seguridad, los SMR incorporan", "Estos dispositivos", "Estos sistemas")
RR("Entre los usos alternativos actualmente en estudio", "grandes data centers (centros de datos)", "grandes centros de datos")
RR("En el presente trabajo se abordará la propuesta y validación", "la propuesta y validación de una metodología",
   "la propuesta y aplicación de una metodología")
RR("En el presente trabajo se abordará la propuesta y aplicación", "seguridad nuclear, y la viabilidad de establecer "
   "corredores marítimos seguros en el contexto de operaciones regulares.",
   "seguridad nuclear, y las condiciones en que el buque podría hacer escala; la navegación por la ría y la "
   "aproximación al puerto quedan fuera de su alcance.")
RR("Con el fin de establecer dichas zonas de protección radiológica, se planteará",
   "un evento con daño al núcleo del reactor, que derive en la liberación de radionucleidos al medio ambiente",
   "un accidente base de diseño que derive en la liberación de radionucleidos al medio ambiente")
RR("Adicionalmente, se considerará el contexto climatológico e histórico", "el contexto climatológico e histórico de la "
   "zona portuaria de Bilbao", "la meteorología de la zona portuaria de Bilbao")
RR("Adicionalmente, se considerará la meteorología", "estimar las dosis absorbidas por receptores",
   "estimar las dosis que recibirían receptores")
RR("OE6. Obtener los radios del EAB y de la LPZ", "Obtener los radios del EAB y de la LPZ para el puerto de Bilbao",
   "Obtener los radios de las zonas de emergencia (EAB, LPZ y zonas de medidas urgentes) para el puerto de Bilbao")

# ================================================================ chapter 3
RR("A falta de caracterización radiológica, la Directriz fija por defecto",
   "Estas distancias genéricas están pensadas para fuentes radiactivas y no son representativas de un reactor de "
   "320 MWth. Precisamente por eso es necesario un análisis específico como el de este trabajo.",
   "Estas distancias genéricas están pensadas para fuentes radiactivas y no proceden de una caracterización del "
   "reactor; por eso es necesario un análisis específico como el de este trabajo, que el capítulo 13 compara con "
   "ellas.")
RR("El documento EPR-NPP Public Protective Actions (2013) sugiere tamaños de zona",
   "Para el intervalo de 100 a 1000 MWth, en el que se encuadra el KP-FHR, las distancias",
   "Para el intervalo de 100 a 1000 MWth, en el que se encuadra el KP-FHR, la PAZ se reduce a 0,5–3 km, la UPZ a "
   "5–15 km y las distancias")
for _ in range(2):
    RRp("Condicionamiento de evaluación", "Condicionamiento de evaluación", "Criterio de evaluación")
RR("Las evaluaciones de dosis en EAB y LPZ se utilizan para validar",
   "incluso en un accidente severo, no se excedan", "incluso en el accidente base de diseño más desfavorable, no se excedan")
_p221 = P(", los resultados del trabajo deben leerse así:")
_ins = track_attrs(el("ins")); _ins.append(_mk_run("A la vista de la "))
_ppr = _p221.find(q("pPr")); (_ppr.addnext(_ins) if _ppr is not None else _p221.insert(0, _ins))
RR(", los resultados del trabajo deben leerse así:", "deben leerse así:", "se leen así:")
RR("Como análisis de sensibilidad, se repite el cálculo de dosis",
   "(F, 1 m/s durante 12 h, emisión a nivel del mar)",
   "(clase F y 1 m/s, aplicada a todas las horas, con emisión a nivel del mar)")
RR("A partir de los referentes anteriores, se propone que las conclusiones",
   "a validar con los resultados numéricos:", "que el capítulo 14 contrasta con los resultados numéricos:")
RR("Comprobación de diseño (EAB)", "Comprobación de diseño (EAB)", "Comprobación de diseño (EAB y LPZ)")
_c = [p for p in paras() if ptext(p).strip() == "Peores 2 h" and p.getparent().tag == q("tc")
      and "Comprobación de diseño" in "".join(x.text or "" for x in p.getparent().getparent().iter(q("t")))][0]
_t_ = _isolate(_c, "Peores 2 h"); _d = _to_del(_t_); _i = track_attrs(el("ins"))
_i.append(_mk_run("Peores 2 h (EAB); 30 días (LPZ)", _t_[0].find(q("rPr")))); _d.addnext(_i)
C.on_paragraph(P("Comprobación de diseño (EAB y LPZ)"),
               "La Tabla 4 solo recogía el EAB, pero el trabajo calcula también la LPZ (capítulos 7, 12 y 13).")

# ============================================================ chapters 4–5
RR("En este apartado se aborda el proceso de selección del reactor", "En este apartado", "En este capítulo")
RR("Como resultado de este filtrado progresivo", "las cuales se presentan en la sección",
   "las cuales se presentan en el capítulo")
RR("En la siguiente sección se procederá a describir", "En la siguiente sección se procederá a describir",
   "En el capítulo siguiente se describen")
RR("Para llevar a cabo la comparación entre los reactores que han superado", "establecida por el usuario",
   "establecida por el autor")
for sub in ("documentos regulatorios asociados al reactor de demostración HERMES",
            "documentación regulatoria asociada al reactor de demostración HERMES",
            "cuyo elemento central es el reactor de demostración HERMES"):
    RR(sub, "HERMES", "Hermes")
RRp("HERMES (reactor demostrador)", "HERMES", "Hermes")
# AHP criteria list: subcriteria one level below their criterion
_crit = {"Características del núcleo del reactor", "Características del sistema del reactor",
         "Características del ciclo de combustible", "Desmantelamiento y gestión de residuos",
         "Estado del licenciamiento", "Consideraciones políticas y sociales", "Retos operativos marítimos"}
_p0 = P("Siguiendo la estructura de criterios de la herramienta SMART")
_x = _p0.getnext()
while _x is not None and _x.find(q("pPr") + "/" + q("numPr")) is not None:
    if ptext(_x).strip() not in _crit:
        _x.find(q("pPr") + "/" + q("numPr")).find(q("ilvl")).set(q("val"), "1")
    _x = _x.getnext()

# ================================================================ chapter 6
RR("De acuerdo con la documentación técnica del buque, la potencia propulsiva", "515 °C. ", "515 °C ")
RR("De acuerdo con la documentación técnica del buque, la potencia propulsiva", " El caudal total", ". El caudal total")
RR("La demanda energética total del buque, considerando de forma conjunta",
   "Este valor representa la potencia térmica mínima que debe ser suministrada por cualquier sistema alternativo",
   "Este valor representa la potencia térmica que debe poder suministrar cualquier sistema alternativo")
RR("Buque de referencia LNG Castillo de Villalba [6]", " [6]", "@CITE:Emp03|32@", nth=1)
RR("Buque de referencia LNG Castillo de Villalba [6]", "Villalba [6]", "Villalba [32]", nth=0)   # list of figures

# ================================================================ chapter 8
RR("El accidente se inicia con la pérdida completa del suministro eléctrico alterno", "suministro eléctrico alterno",
   "suministro eléctrico de corriente alterna")
RR("Este sistema actúa de forma automática, sin necesidad de alimentación eléctrica",
   "intervención del operadory transfiere", "intervención del operador, y transfiere")
RR("El impacto radiológico del accidente se evalúa en términos de dosis efectiva total equivalente",
   "zona de baja densidad de población", "zona de baja población")
RR("El impacto radiológico del accidente se evalúa en términos de dosis efectiva total equivalente",
   "y la contribución de cada nucleido se analiza con los resultados.",
   "y el capítulo 13 confirma que también aquí la dosis la produce casi por completo el tritio.")
RR("E1, accidente base de diseño. Pérdida total de suministro eléctrico",
   "Se emplea para comprobar el diseño frente a los criterios de emplazamiento (250 mSv en el EAB y en la LPZ) y para "
   "dimensionar la zona de planificación.",
   "Se emplea para comprobar el diseño frente a los criterios de emplazamiento (250 mSv en el EAB y en la LPZ) y, "
   "junto con E2, para las zonas de confinamiento, profilaxis con yodo y planificación.")
RR("E2, escenario envolvente. Mismo término fuente que E1",
   "Se emplea para dimensionar las zonas de medidas urgentes (evacuación y confinamiento).",
   "Se emplea para dimensionar la evacuación y comprobar la ausencia de efectos deterministas y, junto con E1, para "
   "las zonas de confinamiento, profilaxis con yodo y planificación (Tabla 4).")
RR("Los dos escenarios se calculan con la herramienta del capítulo 12",
   "cabe esperar que las dosis de E2 sean muy próximas a las de E1.",
   "cabe esperar que las dosis de E2 sean muy próximas a las de E1, como confirma el capítulo 13 (un 0,23 % "
   "mayores).")

# ================================================================ chapter 9
RR("Isotopo", "Isotopo", "Isótopo", nth=0)
RR("Isotopo", "Isotopo", "Isótopo", nth=0)
for _ in range(2):
    RRp("[atom/b/cm]", "[atom/b/cm]", "[átomos/(b·cm)]")
RR("A partir de el periodo de semidesintegración", "A partir de el periodo", "A partir del periodo")
RR("En la Figura 7 se recogen los factores de atenuación (AF)", "(combustible /partícula", "(combustible/partícula")
RR("Los factores de atenuación se proporcionan en la literatura para distintos niveles", "estimación de el término fuente",
   "estimación del término fuente")

# =============================================================== chapter 10
RR("Para tal fin, se empleará un software de simulación debidamente validado", "aceptado por la comisión reguladora",
   "aceptado por la NRC")
RR("En este contexto, el parámetro χ/Q (chi sobre Q)", "antes de alcanzar un punto receptor.",
   "antes de alcanzar un punto receptor")
track_append(P("En este contexto, el parámetro χ/Q (chi sobre Q)"), [_mk_run(".")])
RR("ARCON96 fue desarrollado por la NRC en la década de los 90", "en la década de los 90", "en la década de 1990")
RR("ARCON96 fue desarrollado por la NRC en la década de 1990", "en la dispersión atmosférica.  ",
   "en la dispersión atmosférica ")
track_append(P("ARCON96 fue desarrollado por la NRC en la década de 1990"), [_mk_run(".")])
RR("Este enfoque asegura que el valor obtenido represente una condición meteorológica",
   "condiciones accidentales de corto alcance", "condiciones accidentales de corto alcance.")
RR("Una vez definidos los recursos a emplear, se procederá al desarrollo",
   "Una vez definidos los recursos a emplear, se procederá al desarrollo de la metodología específica. Para ello, se "
   "seleccionarán los datos meteorológicos de partida, los cuales serán procesados conforme a los requerimientos del "
   "modelo ARCON96, con el fin de generar los archivos de entrada en el formato exigido por el software. A "
   "continuación, se ejecutará el modelo y se llevará a cabo un análisis crítico de los archivos de salida obtenidos.",
   "Definidos los recursos, se desarrolla la metodología específica: se seleccionan los datos meteorológicos de "
   "partida, se procesan conforme a los requisitos de ARCON96 para generar los ficheros de entrada en el formato que "
   "exige el programa, se ejecuta el modelo y se analizan críticamente sus salidas.")
RR("Dada esta limitación, se requiere aplicar un tratamiento estadístico",
   "así como la velocidad media del viento y la temperatura media, y posteriormente realizar un ajuste de estos "
   "parámetros", "así como la velocidad media del viento, y posteriormente ajustar estos parámetros")
RR("Teniendo en cuenta los 58 m, para adaptar la rosa de vientos", "en sentido antihoraria", "en sentido antihorario")
RR("De acuerdo con esta guía, se definen siete clases de estabilidad atmosférica", "de la A a la G en función",
   "de la A a la G, en función")
RR("Tabla de ajustes aplicados", "Tabla de ajustes aplicados", "Ajustes aplicados a los datos meteorológicos", nth=1)
RR("Habiendo realizado los cambios descritos se obtiene una tabla",
   "No obstante, en base a los requisitos establecidos por la herramienta Arcon96, para la que",
   "No obstante, según los requisitos de ARCON96, para el que")
RR("Habiendo realizado los cambios descritos se obtiene una tabla",
   "al contener registros únicamente para un único año", "al contener un único año de registros")
RR("Sin embargo, considerando que la serie de datos disponible posee una resolución temporal",
   "(i.e., seis registros por hora)", "(es decir, seis registros por hora)")
RR("Sin embargo, considerando que la serie de datos disponible posee una resolución temporal",
   "tal como lo requiere Arcon96", "tal como lo requiere ARCON96")
RR("Esta metodología permite construir una serie de 5 años sintéticos", "requerimientos de entrada de Arcon96",
   "requisitos de entrada de ARCON96")
RRp("Estabilidad atmósferica", "atmósferica", "atmosférica")
RR("Los programas de monitoreo meteorológico deben incluir", "monitoreo", "vigilancia")

# =============================================================== chapter 11
REPLACE_PARA("Este capítulo tiene como finalidad integrar todo lo previamente analizado", [
    "Este capítulo integra lo analizado en los anteriores para calcular las zonas de exclusión: con la actividad "
    "liberada al ambiente (capítulo @REFN:_RefCap_lib|9@) y la dispersión atmosférica (capítulo "
    "@REFN:_RefCap_disp|10@), se calcula la dosis en función de la distancia y se aplican los criterios de dosis del "
    "capítulo @REFN:_RefCap_marco|3@ con un código especializado en el cálculo de dosis, dentro de una metodología que "
    "integra todos los factores y puede replicarse en otros escenarios similares."])
RR("En la sección previa se ha constatado que para evaluar las distintas zonas",
   "En la sección previa se ha constatado que para evaluar las distintas zonas de emergencia es crucial calcular la "
   "dosis efectiva en cada punto, previo a la comparación de los valores a los obtenidos en la normativa. Para ello, se "
   "utilizará el software “RADTRAD” cuya función y requerimientos se detallan a continuación:",
   "Para evaluar las zonas de emergencia es necesario calcular la dosis efectiva en cada punto antes de compararla "
   "con los criterios de la normativa. Para ello se utiliza RADTRAD, cuya función y requisitos se detallan a "
   "continuación.")
RR("(RADionuclide Transport, Removal And Dose Estimation) es un código",
   "durante accidentes de diseño, como LOCA y otros eventos severos.",
   "durante accidentes base de diseño, como el LOCA.")
RR("Como se ha mencionado anteriormente una de las limitaciones del RADTRAD",
   "Como se ha mencionado anteriormente una de las limitaciones del RADTRAD es la necesidad de proporcionarle una serie "
   "de datos de entrada muy amplio y concreto a fin de definir inequívocamente el entorno. Por tanto, se muestra a "
   "continuación de manera esquemática la apariencia y características de la plantilla que se ha confeccionado como "
   "input para la ejecución del software.",
   "Como se ha mencionado, una de las limitaciones de RADTRAD es que necesita un conjunto muy amplio y concreto de "
   "datos de entrada para definir el escenario sin ambigüedad. Por ello se muestra a continuación, de forma "
   "esquemática, la estructura de la plantilla que se ha confeccionado como entrada del programa.")
RR("Nivel de potencia térmica de la planta (MWt)", "(MWt)", "(MWₜₕ)")
for sub in ("Modelo de X/Q (dispersión atmosférica)", "Tiempos y valores de X/Q"):
    RR(sub, "X/Q", "χ/Q")
RR("El fichero de factores de dosis de RADTRAD contiene 60 nucleidos",
   "los 22 del inventario que no están en él se excluyen del .nif. Además,",
   "los 22 del inventario que no están en él se excluyen del .nif. Suman unos 2 Ci, el 0,03 % de la actividad "
   "liberada, y casi todo corresponde al Xe-138, el Xe-135m y el Xe-133m, gases nobles que solo contribuyen por "
   "irradiación externa desde la nube; el Xe-135m procedente del I-135 ya está incluido en los factores de este "
   "último. Además,")
RR("El fichero de factores de dosis de RADTRAD contiene 60 nucleidos",
   " Suman unos 2 Ci, el 0,03 % de la actividad liberada, y casi todo corresponde al Xe-138, el Xe-135m y el Xe-133m, "
   "gases nobles que solo contribuyen por irradiación externa desde la nube. El Xe-135m procedente del I-135 ya está "
   "incluido en los factores de este último.", "")

# =============================================================== chapter 12
RR("Para cada distancia del barrido se ejecutan un caso independiente de la dirección",
   "en dos bloques, cada uno con su propia columna de χ/Q, y la herramienta identifica la columna de cada periodo a "
   "partir de la cabecera del propio fichero, para no confundir unos periodos con otros.",
   "en dos bloques. Como el rango de χ/Q es propio de cada periodo y el fichero solo imprime la escala de uno, la "
   "herramienta reconstruye la escala de cada periodo con los límites del fichero de registro de ARCON96 y comprueba "
   "que el percentil 95 que obtiene coincide con el que calcula el propio código (apartado de verificación).")
REPLACE_PARA("Si la dosis no supera el criterio en ninguna distancia, el radio se informa", [
    "Si la dosis no supera el criterio en ninguna distancia, el radio se informa como menor o igual que la distancia "
    "mínima calculada; si lo supera en la máxima, la herramienta lo advierte para que se amplíe el barrido. Las zonas "
    "se representan como circunferencias centradas en el reactor, situado a popa en la zona de máquinas (por defecto, "
    "a 28 m de la popa, en el centro de los 30–35 m de esa zona), con el radio de la distancia más desfavorable: es "
    "una representación conservadora, porque el χ/Q de diseño ya es el del peor sector.",
    "El mapa se genera como página web con Leaflet sobre cartografía de OpenStreetMap, con el buque orientado según "
    "su rumbo y una ventana con el radio, el criterio y el juego de fracciones que lo determina; en ella pueden "
    "elegirse las zonas que se dibujan y modificarse cada criterio. Sin conexión a internet la página dibuja un "
    "esquema equivalente sin fondo cartográfico, y se genera además una imagen estática para informes.",
    "La interfaz gráfica de la herramienta integra el mapa en una pestaña propia, «Mapa de zonas», que carga los "
    "resultados de cada ejecución (caso base, con E1 y E2, y caso de sensibilidad meteorológica), muestra los radios y "
    "dibuja el buque, el reactor y las zonas sobre la cartografía de OpenStreetMap o la imagen de satélite, con las "
    "coordenadas del cursor y una cuadrícula de latitud y longitud; en ella pueden cambiarse los criterios y la "
    "posición, el rumbo y las dimensiones del buque, y abrirse el mapa completo en el navegador.",
    "El buque se dibuja a escala, con la eslora y la manga del buque de referencia del capítulo "
    "@REFN:_RefCap_buque|6@ (284,4 × 42,5 m), y por defecto aparece atracado en el pantalán de metaneros de la "
    "terminal de GNL de Bahía de Bizkaia Gas, en Punta Ceballos (Zierbena). La posición, el rumbo y las dimensiones "
    "pueden cambiarse al lanzar el cálculo o en el propio visor.",
])

# ========================================================== chapters 13–14
RRp("muestra el χ/Q de diseño frente a la distancia al reactor para los intervalos de la RG 1.145", "RG 1.145 ", "RG 1.145")
RRp("El cálculo de ejemplo de Kairos Power da 7,2 mSv a 335 m", "por tritio ", "por tritio")
RRp("intervención del operador, y transfiere", "a ella ", "a ella")
RRp("y no se acreditan filtros", "acreditan filtros ", "acreditan filtros")

# ================================================================= annexes
RRp("X/Q(t₁→t₂) = (t₂·X/Q(0→t₂) − t₁·X/Q(0→t₁)) / (t₂ − t₁)",
    "X/Q(t₁→t₂) = (t₂·X/Q(0→t₂) − t₁·X/Q(0→t₁)) / (t₂ − t₁)",
    "χ/Q(t₁→t₂) = (t₂·χ/Q(0→t₂) − t₁·χ/Q(0→t₁)) / (t₂ − t₁)")

# ============================================================== references
# "et al." stored as an author without first name gave "y . et al.": authors as literal text
_src_xml = UN / "customXml/item1.xml"
_sx = _src_xml.read_text(encoding="utf-8")
for _tag, _txt in (("ENDF8", "D. A. Brown, M. B. Chadwick, R. Capote et al."),
                   ("DTU", "N. N. Davis, J. Badger, A. N. Hahmann et al."),
                   ("RADTRAD", "S. L. Humphreys et al.")):
    _sx = _re.sub(r"(<b:Tag>%s</b:Tag>.*?<b:Author><b:Author>)<b:NameList>.*?</b:NameList>" % _tag,
                  lambda m: m.group(1) + "<b:Corporate>%s</b:Corporate>" % _txt, _sx, count=1, flags=_re.S)
_src_xml.write_text(_sx, encoding="utf-8")
for _sub in ("ENDF/B-VIII.0: The 8th Major Release", "The Global Wind Atlas", "RADTRAD: A Simplified Model"):
    _p = [p for p in paras() if _sub in ptext(p) and " y . et al." in ptext(p)]
    if _p:
        RR(_sub, " y . et al.", " et al.", nth=0)
    else:
        _p = [p for p in paras() if _sub in ptext(p) and ". et al." in ptext(p)]
        if _p:
            WARN.append("et al. format in %s: %r" % (_sub, ptext(_p[0])[:80]))

C.on_paragraph(P("Este trabajo propone y aplica una metodología para delimitar"),
               "Versión 9: revisión integral como corrector del tribunal sobre TFM_v8_limpia_2. Erratas y tildes, "
               "coherencia con los resultados (alcance de la Tabla 4, escenarios, objetivos y resumen), referencias "
               "(Figura 3 citaba la [6] en lugar de la [32]; «y . et al.» en la bibliografía), tablas flotantes del "
               "capítulo 10 y diagrama de flujo, trasladado al capítulo 7.")

_counts = _renumber()
print("captions:", _counts)
