# Análisis de coherencia de la memoria (v6 → v7)

Documento de trabajo que acompaña a `TFM_v7_revisado.docx`. La memoria revisada conserva el original (`TFMhastael6.docx`) intacto. Todas las correcciones de texto van como **cambios controlados** (autor «Claude») y cada punto que necesita una decisión o un dato tuyo va como **comentario**.

## 1. Nuevo índice

| Cap. | Contenido | Origen |
|---|---|---|
| — | Resumen / Abstract / Laburpena *(vacíos)* | nuevo |
| — | Índice | v6 (se regenera al abrir en Word) |
| — | Lista de siglas y acrónimos | nuevo, a partir de `SIGLAS.xlsx` |
| 1 | Introducción | v6 |
| 2 | Objetivos y alcance + *Estructura del documento* | v6 + apartado nuevo |
| 3 | Marco regulatorio (normativa española, OIEA/Euratom, OMI, NRC, práctica internacional, criterios adoptados) | v6 + límites de la NRC traídos del antiguo cap. «Cálculo de dosis» |
| 4 | Selección del reactor | v6 (tabla del catálogo movida al Anexo A) |
| 5 | Descripción técnica del KP-FHR | v6 |
| 6 | Buque de referencia e integración del reactor | v6 |
| 7 | **Marco de cálculo** (cadena de cálculo, criterios, hipótesis, matriz de trazabilidad) | nuevo |
| 8 | Accidente postulado | v6 |
| 9 | Término fuente: liberación de radionucleidos | v6 |
| 10 | Dispersión atmosférica + **formulación de ARCON96 y percentiles de diseño** | v6 + teoría nueva |
| 11 | Cálculo de dosis + **modelo de compartimentos, dosis, formas del yodo y ficheros de RADTRAD** | v6 + teoría nueva |
| 12 | **Desarrollo de la herramienta de cálculo** (PIPELINE + mapa de zonas) | nuevo |
| 13 | Resultados *(vacío)* | v6 |
| 14 | Conclusiones *(vacío)* | v6 |
| — | Bibliografía (campo BIBLIOGRAPHY de Word) | nuevo |
| A | Catálogo de diseños SMR | tabla movida desde el cap. 4 |
| B | Ponderaciones del AHP *(vacío)* | nuevo (el texto citaba un «Anexo X» inexistente) |
| C | Radionucleidos al exterior del edificio | antiguo Anexo 1 |

## 2. Referencias y trazabilidad

- La memoria usaba dos sistemas: campos CITATION de Word ([1]–[12]) y marcas escritas a mano ([R-1]–[R-21]) sin lista de referencias. Ahora **todo son campos CITATION** de Word con una sola numeración por orden de aparición y un campo BIBLIOGRAPHY. Puedes seguir gestionándolas en *Referencias → Administrar fuentes*.
- Se han corregido los autores mal introducidos en el administrador de fuentes (p. ej., «Forum, Generation IV International» → autor corporativo).
- Se han completado las citas vacías `[]` (RG 1.23, NUREG-0800) y la palabra suelta «NUREG» (NUREG/CR-6331).
- La fuente «DTU» (imágenes de Bilbao) no existía en el administrador; se ha creado como *Global Wind Atlas (DTU)*, pendiente de verificar.
- Las fuentes que no se han podido identificar con seguridad aparecen como **[Completar]** o **[Verificar]** en la bibliografía.
- Referencias verificadas y completadas: ARPANSA (informe RB-NPW-66/00, diciembre 2000), DSA-rapport 2021:05 (Brown, Hosseini, Dowdall y Amundsen), informe de consecuencias de Ramsden Dock (Navy Command; DEPZ 690 m, OPZ 4 km) y plan DOSEP de Devonport (DEPZ ≥ 1,5 km, OPZ 5 km). Las cifras del texto coinciden con las fuentes. También completadas: Armada (respuesta del Gobierno al Congreso, 2019; corregido el nombre del GOVRA, Grupo Operativo de Vigilancia Radiológica), nueva cita de Romero Bartumeus (Cuadernos de Gibraltar, 2021) sobre la falta de plan exterior en Rota, metodología de EPZ de NuScale (TR-0915-17772, Rev. 3) y Super Decisions. Después: buques mercantes nucleares → Holbert (J. Nucl. Eng., 2025); Global Wind Atlas → Davis et al. (BAMS, 2023); Super Decisions 2.10. La viñeta del Otto Hahn se ha reescrito con datos comprobables y la del Sevmorput queda marcada por falta de fuente. Laburpena redactado (pendiente de revisión por una persona euskaldun). Retirada la viñeta del Sevmorput. Criterio de 200 rem atribuido a su origen, la NUREG-0396 (nueva referencia), con NuScale como ejemplo de aplicación a SMR. Tabla del OIEA: EPD 50 km e ICPD 100 km confirmados para 100–1000 MWth; la PAZ/UPZ de ese intervalo no se da porque las fuentes discrepan. Quedan pendientes: el año del DOSEP v8.0 y confirmar el origen de la rosa de los vientos.
- La tabla «Cadena de cálculo y trazabilidad metodológica» (cap. 7) relaciona cada etapa con su herramienta, entradas, salidas, documento base y capítulo.
- Las referencias cruzadas a tablas, figuras y capítulos son campos REF y se actualizan solas; se ha reparado la que daba «¡Error! No se encuentra el origen de la referencia».

## 3. Correcciones aplicadas (cambios controlados)

- **Buque**: la introducción hablaba de un portacontenedores que quemaba queroseno; el resto del trabajo usa un metanero (LNG carrier) de vapor. Unificado.
- **Potencia del KP-FHR**: 150 MWe (2×75) en la ficha, 140–150 MWth / 75 MWe en el texto y 320 MWth / 140 MWe en la tabla. Unificado a 320 MWth / 140 MWe. Comprobado que 320 MWth / 140 MWe es el diseño de referencia del KP-FHR en la época de KP-TR-012 (2020); la planta comercial actual de Kairos es 2 × 75 MWe. **Decisión: se adopta 320 MWth**, con la justificación en el apartado de compatibilidad de potencia; la ficha técnica indica una unidad a bordo.
- **Balance de potencia**: el texto daba 110–125 MWth y la tabla 134 MWth; alineado con la tabla.
- **Volumen**: el margen «factor 2,5–3» no salía de los propios rangos; recalculado (2,1–5,0).
- **10 CFR 100.11** no expresa los límites en TEDE (lo hacen 10 CFR 50.34 / RG 1.183); corregido y unificado con el cap. 3 en mSv.
- **ARCON96** sí es un modelo gaussiano (modificado); corregida la frase que decía lo contrario.
- **Accidente postulado**: reproduce el ejemplo del Apéndice B de KP-TR-012; añadida la cita y matizado que los resultados citados son de Kairos.
- Enriquecimientos convertidos en fechas por Excel («10-dic», «03-oct», «oct-20»), la fila del KP-FHR en el catálogo (decía sal combustible y ²³³U) y erratas varias.
- Encabezados en mayúsculas a mitad de capítulo, falsos encabezados en negrita del cap. 3 convertidos en títulos reales, listas sin viñeta, interlineado distinto en el cap. 3 y títulos de tabla «9.x» convertidos en leyendas numeradas.
- Términos unificados: radionucleido, término fuente, FLiBe, «Imagen» → «Figura».

## 4. Puntos abiertos, por prioridad

**Críticos (afectan a los resultados)**

