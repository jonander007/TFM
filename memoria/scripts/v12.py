# v12: external technical review (Revision_y_prompt_TFM.md) applied after v10.py and v11.py.
# P0 dosimetry and criteria, P1 methodology/results/conclusions, P2 wording.

_FAIL = []


def _soft(fn):
    def w(*a, **k):
        try:
            return fn(*a, **k)
        except (SystemExit, Exception) as e:
            _FAIL.append("%s%r: %s" % (fn.__name__, a[:2], e))
    w.__name__ = fn.__name__
    return w


def RRp(sub, old, new):
    p = next((p for p in paras() if sub in visible(p) and old in visible(p) and p not in _bibp), None)
    if p is None:
        raise SystemExit("RRp not found")
    RRo(p, old, new)
    return p


RR = _soft(RR); RRp = _soft(RRp); _append = _soft(_append)


def _cell(h0, r0, col):
    """First paragraph of the cell `col` of the row whose first cell is `r0`, in the table whose header starts with `h0`."""
    for tbl in body.iter(q("tbl")):
        rows = tbl.findall(q("tr"))
        if not rows or _cell_text(rows[0].find(q("tc"))) != h0:
            continue
        for tr in rows[1:]:
            tcs = tr.findall(q("tc"))
            if tcs and "".join(visible(p) for p in tcs[0].findall(q("p"))).strip() == r0:
                return tcs[col].find(q("p"))
    raise SystemExit("cell not found: %s / %s" % (h0, r0))


@_soft
def SETC(h0, r0, col, new):
    p = _cell(h0, r0, col)
    RRo(p, visible(p).strip(), new)


def REPLACE_PARA(sub, texts, model=None):
    p = P(sub)
    news = [new_para_like(model if model is not None else p, t) for t in texts]
    after(p, news)
    for sc in p.iter(q("sdtContent")):
        rs = [r for r in sc if r.tag == q("r")]
        if rs:
            _to_del(rs)
    delete_para(p)
    return news



# ============================================================ P0 · abstract
RR("La dosis la domina la inhalación del tritio, el 99 % de la TEDE",
   "Las zonas quedan dentro del ámbito del atraque y muy por debajo de las distancias genéricas de la Directriz básica "
   "(100 y 200 m), que resultan conservadoras para este diseño.",
   "En el escenario y con las hipótesis analizadas —meteorología sintética derivada de un solo año e inventario de "
   "tritio del ejemplo de Kairos Power—, las zonas quedan en el entorno inmediato del buque y por debajo de las "
   "distancias genéricas que la Directriz básica fija para un foco sin caracterizar (radio de 100 m y corona de alerta "
   "hasta 200 m), con las que solo cabe una comparación geométrica.")
RR("The dose is dominated by tritium inhalation, 99 % of the TEDE",
   "The zones remain within the berth area and well below the generic distances of the Spanish radiological emergency "
   "guideline (100 m and 200 m), which are therefore conservative for this design.",
   "For the scenario and assumptions analysed —synthetic meteorology derived from a single year and the tritium "
   "inventory of the Kairos Power example— the zones remain in the immediate surroundings of the ship and below the "
   "generic distances that the Spanish guideline sets for an uncharacterised source (a 100 m radius and an alert ring "
   "up to 200 m), which allow only a geometric comparison.")
RR("Dosia tritioaren arnasketak menderatzen du, TEDEaren % 99",
   "Eremuak atrakalekuaren barruan geratzen dira, Oinarrizko Zuzentarauaren distantzia generikoen (100 eta 200 m) "
   "azpitik; horiek, beraz, kontserbadoreak dira diseinu honetarako.",
   "Aztertutako eszenatoki eta hipotesiekin —urte bakar batetik eratorritako meteorologia sintetikoa eta Kairos "
   "Powerren adibideko tritio-inbentarioa—, eremuak ontziaren inguru hurbilean geratzen dira, Oinarrizko "
   "Zuzentarauak karakterizatu gabeko iturri baterako ezartzen dituen distantzia generikoen azpitik (100 m-ko "
   "erradioa eta 200 m-rainoko alerta-koroa); horiekin konparazio geometrikoa baino ezin da egin.")
RR("Se ha desarrollado una herramienta software que ejecuta toda la cadena", "herramienta software", "herramienta informática")

# ======================================================= P0 · chapter 3
RR("Estos criterios proceden de la NUREG-0396", "200 rem (2 Gy) a cuerpo entero", "200 rem a cuerpo entero")
RR("Los criterios de emplazamiento, 250 mSv (25 rem) TEDE en las peores 2 horas",
   "250 mSv (25 rem) TEDE en las peores 2 horas en el límite del área de exclusión y durante 30 días en la zona de baja "
   "población,",
   "250 mSv (25 rem) TEDE en cualquier periodo de 2 horas tras el inicio de la liberación en el límite del área de "
   "exclusión y durante todo el paso de la nube en el límite exterior de la zona de baja población,")
