# Chapter 8 "Accidente postulado": consistency with the source term and the tool, RVACS, port events, E2.

RR("Una vez analizada la idoneidad del conjunto reactor–embarcación", "en el presente apartado", "en el presente capítulo")

# RVACS (KP-TR-012, appendix B): radiation from the vessel to water panels
RR("Tras la pérdida de los sistemas activos de refrigeración, la evacuación del calor residual",
   ", permitiendo la transferencia de calor desde la vasija del reactor hacia el entorno mediante mecanismos de "
   "radiación y convección natural",
   "y transfiere el calor de la vasija por radiación a unos paneles de agua dispuestos junto a ella @CITE:Kai20|25@")

# Tritium release as in Kairos Power's example
RR("La liberación de radionucleidos durante el accidente está dominada por procesos de desorción",
   "suponiendo una liberación rápida y directa del tritio al gas de cobertura y, posteriormente, al edificio del reactor",
   "suponiendo, como en el ejemplo de Kairos Power, una liberación instantánea del tritio al gas de cobertura y, "
   "posteriormente, al edificio del reactor")

# Reactor building: what Kairos assumes and how this work credits it (E1) or not (E2)
p_edif = P("Una vez que los radionucleidos alcanzan el edificio del reactor, se asume que la retención adicional es mínima")
RR("Una vez que los radionucleidos alcanzan el edificio del reactor, se asume que la retención adicional es mínima",
   ptext(p_edif).strip(),
   "En el ejemplo de Kairos Power, los radionucleidos que llegan al gas de cobertura pasan sin retención al edificio "
   "del reactor, donde parte de los aerosoles se deposita por gravedad, y desde él escapan al exterior con las "
   "hipótesis de fuga de los accidentes base de diseño; la ventilación se supone parada desde el inicio del accidente "
   "y no se acreditan filtros @CITE:Kai20|25@. En este trabajo el edificio se acredita en el escenario E1 mediante su "
   "factor de atenuación (capítulo @REFN:_RefCap_lib|9@), que reduce a la mitad la actividad de los yodos y de las "
   "partículas y no retiene los gases nobles ni el tritio, y no se acredita en el escenario E2.")

# Tritium dominance: Kairos result, not anticipated for this work
RR("El impacto radiológico del accidente se evalúa en términos de dosis efectiva total equivalente",
   "La contribución dominante a la dosis corresponde al tritio, mientras que la aportación del resto de productos de "
   "fisión resulta significativamente menor, reflejo de la elevada capacidad de retención del combustible TRISO y del "
   "refrigerante FLiBe.",
   "En ese cálculo la contribución dominante a la dosis corresponde al tritio, reflejo de la elevada capacidad de "
   "retención del combustible TRISO y del refrigerante FLiBe para el resto de productos de fisión. Ese reparto es el "
   "del ejemplo de Kairos Power; en este trabajo el término fuente se construye con el inventario del capítulo "
   "@REFN:_RefCap_lib|9@, y la contribución de cada nucleido se analiza con los resultados.")

# The two closing paragraphs repeat what has been said: replaced by the hypotheses of the calculation
p_imp = P("Es importante destacar que el análisis del accidente incorpora múltiples hipótesis conservadoras")
p_conj = P("En conjunto, la descripción del accidente base de diseño pone de manifiesto la elevada robustez")
hip = new_para_like(p_imp,
    "Para trasladar el accidente al cálculo de dosis se adoptan las siguientes hipótesis, todas ellas conservadoras: "
    "el inventario es el de equilibrio a la potencia nominal de 320 MWₜₕ, aunque un buque atracado operaría a baja "
    "potencia o estaría parado; todo el término fuente se libera al exterior en las dos primeras horas; no se acredita "
    "la desintegración radiactiva durante el transporte; y la dosis se integra en las peores 2 h para el EAB, en "
    "30 días para la LPZ y en los periodos de la @REF:_RefTab_criterios|Tabla 4@ para las zonas de medidas urgentes. "
    "Con estas hipótesis, las dosis calculadas sobrestiman las que produciría el accidente real.")
p_conj.addnext(hip)
delete_para(p_imp)
delete_para(p_conj)

