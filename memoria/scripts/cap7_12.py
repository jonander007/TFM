# Audit of the calculation methodology (chapters 7 to 12): content errors (A), text out of date after
# E1/E2 and the Table 4 zones (B), terminology and format (D), and the meteorological sensitivity case.

# ============================================================= chapter 7 ==
RR("Parámetros de ARCON96. Velocidad mínima del viento de 0,5 m/s",
   "constante de anchura del sector de promediado de 4,3.",
   "constante de anchura del sector de promediado de 4,3. El área de la sección del edificio se fija en 0,01 m², "
   "de modo que no se acredita la mayor dispersión que produce su estela, lo que es conservador.")
RR("Los radios del EAB y de la LPZ se determinan con los criterios de emplazamiento de la NRC",
   "Los criterios de planificación de emergencias recogidos en el",
   "Con la misma cadena se evalúan también las zonas de medidas urgentes y de planificación recogidas en el")
RR("Los radios del EAB y de la LPZ se determinan con los criterios de emplazamiento de la NRC",
   " (por ejemplo, 10 mSv en 96 horas) pueden aplicarse con la misma cadena sin más que cambiar el periodo de "
   "integración y el límite.",
   " (@REF:_RefTab_criterios|Tabla 4@), cambiando el periodo de integración, el límite y, en su caso, la magnitud "
   "(dosis a tiroides) y el escenario (E1 o E2) (capítulo @REFN:_RefCap_herr|12@).")
RR("TEDE en el EAB (peores 2 h) y en la LPZ (30 d)", "TEDE en el EAB (peores 2 h) y en la LPZ (30 d)",
   "TEDE y dosis a tiroides acumuladas en el EAB y la LPZ", nth=0)
RR("TEDE(d) de todos los juegos de fracciones de yodo", "TEDE(d) de todos los juegos de fracciones de yodo",
   "Dosis frente a la distancia de todos los juegos de fracciones de yodo, en E1 y E2")
RR("Radios del EAB y la LPZ y mapa", "Radios del EAB y la LPZ y mapa",
   "Radios de las zonas de la Tabla 4 y mapa")

# ============================================================= chapter 9 ==
RR("La elección de dicha sección se justifica por su ubicación central en el núcleo",
   "La elección de dicha sección se justifica por su ubicación central en el núcleo, donde se ha comprobado que las "
   "concentraciones isotópicas alcanzan valores máximos en comparación con otras zonas axiales y radiales. En "
   "consecuencia, la extrapolación de este isotópico a la totalidad del combustible introduce un sesgo conservador, "
   "al sobreestimar de forma intencionada el inventario disponible para su eventual liberación durante el accidente "
   "postulado.",
   "La sección se encuentra en la parte central del núcleo y sus concentraciones son algo superiores a la media de "
   "las 40 zonas del conjunto de datos de Kairos Power: un 4 % para el Cs-137, un 7 % para el Pu-239 y un 21 % para "
   "el Xe-133 y el Ba-140. No son, sin embargo, las máximas, que se alcanzan en las zonas axiales 4 y 5 para los "
   "nucleidos de vida corta y en la 10 para los de vida larga. Como el inventario se normaliza después a la potencia "
   "térmica (apartado siguiente), la actividad de los productos de fisión de vida corta queda fijada por esa "
   "normalización, y la elección de la zona influye sobre todo en la proporción entre los nucleidos de vida larga y "
   "los de vida corta.")
RR("Vida media y constante de desintegración", "Vida media", "Periodo de semidesintegración")
RR("Para cada radionucleido se recopila la vida media a partir de bases de datos", "la vida media",
   "el periodo de semidesintegración")
RR("La vida media se expresa finalmente en segundos", "La vida media se expresa", "El periodo se expresa")
RR("A partir de la vida media", "la vida media", "el periodo de semidesintegración")
RR("es la vida media del radionucleido", "es la vida media del radionucleido",
   "es el periodo de semidesintegración del radionucleido")
RR("y los gases nobles pasan a representar en torno al 99 % de la actividad liberada",
   "en torno al 99 % de la actividad liberada", "en torno al 99 % de la actividad liberada sin contar el tritio")
