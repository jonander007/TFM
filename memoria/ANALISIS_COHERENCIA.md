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
- La tabla «Cadena de cálculo y trazabilidad metodológica» (cap. 7) relaciona cada etapa con su herramienta, entradas, salidas, documento base y capítulo.
- Las referencias cruzadas a tablas, figuras y capítulos son campos REF y se actualizan solas; se ha reparado la que daba «¡Error! No se encuentra el origen de la referencia».

## 3. Correcciones aplicadas (cambios controlados)

- **Buque**: la introducción hablaba de un portacontenedores que quemaba queroseno; el resto del trabajo usa un metanero (LNG carrier) de vapor. Unificado.
- **Potencia del KP-FHR**: 150 MWe (2×75) en la ficha, 140–150 MWth / 75 MWe en el texto y 320 MWth / 140 MWe en la tabla. Unificado a 320 MWth / 140 MWe; pendiente de confirmar con la fuente.
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

1. **Semividas del inventario**: en `Calculosfueradelacontencion.xlsx` se usó la columna «chatGPT», con errores graves (U-237: 98 min en lugar de 6,75 d; Am-243: 5 h en lugar de 7.370 años; núclidos estables con 30 años). El Anexo C hereda actividades imposibles (p. ej., 2·10²⁵ Bq de Sm-142). Hay que recalcular con NUBASE2020/ENDF y no citar herramientas de IA como fuente.
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

- `PIPELINE.py`: optimizado (paralelo, sin relecturas) y con una **Fase 4** nueva que llama a `zonas_emergencia.py`.
- `zonas_emergencia.py`: calcula los radios del EAB (peores 2 h) y de la LPZ (30 d) con la envolvente de todos los juegos de fracciones de yodo e interpolación logarítmica, y genera `zonas_emergencia.json`, `mapa_zonas.html` (Leaflet + OpenStreetMap, con esquema sin conexión) y `mapa_zonas.png` (requiere matplotlib).
- Uso independiente: `python zonas_emergencia.py psf_batch/postprocess --lat 43.353 --lon -3.086 --rumbo 300`.
- Verificado con ejecutables sustitutos: las salidas de las fases 1–3 son idénticas a las del script original. Falta probarlo con ARCON96 y RADTRAD reales en Windows.