_append("Los criterios de emplazamiento, 250 mSv (25 rem) TEDE en cualquier periodo",
        " El mismo criterio figura en 10 CFR 50.67 para las centrales en operación que adoptan el término fuente "
        "alternativo, y 10 CFR 100.11 conserva la formulación original en dosis a cuerpo entero y a tiroides. Los "
        "30 días son el horizonte de cálculo adoptado, que en este modelo contiene el paso de la nube porque la "
        "emisión termina a las 2 horas. La aplicación de estos criterios terrestres a un buque atracado es una "
        "referencia metodológica, no un requisito.")
_append("A falta de caracterización radiológica, la Directriz fija por defecto",
        " Esas zonas se definen por tasa de dosis (5 mSv/h y 100 µSv/h) y no por dosis integrada, de modo que con "
        "los radios calculados solo admiten una comparación geométrica.")
SETC("Referente", "Directriz española (genérica)", 2, "100 m (radio genérico de la zona de medidas urgentes)")
SETC("Referente", "Directriz española (genérica)", 3, "100–200 m (corona de la zona de alerta)")
SETC("Referente", "Directriz española (genérica)", 4, "Foco en espacio abierto sin caracterización; criterios de tasa "
     "de dosis (5 mSv/h y 100 µSv/h)")
# Table 4: four families of criteria
SETC("Zona / comprobación", "Comprobación de diseño (EAB y LPZ)", 1, "TEDE ≤ 250 mSv (25 rem)")
SETC("Zona / comprobación", "Comprobación de diseño (EAB y LPZ)", 2, "Cualquier ventana de 2 h tras el inicio de la "
     "liberación (EAB); paso de la nube, con 30 días como horizonte de cálculo (LPZ)")
SETC("Zona / comprobación", "Comprobación de diseño (EAB y LPZ)", 0, "Emplazamiento (NRC): EAB y LPZ")
SETC("Zona / comprobación", "Zona de medidas urgentes: evacuación", 1, "Dosis efectiva evitable ≥ 50 mSv (cribada con la "
     "TEDE proyectada)")
SETC("Zona / comprobación", "Zona de medidas urgentes: evacuación", 2, "Hasta 1 semana (7 días)")
SETC("Zona / comprobación", "Zona de medidas urgentes: evacuación", 0, "Intervención (Directriz): evacuación")
SETC("Zona / comprobación", "Zona de medidas urgentes: confinamiento", 1, "Dosis efectiva evitable ≥ 10 mSv (cribada con "
     "la TEDE proyectada)")
SETC("Zona / comprobación", "Zona de medidas urgentes: confinamiento", 2, "Hasta 2 días (48 h)")
SETC("Zona / comprobación", "Zona de medidas urgentes: confinamiento", 0, "Intervención (Directriz): confinamiento")
SETC("Zona / comprobación", "Profilaxis con yodo", 1, "Dosis equivalente evitable a tiroides ≥ 100 mSv (dosis proyectada)")
SETC("Zona / comprobación", "Profilaxis con yodo", 2, "7 días (hipótesis del trabajo)")
SETC("Zona / comprobación", "Profilaxis con yodo", 0, "Intervención (Directriz): profilaxis con yodo")
SETC("Zona / comprobación", "Zona de planificación de emergencias", 3, "E1 y E2")
SETC("Zona / comprobación", "Zona de planificación de emergencias", 0, "Planificación (NRC, referencia metodológica): "
     "contorno de 10 mSv en 96 h")
SETC("Zona / comprobación", "Ausencia de efectos deterministas", 1, "1 Gy en médula ósea; 5 Gy en tiroides (dosis "
     "absorbida proyectada)")
SETC("Zona / comprobación", "Ausencia de efectos deterministas", 2, "Menos de 2 días")
SETC("Zona / comprobación", "Ausencia de efectos deterministas", 3, "No calculada; acotada (capítulo 13)")
SETC("Zona / comprobación", "Ausencia de efectos deterministas", 0, "Dosis absorbida por órgano (umbrales agudos)")
_append("Los niveles españoles se expresan como dosis evitable. Compararlos con la dosis proyectada",
        " Las vías incluidas son la inhalación durante el paso de la nube y la inmersión en ella; no se incluyen la "
        "irradiación desde el suelo contaminado, la ingestión ni la vía marina. La TEDE se usa como aproximación a la "
        "dosis efectiva para cribar los niveles de dosis efectiva evitable; los umbrales de efectos deterministas se "
        "expresan en dosis absorbida (Gy) y no se comparan con la TEDE ni con la dosis equivalente en mSv.")

# ====================================================== P0 · magnitudes
RR("Total Effective Dose Equivalent (dosis efectiva total equivalente)", "(dosis efectiva total equivalente)",
   "(equivalente de dosis efectiva total, magnitud de la NRC)")
RR("El impacto radiológico del accidente se evalúa en términos de dosis efectiva total equivalente",
   "dosis efectiva total equivalente", "equivalente de dosis efectiva total (TEDE)")