RR("fracción de liberación inicial desde el combustible hacia el refrigerante/primario",
   "fracción de liberación inicial desde el combustible hacia el refrigerante/primario (dependerá de la hipótesis de "
   "accidente y de la clase de isótopo).",
   "fracción de liberación inicial desde el combustible. En este trabajo f = 1, porque la salida desde el combustible "
   "se representa con los factores de atenuación de sus propias etapas (contaminación por metal pesado, núcleo de "
   "la partícula y difusión a través de los recubrimientos), que para los yodos, los gases nobles y el cesio dejan "
   "salir del orden de 10⁻⁷ de su actividad.")
p_eta = [p for p in paras() if "eficiencia global de mitigación agregada" in ptext(p)][0]
p_build = new_para_like(p_eta,
    "El último factor, el del edificio del reactor, vale 2 para los yodos y las partículas y 1 para los gases "
    "nobles y el tritio. El escenario E1 lo aplica; el E2 (capítulo @REFN:_RefCap_acc|8@) supone que el edificio ha "
    "perdido su capacidad de retención, por lo que su término fuente es la actividad que sale del FLiBe. La "
    "herramienta genera los dos inventarios para RADTRAD (kpfhr_terminofuente.nif y kpfhr_terminofuente_E2.nif).")
p_eta.addnext(p_build)

# ============================================================ chapter 10 ==
RR("el parámetro χ/Q (chi sobre Q) es una magnitud que permite relacionar",
   "Es un coeficiente adimensional en el sentido físico estricto, pero con unidades derivadas (s/m³), y representa",
   "Se mide en s/m³ y representa")
RR("Corto plazo (accidentes de corta duración, típicamente 2 horas).",
   "Corto plazo (accidentes de corta duración, típicamente 2 horas).",
   "Emisiones de corta duración; χ/Q para periodos de 1 hora a 30 días.")
RR("Temperatura del aire (°C), a dos niveles distintos.", "Temperatura del aire (°C), a dos niveles distintos.",
   "Clase de estabilidad atmosférica de cada hora (A a G), obtenida antes de preparar los ficheros a partir de la "
   "temperatura del aire medida a dos alturas.")
RR("Aunque ARCON96 no emplea explícitamente la clasificación Pasquill-Gifford",
   ptext(P("Aunque ARCON96 no emplea explícitamente la clasificación Pasquill-Gifford")).strip(),
   "ARCON96 no calcula la estabilidad: lee en cada registro la clase de Pasquill (de 1 a 7), que debe obtenerse "
   "previamente a partir de la diferencia de temperatura entre dos alturas, según la RG 1.23.")
p_inter = P("Con esta información, se determina el tipo de interacción viento-edificio")
RR("Con esta información, se determina el tipo de interacción viento-edificio", ptext(p_inter).strip(),
   "Con esta información, ARCON96 decide si en esa hora el viento puede llevar la emisión hacia el receptor, es "
   "decir, si su dirección cae dentro de la ventana de direcciones definida alrededor de la línea fuente–receptor, y "
   "en ese caso calcula el χ/Q con los coeficientes de difusión del apartado siguiente. El efecto de los edificios "
   "se introduce mediante un único parámetro, el área de su sección transversal, que aumenta la dispersión por la "
   "estela. En este trabajo esa área se fija en 0,01 m², de modo que no se acredita la estela, lo que es "
   "conservador porque la estela reduce el χ/Q.")
for sub in ("Frontal, si el viento impacta directamente sobre el edificio.",
            "Paralela, si el flujo es canalizado entre estructuras.",
            "Oblicua, si se presenta en ángulo intermedio.",
            "Cada una de estas configuraciones influye de manera diferente en la generación de turbulencia"):
    delete_para(P(sub))
RR("La dirección del viento respecto a la geometría del edificio.", "respecto a la geometría del edificio",
   "respecto a la línea fuente–receptor")
RR("La altura y orientación de estructuras cercanas.", "La altura y orientación de estructuras cercanas.",
   "El área de la sección transversal del edificio (en este trabajo, sin efecto de estela).")
