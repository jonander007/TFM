# Registro de cambios v12 (revisión técnica externa)

Base: `TFM_JGL.docx` + v10 + v11. Salidas: `TFM_v12_revisado.docx` (control de cambios y comentarios) y `TFM_v12_limpia.docx`.
Al insertar la nueva tabla de escenarios (Tabla 12), las Tablas 12–35 de v11 pasan a ser 13–36: los «Tablas 23–24» de la revisión son ahora las **Tablas 24 (radios) y 25 (sensibilidad)**. Las referencias cruzadas se renumeran solas.

Estados: **corregido** (redacción o criterio), **recalculado y verificado** (cifra rehecha a partir de los resultados de la herramienta o del cálculo manual), **pendiente de datos** (hace falta una fuente o un cálculo que no existe en el trabajo).

## P0 · Dosimetría y criterios

| Ubicación | Cambio | Motivo | Evidencia | Estado |
|---|---|---|---|---|
| Tabla 24, filas deterministas | Magnitud «dosis absorbida en médula, 1 Gy / en tiroides, 5 Gy»; radio «No evaluado» | La TEDE (mSv) no puede compararse con umbrales en Gy | La herramienta no calcula dosis absorbida | corregido |
| Cap. 13, párrafo nuevo tras los radios | Cota: con wR = 1, la dosis absorbida en 48 h ≤ dosis equivalente comprometida ≈ 0,1 Sv a 10 m, así que < 0,1 Gy, al menos 10 veces por debajo de los umbrales | Sustituye la afirmación «99,6 mSv demuestra la ausencia de efectos deterministas» | Tiroides ≈ 101–103 mSv a 10 m; el HTO se reparte de forma uniforme | recalculado y verificado (cota) |
| Cap. 12, «Cada zona de la Tabla 4…» | Los contornos de 1.000 mSv TEDE y 5.000 mSv tiroides pasan a ser «indicadores de cribado», no dosis absorbida | Coherencia con la Tabla 24 | Etiquetas cambiadas también en `herramienta/zonas_emergencia.py` (DETM, DETT) | corregido |
| Cap. 3, NUREG-0396 | «200 rem (2 Gy) a cuerpo entero» → «200 rem a cuerpo entero» | La equivalencia rem→Gy no es válida | — | corregido; texto literal de NUREG-0396 **pendiente de datos** |
| Cap. 3, criterios de emplazamiento | EAB en «cualquier periodo de 2 h tras el inicio»; LPZ «durante todo el paso de la nube», con 30 días como horizonte de cálculo; nota sobre 10 CFR 50.67 y 100.11; aplicación a un buque como referencia metodológica | Formulación exacta de RG 1.183 | Comentario en el documento | corregido; alcance de 50.67 y revisión de RG 1.183 **pendiente de datos** |
| Tabla 4 | Cuatro familias: Emplazamiento (NRC); Intervención (Directriz: evacuación 50 mSv evitable en 7 días, confinamiento 10 mSv en 2 días, yodo 100 mSv en 7 días como hipótesis; cribado con TEDE proyectada); Planificación (contorno de 10 mSv en 96 h); Dosis absorbida por órgano («no calculada; acotada») | Mezclaba magnitudes y familias de criterios | — | corregido |
| Párrafo tras la Tabla 4 | Vías incluidas (inhalación e inmersión) y excluidas (suelo, ingestión, vía marina); uso de la TEDE para el cribado; Gy no se compara con mSv | Transparencia de magnitudes | — | corregido |
| Tabla 3, Directriz; cap. 3 | «100 m (radio genérico de medidas urgentes)», «100–200 m (corona de alerta)»; definidas por tasa de dosis (5 mSv/h, 100 µSv/h); comparación solo geométrica | No es una zona de evacuación ni de confinamiento por dosis integrada | Directriz básica, foco sin caracterizar | corregido |
| Cap. 13, comparación con referentes | «entre uno y dos órdenes de magnitud» → «entre 2 y 9 veces (evacuación de Barrow) y entre 18 y 56 veces (el resto)» | Cifra real | 30–130 m / 15 m; 630 m–1,9 km / 34 m | recalculado y verificado |
| Cap. 13 y 14, Directriz | Quitado «envuelven con un margen de 4 a 7 veces», «conservadoras para este diseño», «pueden adoptarse como zonas de planificación» | Comparación geométrica; la decisión corresponde a la autoridad | — | corregido |
| Siglas, cap. 8 | TEDE = «equivalente de dosis efectiva total»; párrafo que distingue E (FGR 11 + FGR 12), H_tiroides y D (Gy); rem→mSv una sola vez | Terminología | Cálculo manual del cap. 13 | corregido |