_append("La TEDE es la suma de ambas. Los factores de conversión proceden del Federal Guidance Report",
        " En RADTRAD 3.03, la TEDE es la suma de la dosis efectiva comprometida a 50 años por inhalación (FGR 11) y de "
        "la dosis efectiva externa por inmersión en la nube (FGR 12); no incluye la irradiación desde el suelo. La "
        "dosis a tiroides es la dosis equivalente comprometida en ese órgano. Ninguna de las dos es una dosis "
        "absorbida, que se expresa en Gy. La herramienta convierte las salidas de rem a mSv una sola vez "
        "(1 rem = 10 mSv), como confirma el cálculo manual del capítulo 13.")

# ============================================== P1 · objectives and scope
_p_sint = P("En síntesis, este documento no solo propone una metodología")
after(_p_sint, [T("El alcance es el de un estudio preliminar: buque atracado, emisión atmosférica a nivel del suelo, "
                  "geometría simplificada, dos escenarios postulados (E1 y E2) y un caso de sensibilidad meteorológica. "
                  "Quedan fuera del cálculo, y se tratan solo de forma cualitativa, las maniobras y la navegación por la "
                  "ría, las vías marina y alimentaria, el depósito en el suelo, la exposición a bordo y la respuesta de "
                  "emergencia.")])

# ====================================================== P1 · chapters 4–6
RR("Se excluyen conceptos cuyo refrigerante o sales reaccionan violentamente",
   "cuyo refrigerante o sales reaccionan violentamente con el agua de mar, como sales basadas en NaCl o reactores "
   "rápidos refrigerados por sodio.",
   "cuyo refrigerante reacciona violentamente con el agua de mar, como el sodio de los reactores rápidos, o es una sal "
   "clorada, muy soluble y corrosiva en contacto con ella.")
RR("En primer lugar, se excluyen aquellos diseños cuyo refrigerante presenta una elevada reactividad",
   "puede dar lugar a reacciones violentas con consecuencias severas para la integridad del buque, lo que descarta "
   "tecnologías basadas en sales altamente solubles, como las sales cloradas, así como reactores rápidos refrigerados "
   "por sodio.",
   "puede dar lugar a reacciones violentas, como la del sodio, o a la disolución del refrigerante y la corrosión, como "
   "en las sales cloradas, muy solubles; por ello se descartan los reactores rápidos refrigerados por sodio y los de "
   "sales cloradas.")
for _q in ("Tipo", "Refrigerante/moderador", "Tipo de combustible", "Enriquecimiento (%)", "País"):
    RRp("“%s”" % _q, "“%s”" % _q, "«%s»" % _q)
RRp("“Status”", "“Status”", "«Estado de desarrollo»")
for _p in paras():
    if visible(_p).startswith("La columna «Enriquecimiento (%)»"):
        for _r in _p.iter(q("r")):
            _rp = _r.find(q("rPr"))
            if _rp is not None:
                for _x in _rp.findall(q("b")) + _rp.findall(q("bCs")):
                    _rp.remove(_x)
RRp("Status", "Status", "Estado de desarrollo")
RRp("Corea y Arabia Saudi", "Arabia Saudi", "Arabia Saudí")
RRp("KAIROS Power, LLC.", "KAIROS Power, LLC.", "Kairos Power, LLC")
RRp("Terrapower", "Terrapower", "TerraPower")
RR("La ventaja del KP-FHR procede sobre todo del estado del licenciamiento",
   "el permiso de construcción del reactor de demostración Hermes.",
   "el permiso de construcción del reactor de demostración Hermes, no del diseño comercial del KP-FHR.")
RR("Todas las matrices son consistentes.", "Todas las matrices son consistentes.",
   "Todas las matrices tienen una coherencia interna aceptable (razón de consistencia inferior a 0,10).")
RR("Su diseño combina elementos de distintas tecnologías de cuarta generación",
   "manteniendo al mismo tiempo un elevado nivel de seguridad inherente y una gran flexibilidad operativa.",
   "manteniendo al mismo tiempo la seguridad inherente que aporta cada uno.")
RR("de operación del KP-FHR proporciona una gran flexibilidad en la selección del ciclo",
   "El elevado nivel de temperatura de operación del KP-FHR proporciona una gran flexibilidad en la selección del "
   "ciclo de conversión energética.",
   "La temperatura de salida del KP-FHR, de unos 650 °C, permite elegir entre varios ciclos de conversión energética.")
RR("este enfoque operativo constituye un elemento claramente favorable", "constituye un elemento claramente favorable",
   "puede ser favorable")
RR("La operación a carga parcial reduce la fatiga térmica",
   "La operación a carga parcial reduce la fatiga térmica de los componentes y favorece una mayor estabilidad del "
   "sistema.",
   "Cabe esperar que la operación a carga parcial reduzca la fatiga térmica de los componentes, aunque no se ha "
   "analizado.")
RR("En términos de seguridad nuclear, operar el reactor por debajo de su potencia nominal",
   "contribuye a un mayor margen", "contribuiría previsiblemente a un mayor margen")