1. ~~**Semividas del inventario**~~ **Corregido** con NUBASE2020 (`datos/nubase2020/`). Al revisarlo aparecieron otros dos errores, también corregidos:
   - **Nombres cambiados:** 16 lantánidos no correspondían a su código ZZAAA (Ce-144 figuraba como «Sm-144», Pm-147 como «Eu-147», Eu-154 como «Dy-154»…), así que se les asignaba la semivida de otro nucleido. El código ZZAAA, comprobado con el PDF de Kairos, manda.
   - **Grupos químicos:** esos mismos nucleidos tenían los factores de atenuación del grupo equivocado (Pm en «Sr, Ba, Eu», Eu en «tierras raras»). Además, Cs-134 y U-236 no tenían factores, porque se trataban como estables. Ahora cada nucleido usa los de su grupo.
   - **Efecto:** la actividad total del núcleo pasa de 6,5·10²⁵ Bq a 1,7·10²¹ Bq. Los nucleidos estables desaparecen del Anexo C, y Cs-134 aparece con una actividad en el exterior del edificio del mismo orden que la de Cs-137.
   - **Ficheros:** `datos/inventario/Calculosfueradelacontencion_NUBASE2020.xlsx` y `datos/inventario/ECC_Calculations_NUBASE2020.xlsx` (los originales se conservan) y `datos/nubase2020/cambios_semividas.csv` (detalle nucleido a nucleido). Se regeneran con `actualizar_semividas.py`.
1b. **Inventario incompleto:** el juego de datos público de Kairos (89 nucleidos de la zona AZ6-RZ1) no incluye yodos radiológicos (I-131, I-133, I-135) ni varios gases nobles de vida corta, que suelen dominar la dosis. Hay que completarlo (p. ej., con ORIGEN) o justificar la omisión.
1c. ~~**Ficheros de inventario de RADTRAD**~~ **Regenerado.** `herramienta/generar_nif.py` crea `kpfhr_terminofuente.nif` con el término fuente atenuado: 42 nucleidos, 346 Ci fuera del edificio (1,08 Ci/MWth a 320 MWth), nombres y semividas de NUBASE2020, grupos de liberación de RADTRAD 1–9 y cadenas de desintegración de NUBASE. `PIPELINE.py` fija la potencia del `.psf` en 320 MWth (la plantilla traía los 3.441 MWth del ejemplo BWR, que multiplicaban el inventario por 10,75) y avisa de los nucleidos sin factores de dosis en el `.inp`.
1d. **Modelo de RADTRAD (pendiente, decisión tuya):** `template_master.psf` es el ejemplo BWR de RADTRAD (contención → edificio auxiliar → ambiente, con `bwr_dba.rft`). Con un término fuente que ya está fuera del edificio hacen falta un `.rft` con fracción liberada 1 para todos los grupos al inicio y un modelo que lo emita al ambiente sin retención adicional. Sin eso, el término fuente se atenúa dos veces.
2. ~~**χ/Q que recibe RADTRAD**~~ **Corregido.** La tabla del `.psf` empieza en t = 0 y usa valores por intervalo (Ec. 105 de KP-TR-012) en lugar de las medias de 0 a t. Si un intervalo sale negativo, se usa la media de 0 a t₂ y queda registrado en el log.
3. ~~**Columnas del `.cfd`**~~ **Corregido.** El `.cfd` tiene 11 periodos (incluido 48 h). El mapeo antiguo leía la columna de 24 h como 12 h y la de 48 h como 24 h. Ahora la columna se toma de la cabecera del fichero o, sin cabecera, del número de columnas, y lo mismo con «TOTAL X/Qs». Queda confirmarlo con un `ISMR.cfd` real; el log dice qué disposición se ha usado.
4. **Ficheros de soporte**: `tid_dba.rft` es un término fuente de reactor de agua ligera (TID-14844) y el `.nif` está normalizado a «i_SMR 530.4 MWth». No son coherentes con el término fuente mecanicista del KP-FHR a 320 MWth.
5. **Tritio**: el cap. 8 lo presenta como contribución dominante, pero no aparece en el inventario.

**Importantes (coherencia del documento)**

6. Escenarios **E1/E2** citados en el cap. 3 que no se definen en el cap. 8.
7. **Criterio C3**: excluye los lechos de esferas, pero el KP-FHR usa esferas; hay que justificarlo.
8. Serie meteorológica de «5 años» construida con un único año desfasando 10 min: no aporta variabilidad interanual y debe presentarse como limitación. Incoherencia en la rotación a 58 m.
9. **AF_FLiBe = 100** sin justificación; KP-TR-012 (Tabla B-4) da factores específicos.
10. Filas desplazadas en el bloque de microrreactores del catálogo y fila del IMSR.

**Pendientes de contenido**: resumen, resultados, conclusiones, Anexo B, figuras de las rosas de los vientos, figura del mapa, fecha de portada.

## 5. Software

- `herramienta/PIPELINE.py`: optimizado (paralelo, sin relecturas) y con una **Fase 4** nueva que llama a `zonas_emergencia.py`.
- `herramienta/zonas_emergencia.py`: calcula los radios del EAB (peores 2 h) y de la LPZ (30 d) con la envolvente de todos los juegos de fracciones de yodo e interpolación logarítmica, y genera `zonas_emergencia.json`, `mapa_zonas.html` (Leaflet + OpenStreetMap, con esquema sin conexión) y `mapa_zonas.png` (requiere matplotlib).
- Uso independiente: `python zonas_emergencia.py psf_batch/postprocess --lat 43.353 --lon -3.086 --rumbo 300`.
- Verificado con ejecutables sustitutos: las salidas de las fases 1–3 son idénticas a las del script original. Falta probarlo con ARCON96 y RADTRAD reales en Windows.

## 6. Segunda ronda de contenido

Añadido a la memoria (cambios controlados, con comentario en cada bloque nuevo):

- **Resumen y abstract** redactados (falta la frase con resultados); laburpena pendiente.
- **Introducción**: antecedentes de los buques mercantes nucleares y cita al catálogo de SMR.
- **Objetivos específicos** OE1–OE6, enlazados a los capítulos.
- **Selección**: citas del método AHP (Saaty) y de SuperDecisions; justificación de por qué el criterio C3 no excluye al KP-FHR (las esferas flotan en el FLiBe, KP-TR-012).
- **KP-FHR**: fuentes de la ficha técnica y de los apartados de seguridad (KP-TR-012, FSAR de Hermes, criterios de diseño FHR de ORNL).
- **Accidente postulado**: apartado «Escenarios analizados» con la definición de E1 y E2 (E2 es una propuesta) y el valor de referencia de Kairos: 7,2 mSv a 335 m, el 98 % por tritio.
- **Término fuente**: apartado «Tritio y alcance del inventario» (≈ 6.400 Ci de tritio según KP-TR-012; faltan los yodos y los gases de vida corta) y comparación del AF_FLiBe con la Tabla B-4 de KP-TR-012.
- **Dispersión**: cita de Pasquill–Gifford y párrafo de limitaciones de la serie meteorológica.
- **Resultados**: estructura con lo que debe ir en cada apartado.
- **Conclusiones**: borrador de las que no dependen de los resultados, limitaciones y líneas futuras.
- Unificado «fuente término» → «término fuente».

