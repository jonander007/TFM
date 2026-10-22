# TFM — Zona de protección en emergencias para buques de propulsión nuclear en el puerto de Bilbao

Máster Universitario en Ingeniería Industrial (EHU) · Jon Ander Goiti Larrinaga

El trabajo define las zonas de emergencia (EAB y LPZ) alrededor de un metanero con un reactor KP-FHR atracado en el puerto de Bilbao. La cadena de cálculo es: inventario del núcleo → término fuente mecanicista → dispersión atmosférica (ARCON96) → transporte y dosis (RADTRAD) → radios de las zonas sobre el mapa.

## Estructura

| Carpeta | Contenido |
|---|---|
| `memoria/` | `TFM_v7_revisado.docx` (versión de trabajo, con cambios controlados y comentarios), `TFMhastael6.docx` (versión original) y `ANALISIS_COHERENCIA.md` (estado de la revisión y puntos abiertos). |
| `herramienta/` | Herramienta de cálculo. `PIPELINE.py` encadena ARCON96, RADTRAD, el postproceso y el mapa; `zonas_emergencia.py` calcula los radios del EAB y la LPZ y genera el mapa; `visor_zonas.html` es la interfaz del mapa. Junto a ellos están las entradas que el pipeline busca en su carpeta (plantilla `.psf` y ficheros de inventario `.nif`). |
| `herramienta/legacy/` | Scripts anteriores (`NIF.py`, `RADTRAD_batch_post_integrated.py`). Su funcionalidad ya está integrada en `PIPELINE.py`; se conservan como histórico. |
| `datos/inventario/` | Inventario del núcleo y término fuente. Los ficheros `*_NUBASE2020.xlsx` son la versión corregida, y los originales se conservan. |
| `datos/nubase2020/` | Tabla NUBASE2020 original, lector `nubase.py` y `actualizar_semividas.py`, que regenera los libros corregidos y deja el registro en `cambios_semividas.csv`. |
| `datos/arcon/` | Hoja puente de χ/Q de un cálculo anterior y plantilla de datos meteorológicos. |
| `referencias/` | Documentos de referencia: metodología de término fuente de Kairos Power (KP-TR-012, revisiones), concentraciones de equilibrio del núcleo, criterios de diseño FHR de ORNL y el TFM de referencia sobre selección de SMR. |

## Ejecutar la herramienta

Requiere Windows con ARCON96 y RADTRAD instalados, Python 3.10 o posterior y `pip install pandas numpy openpyxl matplotlib` (matplotlib es opcional; solo se usa para la imagen PNG del mapa).

1. En `herramienta/`, añade los ficheros meteorológicos `MET01.MET`, `MET02.MET`, … y la carpeta `Defaults` con el `.nif`, el `.rft` y `fgr11&12.inp`.
2. Si los ejecutables no están en `C:\ARCON96\arcon96f.exe` y `C:\RADTRAD\RADTRAD3.03x\Distribution0203\BatchModeVersion\radtrad.exe`, cambia esas rutas al principio de `PIPELINE.py`.
3. Ejecuta `python PIPELINE.py` desde `herramienta/`. Todas las preguntas se hacen al inicio y después el cálculo es desatendido.
4. Abre `psf_batch/postprocess/mapa_zonas.html` para ver el buque con las zonas sobre el mapa.

`zonas_emergencia.py` también funciona por separado sobre unos resultados ya calculados:

```
python zonas_emergencia.py psf_batch/postprocess --lat 43.353 --lon -3.086 --rumbo 300
```

## Antes de los cálculos definitivos

Ver `memoria/ANALISIS_COHERENCIA.md`. Lo principal: regenerar el inventario `.nif` (todavía tiene los nombres de nucleidos sin corregir), completar el inventario con los yodos y gases nobles de vida corta, y usar un `.rft` coherente con el término fuente del KP-FHR.
