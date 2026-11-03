# TFM — Zona de protección en emergencias para buques de propulsión nuclear en el puerto de Bilbao

Máster Universitario en Ingeniería Industrial (EHU) · Jon Ander Goiti Larrinaga

El trabajo define las zonas de emergencia (EAB y LPZ) alrededor de un metanero con un reactor KP-FHR atracado en el puerto de Bilbao. La cadena de cálculo es: inventario del núcleo → término fuente mecanicista → dispersión atmosférica (ARCON96) → transporte y dosis (RADTRAD) → radios de las zonas sobre el mapa.

## Estructura

| Carpeta | Contenido |
|---|---|
| `memoria/` | `TFM_v7_revisado.docx` (versión de trabajo, con cambios controlados y comentarios), `TFM_v7_limpia.docx` (misma versión con todos los cambios aceptados y sin comentarios), `TFMhastael6.docx` (versión original) y `ANALISIS_COHERENCIA.md` (estado de la revisión y puntos abiertos). |
| `herramienta/` | Herramienta de cálculo. `PIPELINE.py` encadena ARCON96, RADTRAD, el postproceso y el mapa; `zonas_emergencia.py` calcula los radios del EAB y la LPZ y genera el mapa; `visor_zonas.html` es la interfaz del mapa. Junto a ellos están las entradas que el pipeline busca en su carpeta: `template_kpfhr.psf` (modelo de emisión directa al ambiente), `template_master.psf` (ejemplo BWR original de RADTRAD) y `Defaults/` (`.nif`, `kpfhr_directo.rft` y `MHA.rft` de referencia). |
| `herramienta/generar_nif.py` | Genera el inventario de RADTRAD (`kpfhr_terminofuente.nif`) a partir del término fuente atenuado del Excel corregido. |
| `herramienta/legacy/` | Scripts anteriores (`NIF.py`, `RADTRAD_batch_post_integrated.py`). Su funcionalidad ya está integrada en `PIPELINE.py`; se conservan como histórico. |
| `datos/inventario/` | Inventario del núcleo y término fuente. Los ficheros `*_NUBASE2020.xlsx` son la versión corregida, y los originales se conservan. |
| `datos/nubase2020/` | Tabla NUBASE2020 original, lector `nubase.py` y `actualizar_semividas.py`, que regenera los libros corregidos y deja el registro en `cambios_semividas.csv`. |
| `datos/arcon/` | Hoja puente de χ/Q de un cálculo anterior y plantilla de datos meteorológicos. |
| `referencias/` | Documentos de referencia: metodología de término fuente de Kairos Power (KP-TR-012, revisiones), concentraciones de equilibrio del núcleo, criterios de diseño FHR de ORNL y el TFM de referencia sobre selección de SMR. |

## Ejecutar la herramienta

Requiere Windows con ARCON96 y RADTRAD instalados, Python 3.10 o posterior y `pip install pandas numpy openpyxl matplotlib` (matplotlib es opcional; solo se usa para la imagen PNG del mapa). `herramienta/Defaults/` ya incluye `fgr11&12.inp` completado con el H-3 (`completar_inp.py`; el original está en `fgr11&12_original.inp`).

1. Los ficheros meteorológicos `MET01.MET` … `MET05.MET` ya están en `herramienta/`, preparados con `preparar_met.py` a partir de los originales de `datos/arcon/met_original/` (un registro por hora, año con dos cifras, norte = 360). La carpeta `herramienta/Defaults/` ya trae el inventario (`kpfhr_terminofuente.nif`), el fichero de liberación (`kpfhr_directo.rft`) y los factores de dosis (`fgr11&12.inp`, con el H-3 añadido); la plantilla por defecto es `template_kpfhr.psf`.
2. Si los ejecutables no están en `C:\ARCON96\arcon96f.exe` y `C:\RADTRAD\RADTRAD3.03x\Distribution0203\BatchModeVersion\radtrad.exe`, cambia esas rutas al principio de `PIPELINE.py`.
3. Ejecuta `python PIPELINE.py` desde `herramienta/`. Todas las preguntas se hacen al inicio y después el cálculo es desatendido.
4. Ejecuta `python ver_mapa.py` (o `VER_MAPA.bat`) para ver el buque con las zonas sobre OpenStreetMap: sirve `psf_batch/postprocess/mapa_zonas.html` en `http://localhost`, porque `tile.openstreetmap.org` no sirve teselas a ficheros abiertos desde el disco. Leaflet 1.9.4 va incluido en `herramienta/vendor/leaflet/` y dentro del propio HTML generado.

`zonas_emergencia.py` también funciona por separado sobre unos resultados ya calculados:

```
python zonas_emergencia.py psf_batch/postprocess --lat 43.353 --lon -3.086 --rumbo 300
```

## Antes de los cálculos definitivos

Ver `memoria/ANALISIS_COHERENCIA.md`. La plantilla `.psf` y el `.rft` ya están adaptados al término fuente atenuado (emisión directa al ambiente, fracción 1 en 0–2 h) y el `.nif` se genera con `generar_nif.py`. El `.nif` incluye ya el tritio (6.368 Ci, KP-TR-012). Lo principal que falta es completar el inventario con los yodos y gases nobles de vida corta.