**Gases nobles en el FLiBe — corregido (corrección mínima).** La hoja de cálculo atenuaba los gases nobles un factor 100 en el FLiBe, pero KP-TR-012 (Tabla B-4) no les atribuye retención (fracción liberada 1,0), lo que subestimaba su liberación 100 veces (no conservador). Ahora se usa AF_FLiBe = 1 para los gases nobles (Xe-133 y Xe-135 en este inventario) y se mantiene 100 para el resto, que sigue siendo conservador frente a los factores por grupo de Kairos. El Xe-133 en el exterior del edificio pasa de 1,1·10¹¹ a 1,1·10¹³ Bq, y los gases nobles son ahora ~99 % de la actividad liberada. El cambio está en `datos/nubase2020/actualizar_semividas.py` (`fix_noble_gases`) y se refleja en los libros `*_NUBASE2020.xlsx`, el Anexo C y el texto del capítulo de término fuente.

### Revisión de comentarios (última ronda)

- **Directriz Básica (RD 1564/2010):** la memoria decía que el RD 524/2023 la había derogado. No es así: su disposición derogatoria deroga el RD 407/1992 (Norma Básica anterior) y el RD 1378/1985; la Directriz sigue vigente. Corregido. Comprobar el texto consolidado en el BOE antes de entregar.
- **NuScale:** 250 MWth corresponde al módulo US460 (subida de potencia del US600, de 160 MWth). Las dimensiones del recinto usadas en el escalado son las del US600; se supone que el US460 las conserva.
- **«Documento de referencia» de los criterios AHP:** sustituido por la guía de SMART y el TFM de Aldekoa Camba (2025), que usa la misma estructura de 10 criterios y 24 subcriterios.
- **Nota interna sobre el término fuente sobreestimado:** reescrita en tono de memoria.
- **Pendiente:** Anexo B (matrices y pesos del AHP obtenidos con SMART / Super Decisions 2.10) — requiere los datos del autor.
- **Volumen de combustible:** el texto ya indica el valor y su cálculo: cilindro de 120 cm de radio y 309 cm de altura (≈ 14,0 m³, celdas K97–K98 de la hoja). Falta citar de dónde salen esas dimensiones del núcleo.
- **Nucleidos estables en la tabla del inventario:** título corregido y frase aclaratoria. Comentario añadido: la frase «sin pérdida de representatividad» choca con la falta de yodos y gases nobles de vida corta en el inventario.
- **Modelo de RADTRAD adaptado:** `herramienta/template_kpfhr.psf` envía la actividad del compartimento 1 directamente al ambiente (camino sin filtro, 10⁶ cfm, residencia < 30 s; el camino al edificio auxiliar queda con caudal nulo). `herramienta/Defaults/kpfhr_directo.rft` tiene fracción 1 para los 9 grupos, liberada uniformemente en 0–2 h (hipótesis conservadora). `PIPELINE.py` usa ambos por defecto, junto con `kpfhr_terminofuente.nif`. Se conserva `Defaults/MHA.rft` (subido por el autor) como referencia. Falta: `fgr11&12.inp` en `Defaults/` y la ejecución real.
- **Tritio incorporado al término fuente:** `generar_nif.py` añade H-3 con 6.368 Ci (KP-TR-012, Tabla B-1), sin atenuación y en el grupo de gases (RADTRAD lo transporta como gas, igual que Kairos). El `.nif` pasa a 43 nucleidos y ≈ 6.714 Ci (20,98 Ci/MWth a 320 MWth); el tritio es el 95 % de la actividad. `--sin-tritio` lo excluye. **Comprobar que `fgr11&12.inp` tiene factores de dosis para H-3**; si no, añadir 1,73·10⁻¹¹ Sv/Bq (inhalación de agua tritiada, FGR 11). La memoria (apartado «Tritio y alcance del inventario», limitaciones y líneas futuras) ya lo refleja.
- **Capítulo de RADTRAD:** nueva tabla con los parámetros del escenario empleado (inventario, potencia, compartimento, camino, .rft, formas del yodo, factores de dosis, receptores, tasas de respiración y duración). Corregidas las unidades de la lista de entradas: volumen en ft³ y caudal en cfm (o %/día para fugas), que son las que usa RADTRAD.

### Normalización del inventario del núcleo (resuelto)

`datos/rendimientos_fision/comprobar_normalizacion.py` compara la actividad del libro de inventario con la de equilibrio que fija la potencia para los productos de fisión de vida corta (A = Y·F, con rendimientos acumulados ENDF/B-VIII.0 del U-235 y F = P/200 MeV). Para Xe-133, Ba-140, Pr-143, Nd-147 y Pm-149 el libro da **unas 156 veces más** actividad de la que corresponde a 320 MWth (equivale a unos 50 GWth).

Causa probable: las densidades del ECC de Kairos son las del **material combustible (núcleo UCO de las partículas TRISO)**: U ≈ 0,020, O ≈ 0,035 y C ≈ 0,012 átomos/(b·cm), proporción UC₀,₅O₁,₅. El libro las multiplica por el volumen de todo el núcleo (cilindro de 120 × 309 cm, ≈ 14 m³). El volumen coherente con 320 MWth es ≈ 0,09 m³ de material combustible (≈ 0,6 % del cilindro), un orden de magnitud plausible para la fracción de núcleos de TRISO en un lecho de esferas.

Consecuencia: el término fuente de productos de fisión está sobrestimado ≈ 150 veces (el tritio no se ve afectado). Corrección propuesta: normalizar el inventario a la potencia (factor ≈ 1/156) o usar el volumen de núcleos de TRISO del diseño, y con la misma normalización añadir los yodos y gases nobles de vida corta (A = Y·F).

**Aplicado (decisión del autor: normalizar a 320 MWth).** `datos/rendimientos_fision/normalizar_inventario.py` escribe la fracción de material combustible (1/156,1 = 0,64 %) en la celda K99 del libro y multiplica por ella el volumen; añade, debajo del bloque de datos del núcleo, I-131 a I-135, Te-132, Kr-85m, Kr-87, Kr-88, Xe-133m, Xe-135m y Xe-138 con A = Y·F y los factores de atenuación de su grupo; y reconstruye el Anexo C. Resultados en el núcleo: Xe-133 ≈ 1,9·10⁷ Ci (6,0·10⁴ Ci/MWth), I-131 ≈ 7,8·10⁶ Ci (2,4·10⁴ Ci/MWth). El `.nif` pasa a 55 nucleidos y ≈ 6.374 Ci fuera del edificio, de los que ≈ 6 Ci son productos de fisión y el resto tritio. La memoria (cálculo del volumen, «Tritio y alcance del inventario», tabla de RADTRAD, cadena de cálculo, limitaciones y Anexo C) ya lo refleja, con la nueva referencia ENDF/B-VIII.0. `ECC_Calculations_NUBASE2020.xlsx` no se ha normalizado porque la herramienta no lo usa.

- **Factores de dosis:** el `fgr11&12.inp` de RADTRAD (60 nucleidos, subido por el autor) no tenía H-3. `herramienta/completar_inp.py` lo añade (1,73·10⁻¹¹ Sv/Bq por inhalación, agua tritiada, FGR 11; externos nulos) y deja el resultado en `Defaults/fgr11&12.inp` (original en `fgr11&12_original.inp`). `generar_nif.py` excluye del `.nif` los nucleidos sin factores en el `.inp`: 22 nucleidos, ≈ 2 Ci (0,03 % de la actividad liberada; sobre todo Xe-138, Xe-135m y Xe-133m). El `.nif` queda con 33 nucleidos y ≈ 6.372 Ci. Pendiente: verificar el valor del H-3 en la tabla 2.1 de FGR 11.

### Datos meteorológicos (MET01–MET05)