RR("Para acoplarse a la planta existente, el KP-FHR sustituiría a las calderas principales",
   "por lo que pueden mantenerse las condiciones de vapor de la turbina.",
   "condición necesaria para mantener las condiciones de vapor de la turbina, aunque no suficiente: quedan por "
   "comprobar la presión y el caudal de vapor, los saltos térmicos de los circuitos intermedios y los rendimientos.")
RRp("mix energético", "mix energético", "combinación energética")
# LNG carrier -> metanero (the definition is kept in its first mention); "gran porte" not repeated
RR("seleccionando un buque mercante de gran porte (un metanero o LNG carrier)",
   "un buque mercante de gran porte (un metanero o LNG carrier)", "un metanero")
RR("Para el presente estudio se adopta como buque de referencia un buque mercante de gran porte",
   "un buque mercante de gran porte destinado al transporte de gas natural licuado (LNG), representativo de los grandes "
   "LNG carriers", "un buque destinado al transporte de gas natural licuado (GNL), representativo de los grandes "
   "metaneros")
RR("en aplicaciones marítimas de gran porte con elevada demanda energética continua", "aplicaciones marítimas de gran porte",
   "buques de gran tamaño")
_n_lng = 0
for _p in paras():
    if _p in _bibp or visible(_p).startswith(("This thesis", "Its power")) or "un metanero o LNG carrier" in visible(_p):
        continue
    for _o, _nw in (("LNG carriers", "metaneros"), ("LNG carrier", "metanero")):
        while _o in visible(_p) and _o in ptext(_p):
            try:
                RRo(_p, _o, _nw); _n_lng += 1
            except ValueError:
                break
print("LNG carrier -> metanero:", _n_lng)

# ======================================================= P1 · chapter 8
RR("E2, escenario envolvente. Mismo término fuente que E1", "E2, escenario envolvente.",
   "E2, sensibilidad a la pérdida de retención del edificio.")
_p503 = P("Los dos escenarios se calculan con la herramienta del capítulo")
_t_esc = TABLE(("Aspecto", "E1", "E2"), [
    ("Suceso iniciador", "Pérdida total de suministro eléctrico (planta del buque y conexión a tierra)",
     "El mismo; representa además una colisión o un golpe que dañe el recinto del reactor"),
    ("Potencia e historial", "320 MWₜₕ en equilibrio; tritio acumulado en 4,75 años de operación", "Igual que E1"),
    ("Evacuación del calor residual", "RVACS pasivo disponible", "Igual que E1 (no se modela su fallo)"),
    ("Combustible y FLiBe", "Intactos; factores de atenuación al 95 %", "Igual que E1"),
    ("Edificio del reactor", "Acreditado: AF = 2 para yodos y partículas; 1 para gases nobles y H-3", "No acreditado"),
    ("Vía de fuga", "Descarga directa al ambiente a nivel del suelo", "Igual que E1"),
    ("Inventario en RADTRAD", "kpfhr_terminofuente.nif", "kpfhr_terminofuente_E2.nif"),
    ("Tiempo de liberación", "Todo el término fuente, de forma uniforme entre 0 y 2 h", "Igual que E1"),
], [2300, 3700, 3600])
after(_p503, [T("La " + REF("_RefTab_escenarios", "Tabla 11") + " resume la definición de los dos escenarios. E2 solo "
                "retira el crédito de una barrera: es una sensibilidad a la pérdida de retención del edificio y no "
                "modela las consecuencias propias de una colisión, un incendio o una inundación, como daños al "
                "combustible, el fallo del RVACS u otras vías de fuga, que quedan fuera del alcance."),
              CAP("Tabla", "Definición de los escenarios E1 y E2", "_RefTab_escenarios"), _t_esc, EMPTY()])

# ======================================================= P1 · chapter 9
after(P("Las densidades del conjunto de datos de Kairos Power corresponden al material combustible"), [
    T("Por ejemplo, para el Cs-137, con 1,57·10⁻⁴ átomos/(b·cm) y V = 8,95·10⁴ cm³, N = 1,57·10⁻⁴ · 10²⁴ · "
      "8,95·10⁴ ≈ 1,41·10²⁵ átomos; con λ = ln 2 / 30,08 años = 7,30·10⁻¹⁰ s⁻¹, A = λ · N ≈ 1,03·10¹⁶ Bq "
      "(unos 2,8·10⁵ Ci), que es la actividad del núcleo que recoge el Anexo C.")])
_append("El inventario de referencia procede de las concentraciones de equilibrio del material combustible",
        " En el fichero de inventario de RADTRAD el tritio figura como 19,90 Ci/MWₜₕ, que el código multiplica por "
        "320 MWₜₕ para obtener los 6.368 Ci; el cálculo manual del capítulo 13 confirma que la normalización no se "
        "aplica dos veces.")
_append("La dosis del tritio depende de su forma química.",
        " La absorción cutánea del agua tritiada no se modela como una vía aparte.")

# ====================================================== P1 · chapter 10
RR("Estos datos, que cumplen con los requisitos establecidos en la normativa descrita",
   "Estos datos, que cumplen con los requisitos establecidos en la normativa descrita en el apartado ",
   "Estos datos tienen el formato y la resolución que exige la normativa descrita en el apartado ")
