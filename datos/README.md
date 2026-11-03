# Datos

- `inventario/`: inventario del núcleo (Kairos Power, zona AZ6-RZ1) y cálculo del término fuente. Los `*_NUBASE2020.xlsx` son la versión corregida.
- `nubase2020/`: semividas de NUBASE2020 y script de actualización.
- `rendimientos_fision/`: rendimientos acumulados de fisión del U-235 (ENDF/B-VIII.0, térmico), comprobación de la normalización del inventario a la potencia y script que la aplica y añade los yodos y gases nobles de vida corta.
- `arcon/`: hoja puente de χ/Q y plantilla meteorológica.

## Regenerar el inventario y el `.nif`

```
python datos/nubase2020/actualizar_semividas.py datos/inventario/Calculosfueradelacontencion.xlsx
python datos/rendimientos_fision/normalizar_inventario.py
# abrir y guardar el libro en Excel/LibreOffice para recalcular las fórmulas
python herramienta/generar_nif.py
```

`normalizar_inventario.py` escribe en la celda K99 la fracción del cilindro del núcleo que ocupa el material combustible (≈ 1/156): las densidades del ECC son las del núcleo de UCO de las partículas TRISO, y multiplicarlas por todo el cilindro daba unas 156 veces la actividad correspondiente a 320 MWth. `comprobar_normalizacion.py` muestra la comparación nucleido a nucleido.