RR("A partir de la serie horaria, ARCON96 calcula medias móviles de χ/Q",
   "desde el inicio de la emisión hasta 1, 2, 4, 8, 12, 24, 48, 96, 168, 360 y 720 horas",
   "desde el inicio de la emisión para los periodos que se le piden; en este trabajo, 1, 2, 4, 8, 12, 24, 96, 168, "
   "360 y 720 horas")
RR("Para el intervalo de 0 a 2 horas se toma el máximo de los valores de 0–1 h y 0–2 h.",
   "Los intervalos normalizados con los que ARCON96 presenta sus resultados son 0–2 h, 2–8 h, 8–24 h, 1–4 días y "
   "4–30 días",
   "Con los diez periodos se obtienen nueve intervalos (0–2, 2–4, 4–8, 8–12, 12–24, 24–96, 96–168, 168–360 y "
   "360–720 h), más finos que los cinco normalizados con los que ARCON96 presenta sus resultados (0–2 h, 2–8 h, "
   "8–24 h, 1–4 días y 4–30 días)")
p_int = P("Para el intervalo de 0 a 2 horas se toma el máximo de los valores de 0–1 h y 0–2 h.")
p_int.addnext(new_para_like(p_int,
    "Como los percentiles de las medias no son estrictamente aditivos, la expresión puede dar valores incoherentes. "
    "La herramienta impide que la media crezca al alargar el periodo, limitándola al valor del periodo anterior, y, "
    "si un intervalo sale negativo, usa la media desde el origen, que es conservadora para ese intervalo."))
RR("Las imágenes 2 y 3 muestran las rosas de los vientos de las dos localizaciones a analizar:",
   "Las imágenes 2 y 3 muestran las rosas de los vientos de las dos localizaciones a analizar:",
   "Las figuras siguientes muestran las rosas de los vientos de los datos de partida y de Bilbao:")
RR("Teniendo en cuenta los 58 m, para adaptar la rosa de vientos", "invertir el sentido angular",
   "invertir la dirección (girarla 180°)")
RR("Teniendo en cuenta los 58 m, para adaptar la rosa de vientos", "más acorde con el formato de representación polar "
   "empleado en la segunda imagen.", "como en Bilbao. El giro neto es, por tanto, de 90° en sentido horario.")
RR("Rotar 90° en sentido antihorario", "Rotar 90° en sentido antihorario",
   "Girar 180° y después 90° en sentido antihorario (90° en sentido horario en total)", 1)
RR("se ha corregido en el MET05 un registro con la hora mal asignada", "se ha corregido en el MET05",
   "Se ha corregido en el MET05")
RR("Por ello, además de sustituir la serie por datos reales del puerto, se recomienda analizar la sensibilidad",
   "Por ello, además de sustituir la serie por datos reales del puerto, se recomienda analizar la sensibilidad de "
   "los resultados a la estabilidad, por ejemplo repitiendo el cálculo con la meteorología determinista del "
   "accidente de referencia de ARPANSA (clase F y 1 m/s).",
   "Por ello, además de recomendar que la serie se sustituya por datos reales del puerto, se calcula un caso de "
   "sensibilidad con meteorología constante de clase F y 1 m/s en todas las horas, la de las primeras 12 horas del "
   "accidente de referencia de ARPANSA (capítulo @REFN:_RefCap_marco|3@). Con viento constante, el percentil 95 "
   "global y el 99,5 del sector que contiene la dirección del viento coinciden con el χ/Q de esas condiciones, "
   "estables y de viento flojo, desfavorables para una emisión a nivel del suelo. La herramienta repite con esa "
   "meteorología toda la cadena, con los escenarios E1 y E2 (capítulo @REFN:_RefCap_herr|12@), y los resultados se "
   "comparan con los del caso base en el capítulo @REFN:_RefCap_res|13@.")

# ============================================================ chapter 11 ==
RR("Este apartado tiene como finalidad integrar todo lo previamente analizado", "en función de la dosis absorbida",
   "en función de la dosis efectiva")