RR("Estos datos tienen el formato y la resolución que exige la normativa", ", proceden de una estación",
   ", pero proceden de una estación")
RR("Con el objetivo de adaptar los datos de entrada a las condiciones de Bilbao a 10 m",
   "noroeste–este-noroeste (NW–WNW)", "noroeste–oeste-noroeste (NW–WNW)")
_append("Con el objetivo de adaptar los datos de entrada a las condiciones de Bilbao a 10 m",
        " Las direcciones son siempre de procedencia del viento, que es como las lee ARCON96.")
RR("Teniendo en cuenta los 58 m, para adaptar la rosa de vientos",
   "la distribución original con predominancia hacia el sur (S) se ajusta para reflejar correctamente un patrón "
   "predominante hacia el oeste (W), como en Bilbao.",
   "la distribución original, con predominio de los vientos del sur (S), pasa a un predominio de los vientos del "
   "oeste (W), como en Bilbao.")
RR("Esta metodología permite construir una serie de 5 años sintéticos",
   "una serie de 5 años sintéticos, cumpliendo con los requisitos de entrada de ARCON96",
   "cinco series sintéticas derivadas de un mismo año, con el formato de entrada de ARCON96")
RR("Los programas de vigilancia meteorológico deben incluir", "vigilancia meteorológico", "vigilancia meteorológica")
RR("Los programas de vigilancia meteorológica deben incluir", "del emplazamiento”", "del emplazamiento” (traducción propia)")
RR("radica fundamentalmente en la distancia a la que se sitúan el límite del área de exclusión",
   "en la distancia a la que se sitúan el límite del área de exclusión (EAB) y la zona de baja población (LPZ)",
   "en las distancias a las que se sitúan el límite del área de exclusión (EAB) y el límite exterior de la zona de baja "
   "población (LPZ)")
_append("Se emplean dos percentiles, de acuerdo con la RG 1.145",
        " ARCON96 calcula las series horarias, las medias, la distribución acumulada y el percentil 95 global; el "
        "percentil 99,5 sectorial, el máximo de ambos y la conversión a intervalos son posprocesamiento de la "
        "herramienta (capítulo 12).")

# =========================================================== P2 · ch. 12
RRp("Una de las aportaciones de este trabajo es una herramienta software", "herramienta software", "herramienta informática")
RRp("El capítulo 12 describe la herramienta software", "herramienta software", "herramienta informática")
RRp("RADTRAD y el postproceso para los escenarios E1 y E2", "el postproceso", "el posprocesamiento")
SETC("Fase", "3. Postproceso", 0, "3. Posprocesamiento")
RRp("tres pestañas: el pipeline de ARCON96 y RADTRAD", "el pipeline de ARCON96", "la cadena de cálculo de ARCON96")

# ====================================================== P1 · chapter 13
RR("Como la emisión termina a las 2 horas, la dosis acumulada en 48 horas",
   "La dosis a tiroides es un 1,3 % mayor que la TEDE en E1, porque el tritio se reparte de manera uniforme en el "
   "organismo, y un 1,8 % mayor en E2 que en E1.",
   "Según el desglose manual, la dosis a tiroides es un 1,3 % mayor que la TEDE en E1: el tritio aporta lo mismo a "
   "ambas, porque su factor de dosis es igual en todos los órganos, y la diferencia procede de los yodos, cuyo factor "
   "de dosis a tiroides es mucho mayor que el efectivo. En E2 la dosis a tiroides es un 1,8 % mayor que en E1.")
RR("con 6.368 Ci y un factor de 1,73·10⁻¹¹ Sv/Bq", "con 6.368 Ci y un factor de 1,73·10⁻¹¹ Sv/Bq, aporta el 99,4 % de la TEDE;",
   "con 6.368 Ci y un factor de 1,73·10⁻¹¹ Sv/Bq (6.368 × 3,7·10¹⁰ Bq × 3,5·10⁻⁴ m³/s × 1,73·10⁻¹¹ Sv/Bq = "
   "1,427 Sv·m³/s, es decir, 1.426,7 mSv por unidad de X/Q), aporta el 99,4 % de la TEDE del desglose manual;")
RR("El cálculo manual coincide con RADTRAD dentro del 1,2 %", "dentro del 1,2 %, y",
   "dentro del 1,2 %, una diferencia que no se ha atribuido a una causa concreta, y")
SETC("Contribución", "Total (RADTRAD)", 3, "98,8 % (cociente RADTRAD / manual)")
_hc = [tc for tbl in body.iter(q("tbl")) if _cell_text(tbl.find(q("tr")).find(q("tc"))) == "Contribución"
       for tc in tbl.find(q("tr")).findall(q("tc"))][3].find(q("p"))