Originales en `datos/arcon/met_original/`; `herramienta/preparar_met.py` genera las copias de `herramienta/` y `datos/arcon/resumen_met.csv`. Correcciones: año de MET01 con dos cifras (sus líneas tenían 31 caracteres y desplazaban las columnas); registro de MET05 etiquetado 251 h23 que era 250 h23; 66–80 direcciones 000 por año escritas como 360; 64–68 horas sin registro por año añadidas con 999/999/99 (o interpoladas con `--interpolar`). Recuperación 99,2–99,3 %. **A verificar con el EXAMPLE.MET de ARCON96:** que el campo de viento es 3+3 cifras (la memoria decía 3+4) y que 999/99 se trata como dato ausente. **Observación importante:** clase A en el 27 % de las horas con 7,3 m/s de media — incoherente (la velocidad se escaló sin cambiar la estabilidad) y potencialmente no conservador. Añadido a la memoria (tabla de calidad, discusión, limitaciones y conclusiones).

### Análisis multicriterio (Anexo B) — pendiente
`datos/ahp/Nuproship.smt` (proyecto SMART subido por el autor) y `datos/ahp/ahp.py`, que reproduce el cálculo AHP (vector propio, CR de Saaty, escalas de valoración idealizadas). **Ese fichero no es el modelo de la Figura 1 de la memoria**: tiene 3 alternativas (SEALER-55, MMR, KP-FHR) en lugar de 5 (faltan IMSR400 y CMSR) y no incluye el subcriterio TRL. Con él el orden es MMR 0,45 > SEALER-55 0,30 > KP-FHR 0,25 (normalizado), es decir, el KP-FHR quedaría último, mientras que en la Figura 1 es el primero (≈ 0,62). CR de los criterios 0,067; algunas escalas de valoración superan 0,10 (Power Scalability 0,19). Hace falta el .smt del modelo con 5 alternativas para redactar el Anexo B.

### Carpeta de ejecución
`ejecucion/TFM_ejecucion/` contiene todo lo necesario para ejecutar en Windows (PIPELINE.py, zonas_emergencia.py, visor, plantilla, MET01–05, Defaults con .nif, .rft e .inp, EJECUTAR.bat y LEEME.txt). Probada de principio a fin con ejecutables simulados (ARCON96 y RADTRAD falsos): las cuatro fases terminan y se genera el mapa. Por defecto: 5 ficheros MET y registro en pipeline.log.
- **Ejecución real (03/11):** ARCON96 terminó con rc=1 en todos los casos. Causa más probable: los registros 999/999/99 añadidos para las horas faltantes (estabilidad fuera de rango). `preparar_met.py` interpola ahora esos huecos por defecto (`--codigo-ausente` para el modo anterior); la memoria lo refleja. La carpeta de ejecución incluye `MET_originales/` para aislar el problema si persiste.
- **Causa real del rc=1 (03/11):** la salida QA de ARCON96 (subrutina METREAD) muestra las columnas que lee: dirección/velocidad a 10 m en 16-18/19-21, estabilidad en 23-24, dirección/velocidad a 58 m en 28-30/31-33. Los MET originales tenían el viento a 58 m una columna antes (y el MET01 todos los campos), así que ARCON96 descartaba la estabilidad de todas las horas del MET01 y de ~64 % en los demás y terminaba con «floating-point error: divide by zero». `preparar_met.py` escribe ahora ese formato (33 caracteres) y comprueba los ficheros leyéndolos con esas columnas: 0 horas inválidas. **Consecuencia:** cualquier χ/Q calculado antes con los MET originales (p. ej. la hoja puente de `datos/arcon/`) leyó mal el viento a 58 m y la estabilidad; hay que rehacerlo.
- **Corrección (03/11, segunda QA):** la primera deducción de columnas suponía que la ejecución de prueba usaba los MET originales; en realidad usaba la versión de 32 caracteres. Comparando hora a hora (8.760 registros) la QA de la versión de 33 caracteres, ARCON96 lee todos los campos una columna más a la derecha: viento a 10 m en 17-19 / 20-22, estabilidad 24-25, viento a 58 m en 29-31 / 32-34. `preparar_met.py` escribe ahora líneas de 34 caracteres (`MET01 0100100   225020 07   267066`) y, en `MET_alternativa/`, la misma información con un espacio inicial por si ARCON96 lee también la fecha desplazada. Pendiente: confirmar con el EXAMPLE.MET de ARCON96.
- **Formato definitivo de los MET (03/11):** el autor aportó `RADTRAD_ENGINE.py`, cuyo `_met_build_line` escribe `" MET01 0100100  2250020 07  2670066"` (espacio inicial, velocidades de 4 cifras). Ese formato explica las 8.760 horas de la QA de ARCON96 (lectura de 4 cifras ignorando blancos), así que `preparar_met.py` lo adopta (manteniendo el norte como 360). Se elimina `MET_alternativa/`. La memoria vuelve a decir que la velocidad ocupa 4 cifras (como el texto original) y da las columnas exactas.
- **Primera ejecución con ARCON96 correcta (03/11):** 43.800 horas válidas (5 × 8.760). Problemas en el Excel puente: la hoja H12h no tiene valores por sector (solo «overall») y, a 40 m, los χ/Q por sector de 24 h en adelante son 5–7 veces los de 1–8 h, lo que no es físico. Sospecha: lectura de columnas del ISMR.cfd real. Pendiente de un ISMR.cfd e ISMR.log reales de un caso por sector. Mientras tanto, `interval_xq` impide que el χ/Q medio de 0 a t crezca con t (lo limita al del periodo anterior y lo avisa en el log). RADTRAD no llegó a ejecutarse (no hay .run.log en las carpetas de los casos).
- **Lectura del ISMR.cfd corregida (03/11):** con un `.cfd` real se ve que ARCON96 escribe la distribución acumulada en dos bloques lado a lado, cada uno con su columna XOQ (`XOQ 1 2 4 8 | XOQ 12 24 96 168 360 720`). `_parse_cfd` suponía un bloque de 11 periodos con 48 h (formato del ARCON96 simulado de las pruebas) y por eso la hoja H12h salía sin sectores y la de 24 h usaba los recuentos de 12 h. Ahora sigue la cabecera columna a columna. Validación: los percentiles del 95 % calculados desde el `.cfd` coinciden con los del `ISMR.log` en los diez periodos (p. ej. 3,725E-01 frente a 3,72E-01 a 1 h; 1,382E-01 frente a 1,38E-01 a 720 h). El ARCON96 simulado del banco de pruebas escribe ya el formato real. **Hay que repetir la fase de ARCON96** (los Excel puente anteriores tienen mal los periodos de 12 y 24 h).
- **Primera ejecución completa de RADTRAD (03/11) y dos errores de formato corregidos:**
  1. *Factores de dosis por posición.* El .o0 avisaba «inventory and dose files are inconsistent»: RADTRAD asigna los factores del .inp por posición, no por nombre, así que con el fgr11&12.inp estándar (60 nucleidos) cada nucleido del .nif recibía los factores de otro (p. ej. Ru-103 con 3,5·10⁻⁷ Sv/Bq). `PIPELINE.inp_for_nif` genera ahora `<nif>_dcf.inp` con los mismos nucleidos y en el mismo orden que el .nif, y el .psf lo usa.
  2. *Columnas fijas.* RADTRAD lee las tablas del .psf en columnas fijas. La tabla de χ/Q tenía un espacio de más al principio y dos de menos en medio: leía χ/Q 100 veces mayores (2,93 en vez de 0,0293) y 12 h como 1,2 h. La línea de fracciones de yodo tenía el mismo problema (0,114 leído como 1,14). Ahora se escriben con la disposición exacta del ejemplo de RADTRAD (pares `    0.0000E+00    1.0954E-01`, 10 filas; fracciones en campos de 13). Comprobado: todas las líneas numéricas del .psf generado tienen una disposición presente en `template_master.psf`.
  Los resultados de la ejecución del 03/11 (≈ 20.000 mSv a cualquier distancia) no son válidos. Estimación a mano con los datos corregidos: ≈ 40 mSv a 16 m en el EAB (casi todo tritio).