RR("Este apartado tiene como finalidad integrar todo lo previamente analizado", "dichos radionucleidos en la",
   "dichos radionucleidos en el")
RR("Este apartado tiene como finalidad integrar todo lo previamente analizado", "Este apartado tiene", "Este capítulo tiene")
RR("En la sección previa se ha constatado que para evaluar las distintas zonas de emergencia",
   "calcular la dosis absorbida en cada punto", "calcular la dosis efectiva en cada punto")
RR("es la aportación del término fuente",
   "En el KP-FHR la eliminación de aerosoles en el edificio del reactor",
   "En la metodología de Kairos Power para el KP-FHR, la eliminación de aerosoles en el edificio del reactor")
RR("es la aportación del término fuente",
   "que la NRC considera conservadora para esta aplicación",
   "que la NRC considera conservadora para esta aplicación. En este trabajo no se utiliza: la atenuación del "
   "edificio ya está incluida en el término fuente y el modelo de RADTRAD no tiene mecanismos de eliminación "
   "(véase el modelo adoptado para el KP-FHR, más abajo)")
RR("Las tasas de respiración son las de la RG 1.183", ", ampliando la simulación si la dosis sigue creciendo",
   " (como la emisión termina a las 2 horas, la nube ha pasado mucho antes de ese plazo)")

# ============================================================ chapter 12 ==
RR("Una de las aportaciones de este trabajo es una herramienta software",
   "Está escrita en Python y se compone de dos módulos: PIPELINE.py, que encadena ARCON96, RADTRAD y el postproceso, "
   "y zonas_emergencia.py, que determina los radios del EAB y la LPZ y genera el mapa.",
   "Está escrita en Python. Su núcleo son dos módulos: PIPELINE.py, que encadena ARCON96, RADTRAD y el postproceso "
   "para los escenarios E1 y E2, y zonas_emergencia.py, que calcula los radios de las zonas de la "
   "@REF:_RefTab_criterios|Tabla 4@ y genera el mapa. Los completan preparar_met.py, que revisa los ficheros "
   "meteorológicos y los escribe en el formato de ARCON96; generar_nif.py, que construye los inventarios de E1 y E2 a "
   "partir del libro de cálculo; sensibilidad_met.py, que repite la cadena con meteorología de clase F y 1 m/s; "
   "ver_mapa.py, que abre el mapa; y una interfaz gráfica que recoge los parámetros y organiza cada ejecución en "
   "carpetas de entrada, de trabajo y de salida.")
RR("Un .psf por distancia y juego; ejecución de RADTRAD en lote", "Un .psf por distancia y juego",
   "Un .psf por distancia, juego de fracciones y escenario (E1, E2)")
RR("Envolvente de dosis y cálculo de radios", "Envolvente de dosis y cálculo de radios",
   "Envolvente de dosis y radios de las zonas de la Tabla 4")
RR("Para cada distancia del barrido se ejecutan un caso independiente de la dirección",
   "Esta se da para once periodos de promediado (de 1 a 720 h, incluido el de 48 h), y la herramienta identifica",
   "ARCON96 la escribe para los diez periodos solicitados (de 1 a 720 h) en dos bloques, cada uno con su propia "
   "columna de χ/Q, y la herramienta identifica")
RR("Los casos se ejecutan en paralelo con RADTRAD en modo de lotes.",
   "Los casos se ejecutan en paralelo con RADTRAD en modo de lotes.",
   "Los casos se ejecutan en paralelo con RADTRAD en modo de lotes. Si junto al inventario de E1 está el de E2, la "
   "fase se repite con él y con los mismos juegos de fracciones, y sus resultados se guardan en una subcarpeta "
   "propia.")