RRo(_hc, "Fracción", "Fracción del total manual")
# Table 23
SETC("Zona", "Límite del área de exclusión (EAB)", 2, "Cualquier ventana de 2 h")
SETC("Zona", "Zona de baja población (LPZ)", 2, "Paso de la nube (30 días)")
SETC("Zona", "Evacuación", 1, "TEDE proyectada, 50 mSv (criba)")
SETC("Zona", "Confinamiento", 1, "TEDE proyectada, 10 mSv (criba)")
SETC("Zona", "Profilaxis con yodo", 1, "Dosis equivalente a tiroides, 100 mSv")
SETC("Zona", "Profilaxis con yodo", 2, "7 días (hipótesis)")
SETC("Zona", "Profilaxis con yodo", 4, "≈ 10 m")
SETC("Zona", "Zona de planificación", 0, "Contorno de 10 mSv en 96 h")
SETC("Zona", "Efectos deterministas, médula", 1, "Dosis absorbida en médula, 1 Gy")
SETC("Zona", "Efectos deterministas, médula", 4, "No evaluado")
SETC("Zona", "Efectos deterministas, tiroides", 1, "Dosis absorbida en tiroides, 5 Gy")
SETC("Zona", "Efectos deterministas, tiroides", 4, "No evaluado")
RR("La dosis más alta del barrido, 99,6 mSv a 10 m",
   "La dosis más alta del barrido, 99,6 mSv a 10 m, no llega al límite de 250 mSv del EAB y la LPZ ni a los umbrales "
   "de efectos deterministas; la evacuación alcanza 15 m, la profilaxis con yodo unos 10 m y el confinamiento y la zona "
   "de planificación, 34 m.",
   "Son valores del escenario y de las hipótesis analizadas, obtenidos por interpolación entre los nodos del barrido, "
   "separados 10 m. La dosis más alta, 99,6 mSv a 10 m, no llega a los 250 mSv del EAB y la LPZ; «≤ 10 m» expresa la "
   "resolución del estudio y no permite inferir el comportamiento por debajo de esa distancia. La evacuación cruza "
   "entre 10 m (99,6 mSv) y 20 m (26,6 mSv), en 15 m; el confinamiento y el contorno de 10 mSv en 96 h, entre 30 m "
   "(12,5 mSv) y 40 m (7,2 mSv), en 34 m; y la profilaxis con yodo, justo por encima del nodo de 10 m, con unos "
   "101–103 mSv a tiroides a 10 m y unos 27 mSv a 20 m, estimados con la relación entre la dosis a tiroides y la TEDE "
   "del desglose manual.")
after(P("Son valores del escenario y de las hipótesis analizadas, obtenidos por interpolación"), [
    T("Los umbrales de efectos deterministas se expresan en dosis absorbida (1 Gy en médula ósea y 5 Gy en tiroides en "
      "menos de dos días) y no se han calculado, por lo que figuran como no evaluados. Pueden acotarse: para las "
      "emisiones beta y gamma, el factor de ponderación de la radiación es 1, de modo que la dosis absorbida en 48 horas "
      "no supera numéricamente la dosis equivalente comprometida del órgano, que a 10 m es del orden de 0,1 Sv para la "
      "tiroides y, como el agua tritiada se distribuye de forma uniforme, del mismo orden para la médula. Quedan así por "
      "debajo de 0,1 Gy, al menos un orden de magnitud por debajo de los umbrales.")])
RR("Los radios obtenidos son entre uno y dos órdenes de magnitud menores que los de los referentes",
   "son entre uno y dos órdenes de magnitud menores que los de los referentes de la ",
   "son menores que los de los referentes de la ")
RR("Los radios obtenidos son menores que los de los referentes", "o la DEPZ de al menos 1,5 km de Devonport.",
   "o la DEPZ de al menos 1,5 km de Devonport: entre 2 y 9 veces menores que la evacuación de Barrow y entre unas 18 y "
   "56 veces menores que el resto.")
RR("ni siquiera el caso de sensibilidad se acerca a las distancias de un submarino",
   "y las distancias genéricas de la Directriz básica, 100 m para la evacuación y 200 m para el confinamiento, envuelven "
   "los radios calculados con un margen de entre cuatro y siete veces.",
   "y los radios calculados quedan por debajo de las distancias genéricas de la Directriz básica para un foco sin "
   "caracterizar: 100 m de radio de la zona de medidas urgentes y corona de alerta hasta 200 m. Como esas zonas se "
   "definen por tasa de dosis y no por dosis integrada, la comparación es solo geométrica.")