- **Segunda ejecución completa (03/11, 11:46):** ARCON96 y RADTRAD sin errores (340 + 20 casos). Dos correcciones: (1) `Sets_Worst2h.xlsx` estaba abierto en Excel, el pipeline guardó `_01` y la fase 4 leyó el fichero viejo; `zonas_emergencia.py` usa ahora el más reciente y descarta el que sea anterior a la serie temporal de la ejecución. (2) A partir de 30 m, los χ/Q de 12 h en adelante seguían saliendo incoherentes. Hipótesis: ARCON96 fija el rango de χ/Q (UPPER/LOW LIM.) por periodo y cada bloque del `.cfd` tiene su propia columna XOQ; `_parse_cfd` empareja ahora cada recuento con la XOQ de su bloque. Pendiente de confirmar con un `.cfd` por sector a 30–40 m.
- **Formato real de la tabla de χ/Q de RADTRAD (03/11, tercera ejecución):** con los `.psf` y `.o0` de dos ejecuciones con espaciados distintos (16 m y 22 m) se ha deducido, fila a fila (19 de 19), cómo lee RADTRAD esa tabla: tiempo en las columnas 4-13, una columna ignorada y χ/Q en las 15-24 (`   0.0000E+00 1.5629E-02`); con cualquier otro espaciado pierde los exponentes (χ/Q leído como su mantisa, 12 h como 1,2 h), lo que daba dosis en dientes de sierra que no bajaban con la distancia. `template_master.psf` tiene ese espaciado erróneo (4 + 4), por lo que la comparación anterior con él no era válida. Las demás tablas (respiración, caminos, sala de control, fracciones) RADTRAD las lee bien con su espaciado actual. El .o0 de 22 m confirma además que ya no aparece «inconsistent» y que cada nucleido tiene sus propios factores de dosis.

### Interfaz gráfica (04/11)
`RADTRAD_GUI.py` (del autor, sin cambios salvo la plantilla por defecto, el número de MET por defecto y la lista de fases) y un `RADTRAD_ENGINE.py` nuevo:
- **Generador de PSF** del autor con dos correcciones: (1) números en campos de 13 caracteres (3 blancos + E10.4) y tabla de χ/Q del EAB/LPZ en el formato de RADTRAD; antes escribía con un solo blanco, como el que hacía perder los exponentes; (2) conversión de unidades: la interfaz pide m³, m³/s y 1/s y RADTRAD lee ft³, cfm y %/día (antes se escribían sin convertir). Comprobación: reconstruyendo `template_kpfhr.psf` con el generador, el .psf que sale del pipeline es idéntico (291 líneas) salvo título y nombres.
- **Modo `--gui-mode`**: traduce los parámetros de la interfaz y llama a `PIPELINE.run()` (ARCON96 → RADTRAD → dosis → zonas y mapa), con MET revisados por `preparar_met.py` (desde ficheros o desde la plantilla Excel), `.nif`/`.rft`/`.inp` de `INPUT/` y resultados en `RUN_N/OUTPUT`. Probado con ARCON96 y RADTRAD simulados en los tres modos (completo, solo RADTRAD con χ/Q previo, solo ARCON96 con MET desde Excel) y con los parámetros que devuelve la propia interfaz abierta en una pantalla virtual.
- `PIPELINE.py` se ha dividido en `main()` (preguntas por consola) y `run(p)`, con `configure()` para las carpetas.
- **Australia: dos referencias nuevas (04/11), solo en TFM_v7_revisado.docx.** En el apartado del accidente de referencia de ARPANSA se cita el manual de Defensa OPSMAN 1, ed. 11 (procedimiento de las visitas y papel del Visiting Ships Panel), y la revisión de 2020 del accidente de referencia (PRJ11100253368-R001). Las tres entradas australianas de la bibliografía llevan ahora su URL. La numeración pasa a ser [20] OPSMAN 1, [21] ARPANSA 2000 y [22] revisión 2020, y desde la antigua [21] todo se desplaza dos números. Pendiente: año de la edición 11 del OPSMAN 1 y autor de la revisión de 2020. La versión limpia se ha regenerado después junto con los cambios de formato.
- **Formato (04/11), en las dos versiones:**
  - **Portada** según la de la solicitud de defensa: «Máster Universitario en Ingeniería Industrial», «Trabajo Fin de Máster», título con «radiológica» (con tilde), director Antonio César Hueso Ordóñez, curso 2026-2027, fecha Bilbao, 22 de octubre de 2026, iconos de los ODS 3, 7, 9, 11 y 13, y logo nuevo EHU / Bilboko Ingeniaritza Eskola.
  - **Índices de figuras y de tablas** añadidos tras el índice general, como campos TOC sobre los pies «Figura» y «Tabla». Los números de página aparecen al actualizar los campos.
  - **Secciones:** la portada es una sección propia, sin número. El resto lleva el logo en el encabezado y el número de página en el pie, empezando en 1 en el Resumen. Cada anexo es una sección con su propia numeración (Anexo A – 1, Anexo B – 1, Anexo C – 1).
  - **Capítulos:** cada capítulo (Título 1) empieza en página nueva. Se han quitado los 10 saltos de página manuales que había delante para no dejar páginas en blanco, pero se mantiene la página en blanco entre la portada y el Resumen (está dentro de la sección de la portada y no lleva encabezado ni número).
  - **Tablas:** las 24 tablas tienen el formato de la Tabla 1 (cabecera 1F3864 con texto blanco en negrita, bordes grises de 0,5 pt, 9 pt; 8 pt en el catálogo del Anexo A y en la muestra de datos meteorológicos). La cabecera se repite en cada página y las filas no se parten. Las tablas de hasta 30 filas se mantienen enteras en una página y unidas a su título.
