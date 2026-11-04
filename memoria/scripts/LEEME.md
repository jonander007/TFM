# Scripts de revisión de la memoria (desde la v8)

- `build_v8.py` parte de `memoria/TFM_v8.docx` (versión del autor), aplica los módulos de cada capítulo
  (`cap8.py`, …) con control de cambios y comentarios, y escribe `TFM_v8_revisado.docx` y `TFM_v8_limpia.docx`.
- `lib.py`: funciones de cambios controlados (inserción, borrado, sustitución, comentarios).
- `limpia.sh` + `accept_xml.py`: aceptan los cambios directamente en el XML y quitan los comentarios.
- Las rutas de trabajo apuntan a la carpeta temporal de la sesión; cópialas a una carpeta propia para reutilizarlos.