## P1 · Metodología y resultados

| Ubicación | Cambio | Motivo | Evidencia | Estado |
|---|---|---|---|---|
| Cap. 2, tras «En síntesis…» | Párrafo de alcance con lo que queda fuera (maniobras, vías marina y alimentaria, suelo, a bordo, respuesta) | Delimitar el estudio | — | corregido |
| Cap. 5, criterio C1 y Tabla 5 | El sodio reacciona violentamente; las sales cloradas son solubles y corrosivas (no «violentamente reactivas») | Exactitud química | — | corregido |
| Anexo B | «consistentes» → «coherencia interna aceptable (CR < 0,10)» | Precisión del AHP | CR de las matrices | corregido |
| Cap. 5 | El permiso de Hermes no es del diseño comercial KP-FHR | Precisión | — | corregido |
| Cap. 6 | Carga parcial y fatiga como hipótesis; acoplamiento 650/515 °C «necesario pero no suficiente» (faltan presión, caudal, saltos térmicos, rendimientos) | Afirmaciones sin análisis | — | corregido |
| Cap. 8, E2 y nueva Tabla 12 | E2 = «sensibilidad a la pérdida de retención del edificio»; tabla E1/E2 (iniciador, potencia, RVACS, combustible, edificio, vía, .nif, liberación); E2 no modela una colisión real | Escenario no envolvente | Ficheros `kpfhr_terminofuente(_E2).nif` | corregido |
| Cap. 9 | Ejemplo con el Cs-137: N = 1,41·10²⁵ átomos, A = 1,03·10¹⁶ Bq | Trazabilidad densidad → actividad | Anexo C: 1,027E+16 Bq | recalculado y verificado |
| Cap. 9, tritio | 19,90 Ci/MWₜₕ × 320 = 6.368 Ci; sin doble normalización; la absorción cutánea del HTO no se modela aparte | Trazabilidad | Cálculo manual del cap. 13 | corregido; contenido del factor FGR 11 del HTO (absorción cutánea) **pendiente de datos** |
| Cap. 10, meteorología | «cinco series sintéticas derivadas de un mismo año»; quitado «cumplen con los requisitos»; «noroeste–oeste-noroeste»; «predominio de los vientos del sur/del oeste»; dirección de procedencia; qué calcula ARCON96 y qué el posprocesamiento | Exactitud | — | corregido |
| Cap. 14, limitaciones | Efecto de la estela, las recirculaciones y la altura de descarga «de signo indeterminado»; dosis a bordo no calculadas; párrafo final de incertidumbres principales | Campo cercano | — | corregido |
| Tabla 23 | Columna «Fracción del total manual»; RADTRAD = «98,8 % (cociente RADTRAD / manual)»; diferencia del 1,2 % no atribuida | Lectura correcta | 1.418,1 / 1.435,0 | recalculado y verificado |
| Cap. 13, H-3 | Cálculo explícito: 6.368 × 3,7·10¹⁰ × 3,5·10⁻⁴ × 1,73·10⁻¹¹ = 1,427 Sv·m³/s | Trazabilidad | 1.426,7 mSv·m³/s | recalculado y verificado |
| Cap. 13, tiroides | +1,3 % por los factores de los yodos (el del H-3 es igual en todos los órganos) | La explicación anterior era incorrecta | Desglose manual | corregido |
| Cap. 13, radios | Pares de acotación: 15 m entre 10 m/99,6 y 20 m/26,6 mSv; 34 m entre 30 m/12,5 y 40 m/7,2 mSv; «≤ 10 m» es la resolución; yodo ≈ 10 m (101–103 mSv a 10 m, 27 mSv a 20 m); Tabla 24 «≈ 10 m» | Transparencia de la interpolación | Barrido de RADTRAD | recalculado y verificado; radio de yodo con la serie temporal de tiroides **pendiente de datos** |
| Cap. 13, Kairos | 0,716 rem (7,16 mSv) frente a 0,143 mSv: ≈ 50 veces; X/Q implícito 4,9·10⁻³ s/m³ (× 49); atribuirlo todo al X/Q es una hipótesis | Precisión | X/Q propio a 335 m = 1,006·10⁻⁴ | recalculado y verificado |
| Tabla 25 | Fila «X/Q × 49 (sensibilidad uniforme, ejemplo de Kairos Power)»: 48 / 112 / 271 m | Antes × 48: 47 / 110 / 267 m | Interpolación del barrido | recalculado y verificado |
| Cap. 14, conclusiones y condiciones de escala | «En el escenario y con las hipótesis analizadas»; atraque condicionado a la posición y la meteorología; quitado «retirar el buque no reduce su dosis»; yodo decidido por la autoridad; E1 = E2 no demuestra nada sobre una colisión real | Conclusiones proporcionadas a la evidencia | — | corregido |
| Resúmenes ES/EN/EU | Mismas salvedades; criterio EAB/LPZ en «cualquier ventana de 2 h / paso de la nube»; «distancia mínima calculada, 10 m»; Directriz como referencia geométrica | Coherencia con las Tablas 24–25 | Comprobado frase a frase | corregido |