- **Tabla 5 y versión limpia (04/11):** la columna «Código» de la Tabla 5 pasa de 0,74 a 1 cm de ancho para que la cabecera quepa en una línea; el ancho sale de la columna de descripción. La versión limpia se genera ahora aceptando los cambios directamente en el XML, sin pasar por LibreOffice. LibreOffice renombraba los estilos (Ttulo1 → Heading1), rehacía los encabezados y perdía los saltos de página y la página en blanco. El texto resultante coincide con el de la versión revisada con los cambios aceptados; la única diferencia es que ya no quedan la viñeta vacía y la tabla antigua del Anexo C, que estaban borradas.
- **Selección del reactor: cribado revisado (04/11), en las dos versiones.**
  - **C2 con umbral:** excluye los sistemas primarios presurizados (más de 1 MPa: agua y helio). Antes no tenía valor y los reactores de agua aparecían como C6 aunque el C2 se aplica antes. Actualizada también su fila en la Tabla 5.
  - **Asignaciones:** los reactores de agua y de helio pasan a C2. El C3 se aplicaba también a HTGR prismáticos (GTHTR300, GT-MHR, HTTR, HTR50S, HTGR-POLA, MHR-100, MHR-T) y a reactores rápidos de helio (EM2, FMR) que no son de lecho de esferas. CALOGENA (piscina a baja presión) queda en C6. Otros cambios:
    - MMR, Jimmy, AMR, HOLOS y Pylon D1: C2;
    - Aurora: C1 (sodio);
    - Stellarium y XAMR: C1 (cloruros);
    - LFTR: C10 (U-233);
    - ThorCon: C4 (módulo de 4 años);
    - BREST-OD-300 y LFR-AS-200: C10 (plutonio); antes BREST era C9, mientras SEALER-55, también de plomo, pasaba;
    - Energy Well, Flex Reactor y CA Waste Burner: C5;
    - Thorizon: C11.
  - **Candidatos:** quedan 4 (KP-FHR, CMSR, SEALER-55 e IMSR-400); el MMR sale.
  - **Pendiente:** repetir el AHP en SMART sin el MMR y sustituir la Figura 1 (comentario en el texto).
  - **Tabla 6 fuera del cuerpo:** el texto solo nombra los candidatos y remite al Anexo A, que ahora incluye la tabla «Primer criterio de exclusión de cada diseño», con la justificación de los 70 diseños.
  - **Catálogo del Anexo A corregido:** datos desplazados o mezclados entre filas en los bloques de sales fundidas y de microrreactores (IMSR, LFTR, Stellarium, ThorCon, Thorizon, XAMR, AMR, Aurora, ELENA, Energy Well, eVinci, Jimmy, MoveluX, Pylon D1, SHELF), Blue Capsule (< 5 % en vez de 0,05), CMSR (LEU < 5 %), BREST-OD-300 (nombre completo) y tres filas sin nombre eliminadas.
  - **Fuentes:** prensa técnica y fabricantes; el catálogo del OIEA no era accesible. Quedan por confirmar el enriquecimiento de ELENA y de Energy Well, el tipo del AMR y la sal de Thorizon.
- **AHP final (04/11), en las dos versiones.** Modelo de SMART con 4 candidatos: `datos/ahp/TFM_KP-FHR_4alternativas.smt`, sin el MMR. La única calificación cambiada es el «Refueling Time» del IMSR-400 (pasa a «Online Refueling»).
  - **`ahp.py`** reproduce los resultados del motor de SMART: KP-FHR 0,618 (39,8 %), SEALER-55 0,434 (28,0 %), IMSR-400 0,274 (17,7 %) y CMSR 0,226 (14,6 %).
  - **Figura 1** sustituida por la del modelo final, con su texto alternativo corregido. Las puntuaciones se citan ahora en el texto, y la lista de subcriterios incluye la madurez tecnológica (TRL), que está en el modelo.
  - **Anexo B rellenado:** método, consistencia, pesos de criterios y subcriterios, calificaciones de cada candidato y puntuación global.
  - **Avisos en un comentario del Anexo B:**
    - escalas de calificación con CR > 0,10 (Escalabilidad de potencia 0,187; Corrientes de residuos, Seguridad del combustible y Término fuente 0,126; Factores operativos limitantes 0,101);
    - la escala de TRL no distingue niveles (todas las comparaciones valen 1);
    - en la escala de «Licensing Initiated», «Work in Progress» puntúa más que «Started»;
    - la ventaja del KP-FHR viene sobre todo de «Approved» (0,180 de 0,618);
    - hay diferencias con el Excel de calificaciones, aunque alineándolas el KP-FHR sigue primero;
    - errata en la escala de peso («500-100 t»).
- **AHP: escalas corregidas (04/11).** El modelo final es `datos/ahp/TFM_KP-FHR_final.smt`. Cambios respecto a `TFM_KP-FHR_4alternativas.smt`:
  - la escala de TRL era plana (todas las comparaciones valían 1) y ahora es monótona;
  - en «Licensing Initiated» el orden queda Approved > Started > Work in Progress (antes estaba invertido entre las dos últimas);
  - las cinco escalas con CR > 0,10 se han rehecho con comparaciones consistentes (3, 9, 3); ahora todas las escalas tienen CR ≤ 0,093;
  - errata de la escala de peso corregida («500-1000 t»).
  - **Resultado:** KP-FHR 0,623, SEALER-55 0,434, CMSR 0,216 e IMSR-400 0,193.
  - **Figura 1** rehecha con el estilo de SMART (`datos/ahp/figura1.py`).
  - **Anexo B:** añade la justificación de «Approved» (permiso de construcción de Hermes, NRC, diciembre de 2023) y dos casos de sensibilidad, en los que el KP-FHR sigue primero. El caso combinado, en el que el SEALER-55 quedaría primero, se avisa en un comentario.
- **AHP con el informe de SMART (04/11).**
  - **`ahp.py`** usa ahora los índices aleatorios de SMART, deducidos de su `Report.html`, y reproduce sus razones de consistencia: 0,047 en criterios, como máximo 0,094 en subcriterios y 0,096 en escalas.
  - **Escalas:** se han rehecho otras cuatro que SMART marcaba con 0,110 (Operational Experience, Need for Specific Equipment, Component Qualification y Type), manteniendo su orientación. IMSR400 pasa a llamarse IMSR-400.
  - **Resultado final:** KP-FHR 0,639, SEALER-55 0,449, CMSR 0,222 e IMSR-400 0,199.
  - **Capítulo de selección:** nueva figura de pesos (la del informe de SMART) con su comentario, Figura 2 (ranking) actualizada y un párrafo que explica el resultado por criterios.
  - **Anexo B:**
    - método, consistencia, justificación y sensibilidad (0,524 frente a 0,449 y 0,506 frente a 0,435);
    - tablas de la matriz de criterios, pesos, intensidades de las escalas, calificaciones y puntuación;
    - figura con el reparto de la puntuación de cada candidato.
  - **Pendiente:** cargar `TFM_KP-FHR_final_v2.smt` (el mismo modelo, renombrado para no confundirlo con la versión anterior) en SMART y regenerar su informe para que coincida.
- **Capítulo 5, descripción técnica del KP-FHR (04/11), revisado frente a KP-TR-012, en las dos versiones.**
  - **5.2.5:** contención funcional (no hay contención estanca de tipo LWR), con las mismas barreras que el término fuente del capítulo 9.
  - **5.2.4:**
    - el FLiBe retiene los productos de fisión; antes decía que su interacción era «limitada»;
    - el tritio se produce en el FLiBe y se difunde al circuito intermedio.
  - **5.2.2:** los dos sistemas de evacuación del calor residual permiten la parada segura sin alimentación eléctrica, que es la función que pone a prueba el accidente postulado.
  - **5.2.3:** «no se postula una fusión del núcleo como en los LWR», en lugar de «se elimina el concepto de core melt».
  - **5.3.2:** circuito intermedio de nitratos y ciclo de vapor, compatible con la turbina de vapor del buque.
  - **5.3.3:** la recarga en línea es continua; antes se decía que se reducían las recargas. Además, las escalas prohíben las operaciones con combustible en puerto.
  - **Tabla 6:**
    - espectro neutrónico (antes «Tipo de reactor» aparecía repetido);
    - HALEU, porque «LEU+» se refiere al 5–10 %;
    - esferas (pebbles), recarga en línea, parada sin alimentación eléctrica, dos sistemas de evacuación del calor residual y contención funcional.
  - **Citas de 5.2 y 5.2.4:** colocadas antes de los dos puntos.
  - **Pendiente de fuente:** 140 MWe, grafito IBIDEN ET-10, acero 316H y barras de control con SCRAM.