RR("El cálculo de ejemplo de Kairos Power da 7,2 mSv a 335 m", "da 7,2 mSv a 335 m", "da 0,716 rem (7,16 mSv) a 335 m")
RR("El cálculo de ejemplo de Kairos Power da 0,716 rem",
   "obtiene 0,14 mSv a esa distancia, y 0,27 mSv con clase F y 1 m/s. Como el tritio es el mismo, la diferencia está en "
   "el X/Q: el ejemplo implica unos 5·10⁻³ s/m³ a 335 m, unas 48 veces el X/Q de diseño de este trabajo, un valor que ni "
   "siquiera la clase F con 1 m/s alcanza con las expresiones de ARCON96. Con ese X/Q, los radios serían de unos 47 m "
   "para el EAB, 110 m para la evacuación y 270 m para el confinamiento, del orden de las distancias genéricas de la "
   "Directriz.",
   "obtiene 0,143 mSv a esa distancia (interpolada entre 330 y 340 m), unas 50 veces menos, y 0,27 mSv con clase F y "
   "1 m/s. Si el resto de parámetros (receptor, tasa de respiración, forma química del tritio y duración de la emisión) "
   "fuera igual, el ejemplo implicaría un X/Q de unos 4,9·10⁻³ s/m³ a 335 m, unas 49 veces el de diseño de este trabajo, "
   "un valor que ni siquiera la clase F con 1 m/s alcanza con las expresiones de ARCON96. No se ha podido reproducir el "
   "cálculo de Kairos Power, de modo que atribuir toda la diferencia al X/Q es una hipótesis. Como sensibilidad "
   "uniforme, y no como réplica de su meteorología, multiplicar el X/Q por 49 llevaría los radios a unos 48 m para el "
   "EAB, 112 m para la evacuación y 271 m para el confinamiento.")
SETC("Caso", "X/Q del ejemplo de Kairos Power (× 48)", 1, "48 m")
SETC("Caso", "X/Q del ejemplo de Kairos Power (× 48)", 2, "112 m")
SETC("Caso", "X/Q del ejemplo de Kairos Power (× 48)", 3, "271 m")
SETC("Caso", "X/Q del ejemplo de Kairos Power (× 48)", 0, "X/Q × 49 (sensibilidad uniforme, ejemplo de Kairos Power)")

# ====================================================== P1 · chapter 14
RR("Las zonas de emergencia de un buque con KP-FHR atracado en el puerto exterior de Bilbao son de pocas decenas",
   "Las zonas de emergencia de un buque", "En el escenario y con las hipótesis analizadas, las zonas de emergencia de "
   "un buque")
RR("La dosis la produce la inhalación del tritio, el 99,4 % de la TEDE", "Por eso E1 y E2 dan las mismas zonas,",
   "Por eso E1 y E2 dan las mismas zonas —lo que no demuestra que una colisión real tuviera consecuencias "
   "similares, porque E2 solo retira el crédito del edificio—,")
RR("La dosis la produce la inhalación del tritio, el 99,4 % de la TEDE",
   "quedan entre uno y dos órdenes de magnitud por debajo de las de los buques y submarinos de propulsión nuclear con "
   "reactores de agua, y también por debajo de las distancias genéricas de la Directriz básica (100 y 200 m), que las "
   "envuelven con un margen de cuatro a siete veces.",
   "quedan entre 2 y 56 veces por debajo de las de los buques y submarinos de propulsión nuclear con reactores de agua, "
   "y también por debajo de las distancias genéricas de la Directriz básica para un foco sin caracterizar (100 m y "
   "200 m), con las que solo cabe una comparación geométrica.")
RR("El resultado es robusto frente a las hipótesis sobre las barreras",
   "harían falta un X/Q unas 50 veces mayor, como el implícito en el ejemplo de Kairos Power, o un inventario de tritio "
   "unas 30 veces mayor para alcanzar las distancias de la Directriz.",
   "con un X/Q 49 veces mayor, como el que implicaría el ejemplo de Kairos Power, o con un inventario de tritio unas "
   "30 veces mayor, los radios alcanzarían el orden de las distancias genéricas de la Directriz.")
RR("Las zonas apenas salen del buque", "y las distancias de la Directriz pueden adoptarse como zonas de planificación "
   "conservadoras en torno al reactor.",
   "y las distancias genéricas de la Directriz pueden servir de referencia geométrica mientras no se disponga de un "
   "cálculo con meteorología local; su adopción corresponde a la autoridad competente.")
RR("Atraque: el puerto exterior y la terminal de GNL de Zierbena son adecuados",
   "el puerto exterior y la terminal de GNL de Zierbena son adecuados; con zonas de pocas decenas de metros, ninguna "
   "zona habitada ni instalación ajena al atraque queda afectada.",
   "con la posición del atraque y la meteorología adoptadas, las zonas calculadas no alcanzan zonas habitadas ni "
   "instalaciones ajenas al atraque del puerto exterior; la idoneidad del atraque requiere además comprobaciones "
   "náuticas, de protección física y de la propia terminal de GNL.")
RR("Maniobras y retirada: como la emisión del accidente base de diseño dura 2 horas",
   "como la emisión del accidente base de diseño dura 2 horas, retirar el buque no reduce su dosis; los remolcadores y "
   "el plazo de retirada se justifican para los sucesos más allá del diseño.",
   "el efecto de retirar el buque depende del tiempo hasta la emisión, de la duración de la maniobra y de la "
   "trayectoria, que no se han analizado; los remolcadores y el plazo de retirada deben fijarse con ese análisis.")
RR("Profilaxis con yodo: con un radio de unos 10 m",
   "con un radio de unos 10 m, el reparto de yodo estable se limita a la tripulación y al personal del muelle de "
   "atraque.",
   "el criterio de profilaxis solo se alcanza en el entorno inmediato del buque (radio de cribado de unos 10 m); la "
   "decisión sobre el reparto de yodo estable corresponde a la autoridad competente.")