## P2 · Redacción

| Ubicación | Cambio | Estado |
|---|---|---|
| Cap. 10 | «vigilancia meteorológico» → «meteorológica» (cita marcada como traducción propia) | corregido |
| Cap. 10 | «las distancias a las que se sitúan el límite del área de exclusión (EAB) y el límite exterior de la zona de baja población (LPZ)» | corregido |
| Cap. 4, lista de columnas | “ ” → « », «Estado de desarrollo» en lugar de «Status» (también en la cabecera de la Tabla 26) | corregido |
| Tabla 26 y texto | Arabia Saudí, Kairos Power, LLC, TerraPower | corregido |
| Todo el documento | «herramienta software» → «herramienta informática»; «pipeline» → «cadena de cálculo» (Anexo F); «postproceso» → «posprocesamiento» (título de la fase 3 y Tabla 21); «mix energético» → «combinación energética» | corregido |
| Todo el documento | «LNG carrier» → «metanero» (10 apariciones; se mantiene «metanero o LNG carrier» en la primera mención y en el resumen inglés) | corregido |
| Caps. 5–6 | Menos «gran porte», «claramente favorable», «gran flexibilidad», «elevado nivel» | corregido |
| Bibliografía [28], [34], [46] | Faltan los años | pendiente de datos |

## Conclusiones que cambian

1. Ya no se afirma que no haya efectos deterministas «por comparación con la TEDE». Ahora se acotan por debajo de 0,1 Gy, sin haberlos calculado.
2. La Directriz básica deja de presentarse como «zonas conservadoras que envuelven el cálculo». Sus 100/200 m son zonas por tasa de dosis para un foco sin caracterizar, y la comparación es solo geométrica. Su adopción corresponde a la autoridad.
3. Frente a los referentes, la diferencia ya no es «de uno a dos órdenes de magnitud» sino de 2 a 56 veces (de 2 a 9 frente a la evacuación de Barrow).
4. E2 deja de ser «envolvente»: es una sensibilidad a la pérdida de retención del edificio. Que E1 y E2 coincidan no dice nada de una colisión real.
5. Que retirar el buque no reduzca la dosis ya no es una conclusión: depende de los tiempos y de la maniobra, que no se han analizado.
6. Que el atraque sea «adecuado» queda condicionado a la posición y la meteorología adoptadas, y a comprobaciones náuticas, de protección física y de la terminal.
7. El radio de profilaxis con yodo pasa de «≤ 10 m» a «≈ 10 m», justo por encima del nodo de 10 m.
8. Sensibilidad a Kairos Power: × 49 en lugar de × 48, con radios de 48 / 112 / 271 m. Atribuir toda la diferencia al X/Q es una hipótesis.