- **Capítulo 6, buque de referencia (04/11), en las dos versiones.**
  - **Demanda térmica:** los 134 MWₜₕ son una cota superior. Suman toda la potencia eléctrica instalada y superan los 97–116 MWₜₕ que dan las calderas.
  - **Acoplamiento:** el reactor se acopla a la turbina de vapor existente mediante el circuito intermedio y un generador de vapor; con 650 °C a la salida del reactor se puede producir el vapor actual, a 515 °C.
  - **Sobredimensionamiento:** es conservador para las zonas de emergencia, porque el término fuente se calcula a 320 MWₜₕ.
  - **Escalado con el NuScale:** se acota como orden de magnitud. Se añade la comprobación de la altura: el módulo NuScale mide 23,2 m frente a 18–20 m libres, pero su altura se debe a los componentes integrados en la vasija.
  - **Alcance:** el peso, la estabilidad, el blindaje y las sociedades de clasificación pasan a líneas futuras; la introducción ya no los anuncia.
  - **Correcciones menores:** texto alternativo de la Figura 3, «Valor típico» → «Valor» y fila de altura de la tabla de volúmenes.
- **Tablas y sus pies (04/11).**
  - Las tablas de hasta 15 filas se mantienen enteras junto a su pie.
  - Las más largas se pueden partir, pero el pie siempre va con las tres primeras filas y la cabecera se repite.
  - Antes, una tabla de 16 a 30 filas que no cabía pasaba entera a la página siguiente y dejaba el pie solo; era el caso de la ficha técnica del KP-FHR.
  - El pie de los datos meteorológicos transformados se había separado de su tabla; vuelve debajo de ella, lo que intercambia la numeración de las Tablas 16 y 17.
- **Tablas y pies, segundo ajuste (04/11).** El criterio por número de filas no bastaba: la Tabla 5 tiene 13 filas, pero casi ocupa una página, y Word separaba el pie de la tabla. Ahora se estima la altura de cada tabla a partir del texto de sus celdas. Las que ocupan menos de media página se mantienen enteras con su pie. Las más altas se pueden partir entre filas: el pie va siempre con las dos primeras filas y la cabecera se repite.
- **v8 (04/11): nueva base.** `TFM_v8.docx` es la versión del autor, con sus cambios hasta el marco de cálculo. Desde ella, cada revisión se aplica con control de cambios y se generan `TFM_v8_revisado.docx` y `TFM_v8_limpia.docx` (scripts en `memoria/scripts`).
- **Capítulo 8, accidente postulado (04/11), sobre la v8.**
  - **Edificio del reactor:** se trata como en el capítulo 9 (E1 con su factor de atenuación, E2 sin él); antes el texto decía que su retención era mínima.
  - **RVACS:** transfiere el calor por radiación a paneles de agua (KP-TR-012).
  - **Tritio:** liberación instantánea, como en Kairos. Su papel dominante se presenta como resultado del ejemplo de Kairos.
  - **Párrafo nuevo con las hipótesis del cálculo:** inventario a 320 MWₜₕ, liberación en 2 h, sin desintegración y periodos de integración de la Tabla 4. Sustituye a los dos párrafos finales, que repetían lo dicho.
  - **Apartado nuevo 8.1, sucesos iniciadores durante la escala:**
    - pérdida de la planta eléctrica del buque y de la conexión a tierra;
    - colisión → E2;
    - incendio → E1;
    - manipulación de combustible excluida;
    - inundación fuera del alcance.
  - **E2 calculado por la herramienta:** con `kpfhr_terminofuente_E2.nif`. Como el edificio solo divide por 2 los yodos y las partículas y domina el tritio, se espera E2 ≈ E1; hay que confirmarlo con la ejecución.

## v8 — Auditoría de los capítulos 7–12: categorías A, B y D + sensibilidad meteorológica

Aplicado sobre `TFM_v8.docx` con control de cambios (`memoria/scripts/cap7_12.py`):

- **Cap. 7**: área del edificio 0,01 m² (sin estela) en los parámetros de ARCON96; las zonas de la Tabla 4 se evalúan con la misma cadena; filas de la Tabla 11 al día.
- **Cap. 9**: AZ6-RZ1 descrita con los datos reales (no es la zona máxima: puesto 3–15 de 40, +4 % Cs-137, +7 % Pu-239, +21 % Xe-133/Ba-140); «vida media» → «periodo de semidesintegración»; f = 1 (la liberación va en los AF de cada etapa del combustible); párrafo nuevo sobre el AF del edificio y los inventarios E1/E2.
- **Cap. 10**: χ/Q en s/m³; Tabla 13; estabilidad leída por clase (ARCON96 no la calcula); ventana de direcciones y área del edificio de 0,01 m² en lugar de las categorías frontal/paralela/oblicua; periodos sin 48 h; nueve intervalos y salvaguardas del cálculo; giro de 58 m (180° y 90° antihorario = 90° horario) en el texto y en la Tabla 14; la recomendación se cambia por el caso de sensibilidad (clase F, 1 m/s).
- **Cap. 11**: «dosis efectiva»; la ley de Henry se atribuye a Kairos y no se usa aquí; plazo de la LPZ explicado (la nube pasa antes de las 2 h de emisión).
- **Cap. 12**: módulos, Tabla 20, escritura de ARCON96 en dos bloques, E2 en la fase 2, evaluación de las zonas de la Tabla 4, visor, sensibilidad (`sensibilidad_met.py`, SENS_F1) y verificación (cuatro errores de formato corregidos en la ejecución real; queda pendiente RADTRAD con la χ/Q corregida).
- Textos alternativos de las figuras descriptivos; erratas.

Herramienta: `sensibilidad_met.py` (MET01 de 8760 h, clase F, 1 m/s) por consola o con la casilla de la interfaz; resultados en `OUTPUT/SENS_F1`.

Pendiente: ejecución en Windows (E1, E2, SENS_F1), capítulo de resultados y reescritura del capítulo 7.

- Velocidad del viento: el autor confirma que son medias horarias, no rachas. Cabeceras de la Tabla 16 «Velocidad máxima» → «Velocidad media» (10 y 58 m) y frase en el apartado 10.4.1.

## Ejecución del 5-11-2026 (ARCON96): lectura del ISMR.cfd corregida

- Resultados de ARCON96 coherentes: χ/Q decrece con la distancia (pendiente −1,8 a −1,9) y con el periodo; el «Maximmum Overall» coincide con el P95 de ARCON96; el P99,5 de 0–2 h coincide con el eje de la pluma en clase F y 2 m/s calculado con las fórmulas de ARCON96 (Pasquill–Gifford + meandro de NUREG/CR-6331).
- Error encontrado: en 35 pares distancia–sector (30, 110, 130 y 370–470 m) el P99,5 de 12–720 h salía 10 veces mayor. ARCON96 fija el rango de la distribución por periodo (UPPER/LOW LIM. del ISMR.log) pero el ISMR.cfd imprime la columna XOQ de un solo periodo; cuando el máximo de 12 h baja una década, el bloque 12–720 h se leía con la escala de 1 h. Divididos por 10, los 35 casos decrecen con el periodo, quedan por encima del P95 del log y el cociente 12 h/8 h (0,73–0,80) es el de los pares sin error.
- Corrección en PIPELINE.py: la escala de cada periodo se reconstruye con los límites del ISMR.log (N intervalos logarítmicos), y en cada caso se compara el P95 obtenido del CFD con el de ARCON96 (aviso si difieren más de un 10 %).
- Efecto: 0–2 h (EAB) sin cambios; en 12–720 h pasa a gobernar el P95 global en todas las distancias. El tope de monotonía del pipeline había evitado que el error llegara a RADTRAD, pero dejaba la χ/Q de 8 h en todos los periodos largos de esas distancias (conservador para la LPZ).