# Initiating events during the port call
esc_h = P("Escenarios analizados", style="Ttulo2")
port_h = new_para_like(esc_h, "Sucesos iniciadores durante la escala")
esc_h.addprevious(port_h)
body_model = P("A partir del accidente descrito, y en coherencia con los criterios del capítulo")
bullet_model = P("E1, accidente base de diseño. Pérdida total de suministro eléctrico")
port_txt = [
    (body_model, "El accidente de Kairos Power se analiza para una central en tierra. En un buque atracado, la pérdida "
     "total de suministro eléctrico corresponde a la pérdida simultánea de la planta eléctrica del buque "
     "(turbogeneradores y generadores de emergencia) y de la conexión eléctrica a tierra del muelle, y sigue siendo el "
     "suceso que pone a prueba la evacuación pasiva del calor residual. Los demás sucesos propios de la escala se "
     "tratan como sigue:"),
    (bullet_model, "Colisión, abordaje o golpe contra el muelle durante la maniobra o con el buque atracado: pueden dañar "
     "el recinto del reactor, por lo que quedan cubiertos por el escenario E2, en el que no se acredita la retención "
     "del edificio."),
    (bullet_model, "Incendio a bordo o en la terminal: puede inutilizar los sistemas activos y conduce, de nuevo, a la "
     "pérdida de la refrigeración activa del escenario E1. El FLiBe no es inflamable y opera a presión próxima a la "
     "atmosférica."),
    (bullet_model, "Manipulación de combustible: las condiciones de escala del capítulo @REFN:_RefCap_marco|3@ prohíben "
     "las operaciones con combustible en puerto (capítulo @REFN:_RefCap_kp|5@), por lo que se excluyen los sucesos "
     "del sistema de manejo de esferas."),
    (bullet_model, "Inundación o hundimiento en el atraque: la entrada de agua en el recinto del reactor y su "
     "interacción con el FLiBe a alta temperatura quedan fuera del alcance de este trabajo y se proponen como línea "
     "futura, junto con un análisis probabilista de los sucesos de puerto."),
]
prev = port_h
for model, text in port_txt:
    np_ = new_para_like(model, text, lead=model is bullet_model)
    prev.addnext(np_)
    prev = np_

# Scenarios: how E1 credits the building, how E2 is computed
RR("E1, accidente base de diseño. Pérdida total de suministro eléctrico",
   "con las barreras de retención del edificio del reactor operativas",
   "con el edificio del reactor acreditado mediante su factor de atenuación")
RR("E2, escenario envolvente. Mismo término fuente que E1",
   "de modo que no se acredita atenuación en el edificio.",
   "de modo que no se acredita atenuación en el edificio y llega al exterior la actividad que sale del FLiBe.")
e2_p = P("E2, escenario envolvente. Mismo término fuente que E1")
calc = new_para_like(body_model,
    "Los dos escenarios se calculan con la herramienta del capítulo @REFN:_RefCap_herr|12@, que lanza RADTRAD con el "
    "término fuente de cada uno y los mismos juegos de fracciones químicas del yodo, y evalúa cada zona de la "
    "@REF:_RefTab_criterios|Tabla 4@ con el escenario que le corresponde. Como el edificio solo atenúa los yodos y las "
    "partículas, y la actividad liberada está dominada por el tritio, que no retiene, cabe esperar que las dosis de E2 "
    "sean muy próximas a las de E1.")
e2_p.addnext(calc)

C.on_paragraph(port_h, "Apartado nuevo: sucesos iniciadores propios de la escala y cómo se tratan (colisión → E2, "
               "incendio → E1, manipulación de combustible excluida, inundación fuera del alcance).")
C.on_paragraph(hip, "Párrafo nuevo con las hipótesis con las que el accidente pasa al cálculo; sustituye a los dos "
               "párrafos finales, que repetían lo dicho. El edificio se trata ahora igual que en el capítulo 9 (E1 "
               "con su factor de atenuación, E2 sin él); antes el texto decía que su retención era mínima y "
               "contradecía al escenario E1.")
C.on_paragraph(calc, "E2 ya se calcula: la herramienta genera kpfhr_terminofuente_E2.nif (actividad tras el FLiBe, "
               "columna BC del libro de inventario) y lanza RADTRAD para E1 y E2. El edificio solo divide por 2 los "
               "yodos y las partículas; como el tritio domina la actividad (unos 6368 Ci frente a menos de 0,1 Ci del "
               "resto de nucleidos no gaseosos), E2 dará dosis muy parecidas a E1. Habrá que confirmarlo con la "
               "ejecución en Windows.")