RR("Plan de emergencia: la coordinación con el plan de protección civil de Euskadi",
   "puede apoyarse en las distancias genéricas de la Directriz, que envuelven las calculadas.",
   "puede tomar como referencia geométrica las distancias genéricas de la Directriz, mayores que las calculadas, "
   "hasta que se disponga de un análisis con meteorología local.")
RR("Las distancias calculadas son del orden de las dimensiones del buque",
   "y la estela del buque y del muelle, que no se acredita, aumentaría la dispersión.",
   "y el efecto de la estela del buque y del muelle, de las recirculaciones y de la altura real de la descarga, de "
   "signo indeterminado sin datos locales, no se ha cuantificado; tampoco se han calculado las dosis de receptores a "
   "bordo.")
after(P("La posición del atraque y la del reactor dentro del buque son aproximadas"), [
    B("Las incertidumbres que más pueden cambiar los resultados son el inventario de tritio y su forma química, la "
      "meteorología del emplazamiento y la geometría de campo cercano; no se han calculado la irradiación desde el "
      "suelo, la ingestión ni la vía marina.")])


# ----------------------------------------------- abstracts: criteria wording
RR("El término fuente se estima con un enfoque mecanicista", "comparando la dosis efectiva con los criterios de 250 mSv en "
   "las peores 2 horas y en 30 días, respectivamente,", "comparando la TEDE con el criterio de 250 mSv en cualquier "
   "ventana de 2 horas y durante el paso de la nube (30 días de cálculo), respectivamente,")
RR("La dosis la domina la inhalación del tritio, el 99 % de la TEDE", "se cumple ya a 10 m",
   "se cumple ya en la distancia mínima calculada, 10 m")
RR("The source term is estimated with a mechanistic approach", "comparing the total effective dose with the 250 mSv "
   "criteria for the worst 2 hours and for 30 days", "comparing the TEDE with the 250 mSv criterion for any 2-hour "
   "window and for the whole cloud passage (30-day calculation horizon)")
RR("The dose is dominated by tritium inhalation, 99 % of the TEDE", "is already met at 10 m",
   "is already met at the smallest distance calculated, 10 m")
RR("Iturburu-terminoa ikuspegi mekanizista batekin", "dosi eraginkorra 250 mSv-eko irizpideekin alderatuz lortzen dira, "
   "2 ordu txarrenetan eta 30 egunetan", "TEDEa 250 mSv-eko irizpidearekin alderatuz lortzen dira, edozein 2 orduko "
   "leihotan eta hodeiaren igarotze osoan (30 eguneko kalkulu-horizontea)")
RR("Dosia tritioaren arnasketak menderatzen du", "10 m-tan betetzen da jada",
   "kalkulatutako distantzia txikienean, 10 m-tan, betetzen da jada")
RRo(P("Fase 3: postproceso", style="Ttulo2"), "postproceso", "posprocesamiento")
RR("El resultado es robusto frente a las hipótesis sobre las barreras", "El resultado es robusto frente a las hipótesis "
   "sobre las barreras, pero", "El resultado apenas depende del crédito del edificio del reactor, pero es")

RRp("comprobar la ausencia de efectos deterministas y", "comprobar la ausencia de efectos deterministas",
    "acotar los efectos deterministas")
RRp("Ninguna zona alcanza las instalaciones de la terminal", "Ninguna zona alcanza",
    "Con estas hipótesis, ninguna zona alcanza")

RRp("Cada zona de la Tabla 4 se evalúa con su magnitud", "Los efectos deterministas se comprueban con la TEDE y la dosis "
    "a tiroides en 48 horas de E2, como aproximación a las dosis absorbidas en médula (1 Gy) y tiroides (5 Gy).",
    "La herramienta conserva, como indicadores de cribado, los contornos de 1.000 mSv de TEDE y de 5.000 mSv a "
    "tiroides en 48 horas de E2. No son dosis absorbidas y no sustituyen la comparación con los umbrales de efectos "
    "deterministas, que se expresan en Gy y se acotan aparte en el capítulo 13.")

C.on_paragraph(P("Los criterios de emplazamiento, 250 mSv (25 rem) TEDE en cualquier periodo"),
               "v12 (revisión técnica externa): pendiente de verificar con las fuentes primarias el texto de NUREG-0396 "
               "sobre los 200 rem, el alcance exacto de 10 CFR 50.67 y la revisión de la RG 1.183 empleada.")
C.on_paragraph(P("Los umbrales de efectos deterministas se expresan en dosis absorbida"),
               "v12: la tabla de radios (Tabla 24) ya no compara TEDE en mSv con umbrales en Gy. Las filas deterministas figuran como no "
               "evaluadas con una acotación conservadora (wR = 1 y dosis comprometida ≥ dosis en 48 h).")
_counts = _renumber()
print("captions:", _counts)
print("V12 FAILURES:", len(_FAIL), *_FAIL, sep="\n  ")