## Ejecución con la lectura del CFD corregida (10–400 m cada 10 m, un juego de fracciones)

- χ/Q: sin saltos; decrece con la distancia (pendiente −1,8 a −1,95) y con el periodo; 1–2 h gobierna el P99,5 del sector (1,03–1,09 × P95 global) y desde 12 h el P95 global. Tabla del .psf idéntica a la prevista (110 m: 7,42e-4 · 5,73e-4 · … · 3,12e-4 · 2,86e-4 s/m³).
- RADTRAD lee bien el χ/Q: TEDE/χ/Q(0–2 h) = 1418,1 mSv·m³/s en las 40 distancias (dispersión 0,01 %). A mano, solo H-3 por inhalación (6368 Ci, 3,5e-4 m³/s, 1,73e-11 Sv/Bq): 1427 (−0,6 %).
- El tritio domina: TEDE/dosis de nube = 278. Las fracciones de yodo y el AF del edificio (E2) apenas cambian la TEDE.
- Radios (E1, TEDE de las peores 2 h; la emisión acaba a las 2 h, así que 48 h y 7 d ≈ 2 h): EAB/LPZ ≤ 10 m, evacuación ≈ 14 m, confinamiento y planificación ≈ 34 m, deterministas ≤ 10 m. Todos dentro de la eslora del buque (284 m).
- Mapa: zonas centradas en el reactor, a popa (28 m de la popa por defecto, centro de la zona de máquinas de 30–35 m del capítulo 6), a 114 m del centro del buque. Visor, vista esquemática y mapa_zonas.png; memoria (cap. 12) actualizada.
- Interfaz: pestaña «Mapa de zonas» (mapa_tab.py) con selector de ejecuciones (caso base y SENS_F1), radios recalculados al cambiar los límites, buque y reactor a escala (vista Tk sin conexión) y mapa completo en el navegador servido en localhost. zonas_emergencia.py importa numpy/pandas solo si están (la pestaña no los necesita) y añade radio_registros(). Memoria (cap. 12) actualizada.
- Pestaña «Mapa de zonas»: cartografía real dentro de la interfaz (teselas OpenStreetMap / Esri en Web Mercator, descargadas en segundo plano con caché en cache_teselas/), cuadrícula de latitud y longitud, coordenadas del cursor (decimal y GMS) y distancia al reactor, clic derecho para situar el buque. Probado con un servidor de teselas local (PNG y JPEG).

## Memoria completa: resultados, conclusiones y anexos D–F (`memoria/scripts/cap13.py`)

- Cap. 13 completo con la ejecución de noviembre: χ/Q de diseño (Tabla 21, Figura 16; sector SE, pendiente −1,9; coincide con F a 2 m/s), dosis (Figura 17; TEDE/χQ = 1418 mSv·m³/s, dispersión 0,01 %; H-3 99,4 %; E2 +0,23 %), radios (Tabla 23, Figuras 18 y 19), comparación con los referentes y con Kairos (χ/Q implícito ×48), sensibilidad (Tabla 24; clase F estimada con las expresiones de ARCON96 y comentada como pendiente de SENS_F1).
- Cap. 14: conclusión principal, apartados nuevos «Sobre las zonas de emergencia en el puerto de Bilbao» y «Sobre las condiciones de escala», herramienta, limitaciones y líneas futuras.
- Cap. 3: Tabla 3 con los radios; sensibilidad hecha; Directriz «no proceden de una caracterización radiológica». Cap. 7: escenarios y anexos, hipótesis de punto de emisión y término fuente. Cap. 12: figura de la pestaña de mapa y verificación con los códigos reales (quinto error). Resumen, abstract y laburpena completados.
- Anexos D (ficheros de entrada de RADTRAD: inventarios E1/E2, .rft, .psf, factores de dosis), E (χ/Q de diseño y por intervalo de las 40 distancias) y F (manual de usuario), cada uno en su sección con pie «Anexo X – n».

## Versión 9 (`memoria/scripts/v9.py`, base `TFM_v8_limpia_2.docx` del autor)

- Maquetación: Tablas 15 y 16 (cap. 10) eran flotantes; ahora en línea, con la leyenda encima y sin partirse. El diagrama de flujo del final del cap. 11 (sin leyenda) se redibuja (tildes, χ/Q, todas las zonas) y pasa al apartado 7.1 como Figura 6, aclarando que la herramienta lo resuelve con un barrido. Lista de criterios del AHP con los subcriterios sangrados.
- Coherencia: resumen (ES/EN/EU) y OE6 con todas las zonas; objetivos («accidente base de diseño», no «daño al núcleo»; meteorología adaptada; sin «corredores marítimos»); Directriz y EPR-NPP (PAZ 0,5–3 km, UPZ 5–15 km para 100–1000 MWth); Tabla 4 con EAB y LPZ; sensibilidad «todas las horas»; uso de E1/E2 según la Tabla 4; cap. 8 remite a los resultados; lectura del CFD en el cap. 12 con la reconstrucción de escala; párrafo largo del mapa dividido.
- Referencias: la Figura 3 citaba la [6] (RD 524/2023) en lugar de la [32] (Naviera Elcano); «y . et al.» en [36], [41] y [49] corregido en las fuentes; citas detrás del punto; dobles espacios.
- Erratas y estilo: Arcon96, HERMES, i.e., «en base a», «monitoreo», «costos», «data centers», «antihoraria», «atmósferica», «Isotopo», «de el», «operadory», tiempos verbales de los caps. 10 y 11, X/Q → χ/Q, etc.

## Versión 10 (`memoria/scripts/v10.py`, base `TFM_JGL.docx` del autor)

- Tablas: las 37 tablas de datos con el mismo formato (fuente del documento a 9 pt —8 pt en las Tablas 34 y 35, de 10 y 11 columnas—, cabecera 1F3864 con texto blanco en negrita repetida, cuerpo negro sin negrita salvo las filas de categoría sombreadas, interlineado sencillo, márgenes 60/90, bordes 999999, alineación vertical centrada, texto a la izquierda y valores numéricos centrados). Excluidas la bibliografía y el listado del .psf. Anchos corregidos en las Tablas 11, 15 y 25 (palabras partidas) y línea en blanco tras las Tablas 15 y 16.
- Notación X/Q del autor: restos del reemplazo (XX/Q, XXX/Q, «(, en Bq/m³», TEDE/Q, TEDE/X/Q), ecuaciones y Figuras 6 y 17 pasadas a X/Q.
- Otros: IAEA → OIEA en la Tabla 25, «input» en la Figura 15, m3 → m³ en el Anexo B.

## Versión 11 (`memoria/scripts/v11.py`, segunda pasada sobre `TFM_JGL.docx`, tras v10.py)

- Todas las tablas y figuras se citan en el texto (faltaban las Tablas 1, 2, 9, 10, 14, 15 y 18 y las Figuras 3 y 14).
- Siglas: añadidas EPR-NPP, GSR, HT/HTO, INL, JFD, MCNP, OPSMAN, PAVAN, PENAR, SCRAM, SMART, SNAP y TFM; eliminada DBA (sin uso).
- Coherencia: MWth/MWe/MWt → MWₜₕ/MWₑ; punto de miles (1.000 MWₜₕ, 1.418 mSv·m³/s, 6.368 Ci, Tabla 22); «puerto de Bilbao», «Directriz básica», «zona de baja población», «límite del área de exclusión» y «sala de control» en minúscula; «Kairos» → «Kairos Power».
- Comprobado: las 49 referencias bibliográficas se citan y tienen fuente; las referencias [28], [34] y [46] no tienen año (pendiente del autor).