p_f4 = P("Como las fracciones del yodo son inciertas, se toma, para cada distancia")
p_f4.addprevious(new_para_like(p_f4,
    "Cada zona de la @REF:_RefTab_criterios|Tabla 4@ se evalúa con su magnitud, su periodo de integración y su "
    "escenario: el EAB, con la TEDE de las peores 2 horas de E1; la LPZ, con la acumulada en 30 días de E1; la "
    "evacuación, con la de 7 días de E2; y el confinamiento, la profilaxis con yodo (dosis a tiroides) y la zona de "
    "planificación, con la mayor de E1 y E2 en 48 horas, 7 días y 96 horas. Las dosis acumuladas se interpolan en la "
    "serie temporal de RADTRAD; como los dos receptores usan la misma tabla de χ/Q, cualquiera de ellos da la dosis a "
    "esa distancia. Los efectos deterministas se comprueban con la TEDE y la dosis a tiroides en 48 horas de E2, como "
    "aproximación a las dosis absorbidas en médula (1 Gy) y tiroides (5 Gy)."))
RR("Las zonas se representan como circunferencias centradas en el buque",
   "con el buque orientado según su rumbo y una ventana con el radio, el criterio y el juego de fracciones que lo "
   "determina.",
   "con el buque orientado según su rumbo y una ventana con el radio, el criterio y el juego de fracciones que lo "
   "determina; en ella pueden elegirse las zonas que se dibujan y modificarse cada criterio.")
p_pend = P("[Pendiente: figura con el mapa de zonas generado con los resultados definitivos.]")
p_pend.addprevious(new_para_like(P("Las zonas se representan como circunferencias centradas en el buque"),
    "El caso de sensibilidad meteorológica del capítulo @REFN:_RefCap_disp|10@ se calcula con sensibilidad_met.py, que "
    "escribe un año de registros horarios con clase F y 1 m/s en el formato de ARCON96 y repite las cuatro fases en "
    "carpetas propias, de modo que no modifica el caso base. Desde la interfaz gráfica se activa con una casilla, y "
    "sus resultados quedan en la subcarpeta SENS_F1 de la salida."))
RR("La herramienta se ha verificado con ejecutables sustitutos",
   "La verificación con los códigos reales queda pendiente de ejecutarse en el entorno Windows en que están "
   "instalados.",
   "Las ejecuciones con los códigos reales, en Windows, pusieron de manifiesto cuatro errores de formato, ya "
   "corregidos: los ficheros meteorológicos no respetaban las columnas fijas de ARCON96, que descartaba todas las "
   "horas; la lectura de la distribución acumulada suponía un solo bloque de periodos, cuando ARCON96 la escribe en "
   "dos bloques con su propia columna de χ/Q (los percentiles calculados coinciden ahora con los de su fichero de "
   "registro); la tabla de χ/Q del .psf no seguía el formato de columnas que lee RADTRAD, que perdía los exponentes y "
   "multiplicaba la dosis; y el fichero de factores de dosis no listaba los nucleidos en el mismo orden que el "
   "inventario, mientras que RADTRAD los asigna por posición. La ejecución completa reveló un quinto error, también "
   "corregido: ARCON96 fija el rango de la distribución acumulada de χ/Q para cada periodo de promediado, pero en el "
   "fichero de distribución escribe la columna de χ/Q de un solo periodo, de modo que, cuando el máximo de 12 h bajaba "
   "una década, el percentil 99,5 de 12 a 720 h salía diez veces mayor. La herramienta reconstruye ahora la escala de "
   "cada periodo con los límites del fichero de registro y comprueba en cada caso que el percentil 95 que obtiene "
   "coincide con el que calcula ARCON96. Con los códigos reales, la TEDE dividida por el χ/Q de 0–2 h es la misma en "
   "las 40 distancias calculadas (1418 mSv·m³/s, con una dispersión del 0,01 %) y coincide con el cálculo manual a "
   "partir del inventario y de los factores de dosis (capítulo @REFN:_RefCap_res|13@), lo que verifica que RADTRAD lee "
   "el χ/Q, el inventario y los factores de dosis como se pretende.")

# ================================================================ alt text ==
_WPD = "{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}"
_ALT = {"Tabla": ["Tabla de factores de atenuación por barrera y clase de producto de fisión"],
        "Mapa": ["Mapa del puerto de Bilbao"],
        "Interfaz de usuario gráfica, Aplicación, Tabla, Excel": ["Muestra de la tabla de datos meteorológicos de partida"],
        "Texto": ["Ejemplo de fichero meteorológico de entrada de ARCON96"],
        "Gráfico, Gráfico radial": ["Rosa de los vientos de los datos de partida a 10 m", "Rosa de los vientos en Bilbao a 10 m",
                                    "Rosa de los vientos de los datos de partida a 58 m", "Rosa de los vientos en Bilbao"]}