## Comprobaciones pedidas

- **Resúmenes y Tablas 24–25:** los tres resúmenes dan ≤ 10 m (EAB/LPZ), 15 m (evacuación), 34 m (confinamiento y planificación) y 22/48 m con clase F. Son los valores de las Tablas 24 y 25. Ninguno menciona el yodo ni los efectos deterministas.
- **Gy frente a mSv:** se han revisado todas las apariciones de «Gy» en el texto limpio. Quedan solo en la enumeración de umbrales de la Directriz (cap. 3), en la fila «Dosis absorbida por órgano» de la Tabla 4, en la nota de magnitudes, en la cota del cap. 13 y en las filas «No evaluado» de la Tabla 24. Ninguna compara un umbral en Gy con la TEDE en mSv.

---

# v13 · Repaso final para la entrega en PDF

Salidas: `TFM_v13.pdf` (documento de entrega), `TFM_v13_limpia.docx` y `TFM_v13_revisado.docx`.

| Ubicación | Cambio | Motivo | Estado |
|---|---|---|---|
| Cap. 9 | «En la Tabla 13 se muestra… la sección» → Figura 7 | La renumeración de v12 había cambiado la referencia; comprobadas las 145 referencias cruzadas | corregido |
| Cap. 9 | Figura 7 en línea, antes de la Tabla 13 (antes flotaba a su lado) | El pie pisaba el número de página | corregido |
| Cap. 10 | Figura 15 y su pie en línea | La imagen se salía por el pie de página | corregido |
| Caps. 6, 7, 9, 10, 11, 12 | 19 arreglos en las fórmulas: palabras con tilde, Q̇, DCF, m³, fórmulas en párrafo propio, T₁/₂ | No se dibujaban bien al exportar | corregido |
| Todo el documento | Quitado el resaltado amarillo y el texto en rojo (16 restos) | Restos de edición | corregido |
| Títulos | Más espacio tras la numeración («10.1Conceptos» → «10.1 Conceptos») | Capítulos de dos cifras | corregido |
| Caps. 1–14 | Erratas y redacción: «de la combinación energética», «inventario isotópico», «zonas de emergencia», «fiables», «overlying pool», «necesario abordar», comillas « », 7,16 mSv, «cualquier ventana de 2 horas» | Coherencia | corregido |
| Cap. 13 | «unos 101 mSv a tiroides a 10 m en E1 y 103 mSv en E2»; sin repetir «≤ 10 m» | Claridad | corregido |
| Cap. 14 | «cinco errores del procedimiento inicial», como en el capítulo 12 (antes «dos» y «otros tres») | Coherencia | corregido |
| Cap. 11, Anexos B, D y E | Quitadas las rutas a ficheros y carpetas que no acompañan al PDF | Solo se entrega el PDF | corregido |
| Cap. 12 | Párrafos nuevos: tipo de instalación (embarcación o planta terrestre) y alcance del generador de escenarios; el código no forma parte del documento | Herramienta actualizada | corregido |
| Anexo F | Manual actualizado (tipo de instalación, barra del generador, «Usar en el cálculo», «Guardar posición y criterios») y Figuras 22 y 23 nuevas | Herramienta actualizada | corregido |
| Bibliografía | [46] NUREG-0800 2.3.3, Rev. 3, 2007; [34] «s. f.» | Faltaba el año | corregido; [28] sigue sin año |
| PDF | Índice, lista de figuras y lista de tablas con las páginas reales; anexos como A-1, B-2…; marcadores, título y autor | Entrega en PDF | corregido |

El PDF se genera con `scripts/export_pdf.py` (LibreOffice). La Figura 16 conserva la captura anterior del mapa, en la que el panel se llamaba «Buque»; el texto lo indica.