for dp in body.iter(_WPD + "docPr"):
    s = dp.get("descr") or ""
    if "El contenido generado por IA" in s:
        key = s.split("\n")[0].strip()
        lst = _ALT.get(key)
        dp.set("descr", lst.pop(0) if lst else key)

C.on_paragraph(p_inter,
               "Auditoría de la metodología (capítulos 7 a 12). Errores corregidos: la zona AZ6-RZ1 no es la de "
               "concentraciones máximas (cap. 9); la fracción f no existe como factor aparte (cap. 9); el χ/Q no es "
               "adimensional; ARCON96 lee la clase de estabilidad y no la temperatura; no clasifica la interacción "
               "frontal, paralela u oblicua con el edificio, y en este trabajo no se acredita la estela (área 0,01 m²); "
               "los periodos son diez, sin el de 48 h, y los intervalos nueve; en la LPZ no se amplía la simulación; la "
               "sedimentación de Henry es de Kairos y aquí no se usa; la transformación a 58 m es un giro neto de 90° "
               "en sentido horario (S → W). Actualizado: E1/E2, zonas de la Tabla 4, módulos de la herramienta y "
               "verificación con los códigos reales. Añadido: caso de sensibilidad meteorológica (clase F, 1 m/s).")

# Wind speeds of the meteorological series are hourly means, not gusts (confirmed by the author)
RR("Se parte de un conjunto de datos meteorológicos recogidos durante un año",
   ", correspondientes a dos alturas",
   ". Las velocidades del viento son medias horarias, no rachas, que es la magnitud que utiliza ARCON96, y "
   "corresponden a dos alturas")
for alt in ("10", "58"):
    for _ in range(len([p_ for p_ in paras() if ("Velocidad máxima a %s" % alt) in ptext(p_)])):
        RR("Velocidad máxima a %s" % alt, "máxima", "media", nth=0)

# Map: ship drawn to scale and berthed by default at the BBG LNG jetty
RR("La posición por defecto es el puerto exterior de Bilbao",
   "La posición por defecto es el puerto exterior de Bilbao, en la zona de la terminal de GNL de Zierbena, y puede "
   "cambiarse al lanzar el cálculo.",
   "El buque se dibuja a escala, con la eslora y la manga del buque de referencia del capítulo "
   "@REFN:_RefCap_buque|6@ (284,4 × 42,5 m), y por defecto aparece atracado en el pantalán de metaneros de la terminal de GNL "
   "de Bahía de Bizkaia Gas, en Punta Ceballos (Zierbena). La posición, el rumbo y las dimensiones pueden cambiarse "
   "al lanzar el cálculo o en el propio visor.")

# Zones centred on the reactor, aft, not amidships
RR("Las zonas se representan como circunferencias centradas en el buque",
   "centradas en el buque con el radio",
   "centradas en el reactor, situado a popa en la zona de máquinas (por defecto, a 28 m de la popa, en el centro "
   "de los 30–35 m de esa zona), con el radio")

# Map tab of the graphical interface
RR("El mapa se genera como página web con Leaflet",
   "y se genera además una imagen estática para informes.",
   "y se genera además una imagen estática para informes. La interfaz gráfica de la herramienta integra el mapa en "
   "una pestaña propia, «Mapa de zonas», que carga los resultados de cada ejecución (caso base, con E1 y E2, y caso "
   "de sensibilidad meteorológica), muestra los radios y dibuja el buque, el reactor y las zonas sobre la "
   "cartografía de OpenStreetMap o la imagen de satélite, con las coordenadas del cursor y una cuadrícula de latitud y "
   "longitud; en ella pueden cambiarse los criterios y la posición, el rumbo y las dimensiones del buque, y abrirse el "
   "mapa completo en el navegador.")
