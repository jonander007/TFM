#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RADTRAD_GUI.py  —  Interfaz unificada ARCON96 + RADTRAD + Generador PSF
========================================================================
Requiere RADTRAD_ENGINE.py en la misma carpeta.
Ejecuta: python RADTRAD_GUI.py
"""

import sys
sys.dont_write_bytecode = True  # no genera __pycache__
import json
import re
import os
import shutil
import subprocess
import threading
import tempfile
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path

try:
    import tkinterdnd2
    _DND_OK = True
except ImportError:
    _DND_OK = False

SCRIPT_DIR = Path(__file__).resolve().parent

# Importar motor PSF desde RADTRAD_ENGINE
sys.path.insert(0, str(SCRIPT_DIR))
try:
    from RADTRAD_ENGINE import (
        PSFModel, Compartment, Pathway, DoseLocation,
        TimeValueTable, TimeValue3Table, FilterTable,
        COMP_TYPE_CONTROL_ROOM, COMP_TYPE_ENVIRONMENT, COMP_TYPE_OTHER,
        PATH_TYPE_PIPING, PATH_TYPE_FILTER,
        PATH_TYPE_SUPPRESSION_POOL, PATH_TYPE_AIR_LEAKAGE,
        DEPOSIT_AEROSOL_NONE, DEPOSIT_AEROSOL_USER,
        DEPOSIT_AEROSOL_HENRY, DEPOSIT_AEROSOL_POWERS,
    )
    GENERATOR_OK = True
except Exception as _e:
    GENERATOR_OK = False
    # Guardar el error para mostrarlo en la UI
    _ENGINE_IMPORT_ERROR = str(_e)
    import traceback as _tb
    _ENGINE_IMPORT_TRACEBACK = _tb.format_exc()
    # Stubs para que las anotaciones de tipo no rompan la carga del módulo
    class PSFModel: pass
    class Compartment: pass
    class Pathway: pass
    class DoseLocation: pass
    class TimeValueTable: pass
    class TimeValue3Table: pass
    class FilterTable: pass
    COMP_TYPE_CONTROL_ROOM = COMP_TYPE_ENVIRONMENT = COMP_TYPE_OTHER = 0
    PATH_TYPE_PIPING = PATH_TYPE_FILTER = PATH_TYPE_SUPPRESSION_POOL = PATH_TYPE_AIR_LEAKAGE = 0
    DEPOSIT_AEROSOL_NONE = DEPOSIT_AEROSOL_USER = DEPOSIT_AEROSOL_HENRY = DEPOSIT_AEROSOL_POWERS = 0

# =============================================================================
# PALETA, RUTAS Y CONSTANTES
# =============================================================================

import sys
import subprocess
import threading
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import json

# ── Rutas ────────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent

DIR_INPUT   = SCRIPT_DIR / "INPUT"
DIR_MET     = DIR_INPUT / "MET"
DIR_NIF     = DIR_INPUT / "NIF"
DIR_RFT     = DIR_INPUT / "RFT"
DIR_INP     = DIR_INPUT / "INP"
DIR_PSF     = DIR_INPUT / "PSF"
DIR_INFO    = DIR_NIF
DIR_TEMPLATES = SCRIPT_DIR / "README_&_TEMPLATE"

# Apuntan al RUN más reciente — solo para autodetección en la GUI
DIR_ARCON   = SCRIPT_DIR / "RUN_1" / "WORK" / "ARCON"
DIR_RADTRAD = SCRIPT_DIR / "RUN_1" / "WORK" / "RADTRAD"
DIR_RESULTS = SCRIPT_DIR / "RUN_1" / "OUTPUT"

ARCON_EXE_DEFAULT   = Path(r"C:\ARCON96\arcon96f.exe")
RADTRAD_EXE_DEFAULT = Path(r"C:\RADTRAD\RADTRAD3.03x\Distribution0203\BatchModeVersion\radtrad.exe")

# ── Colores ───────────────────────────────────────────────────────────────────
BG_APP       = "#F3F4F6"
BG_CARD      = "#FFFFFF"
BG_INPUT     = "#E9EBEE"
BG_SECTION   = "#F8F9FA"
BLUE         = "#1A6FD4"
AMBER        = "#B45309"
GREEN        = "#1A7A3C"
TEXT         = "#1F2328"
MUTED        = "#57606A"
WHITE        = "#FFFFFF"
BORDER       = "#D0D7DE"
RED          = "#CF222E"
SUCCESS      = "#1A7A3C"
WARN         = "#9A6700"
BG_OK        = "#DAFBE1"
BG_WARN      = "#FFF8C5"
BG_SEL       = "#EBF5FF"
BORDER_SEL   = "#1A6FD4"
BG_ERR       = "#FFEBE9"

FONT_MONO    = ("Consolas", 10)
FONT_UI      = ("Segoe UI", 10)
FONT_SM      = ("Segoe UI", 9)
FONT_BOLD    = ("Segoe UI Semibold", 10)
FONT_TITLE   = ("Segoe UI Semibold", 12)
FONT_SECTION = ("Segoe UI Semibold", 11)


# PSF aliases
# Aliases paleta PSF → PIPELINE
BG     = BG_APP
CARD   = BG_CARD
INPUT  = BG_INPUT
PURPLE = "#6B3FA0"
FONT_LABEL = FONT_SM


# =============================================================================
# README — Contenido del manual de usuario
# =============================================================================

README_TEXT = """# RADTRAD Tool — Manual de usuario

**Autor:** Jon Ander Goiti Larrinaga — IDOM  
**Versión:** 1.0 · 2025  
**Archivos:** `RADTRAD_ENGINE.py` + `RADTRAD_GUI.py`

---

## ¿Qué es esto?

Herramienta integrada para el cálculo de consecuencias radiológicas de accidentes en centrales nucleares. Combina en una sola interfaz:

- **Pipeline ARCON96 + RADTRAD** — calcula factores de dispersión atmosférica (X/Q) y estima dosis en el límite de exclusión (EAB), zona de baja población (LPZ) y sala de control.
- **Generador PSF** — construye archivos de entrada `.psf` para RADTRAD 3.03 desde cero, sin necesidad de plantilla.

---

## Requisitos

### Python y librerías

```
Python >= 3.10
pip install numpy pandas openpyxl pillow tkinterdnd2
```

- `numpy`, `pandas`, `openpyxl` — necesarios para ejecutar el pipeline ARCON96 + RADTRAD.
- `pillow` — opcional, necesario solo para exportar el diagrama de planta como PNG.
- `tkinterdnd2` — opcional, activa el arrastre de archivos en la interfaz.

### Ejecutables externos

| Programa | Ruta por defecto |
|----------|-----------------|
| ARCON96  | `C:\\ARCON96\\arcon96f.exe` |
| RADTRAD 3.03 | `C:\\RADTRAD\\RADTRAD3.03x\\Distribution0203\\BatchModeVersion\\radtrad.exe` |

Las rutas se pueden cambiar en la interfaz antes de cada ejecución.

---

## Estructura de carpetas

```
mi_proyecto/
├── RADTRAD_ENGINE.py          ← motor de cálculo (no ejecutar directamente)
├── RADTRAD_GUI.py             ← interfaz gráfica (ejecutar esto)
├── LANZAR_RADTRAD.bat         ← acceso directo para Windows
├── README_&_TEMPLATE/        ← documentación y plantillas de referencia
│
├── INPUT/                     ← archivos de entrada (rellenar antes de ejecutar)
│   ├── MET/                   MET01.MET, MET02.MET ...
│   ├── NIF/                   *.NIF + isotopes_db.txt + NIF_Actividades.xlsx
│   ├── RFT/                   *.rft  (fracciones de liberación y tiempos)
│   ├── INP/                   *.inp  (factores de conversión de dosis)
│   └── PSF/                   template_master.psf
│
├── RUN_1/                     ← creada automáticamente al ejecutar
│   ├── INPUT_USED/            copia de los inputs usados + params.json
│   ├── WORK/                  runs internos de ARCON96 y RADTRAD (borrable)
│   └── OUTPUT/                resultados finales (Excel)
│
├── RUN_2/                     ← siguiente ejecución
│   └── ...
```

> **INPUT_USED** guarda una copia exacta de todos los archivos de entrada utilizados y un `params.json` con todos los parámetros de la ejecución. Esto garantiza la trazabilidad completa de cada resultado.

> **WORK** puede eliminarse para liberar espacio. Los resultados en **OUTPUT** no se ven afectados.

---

## Cómo ejecutar

### Opción 1 — Doble clic en el .bat (recomendado en Windows)
```
LANZAR_RADTRAD.bat
```
Si hay algún error, la consola permanece abierta mostrando el mensaje.

### Opción 2 — Línea de comandos
```bash
python RADTRAD_GUI.py
```

---

## Pestaña 1 — Pipeline ARCON96 + RADTRAD

### Sección X/Q — Cálculo de factores de dispersión

Activa o desactiva esta sección con el toggle ON/OFF. Cuando está activa:

**Datos meteorológicos (MET)**  
Tres modos de entrada:
- *Archivos .MET directos* — selecciona los archivos MET01.MET, MET02.MET... manualmente o arrástralos.
- *Excel automático* — selecciona un Excel MET*.xlsx y el pipeline genera los archivos .MET.

**Parámetros ARCON96**
- Distancia mínima, máxima y paso (en metros).
- Ruta al ejecutable `arcon96f.exe`.
- Opción para borrar los directorios de ejecución de ARCON96 al finalizar.
- Opción para conservar la carpeta WORK completa.

### Tipo de instalación

Arriba del todo se elige entre **Embarcación (reactor a bordo)** y **Planta terrestre**:

- *Embarcación*: latitud y longitud del centro del buque y rumbo de la proa. Las zonas se centran en el
  reactor, a popa, y el casco se dibuja a escala. Barrido propuesto: 10–400 m, paso 10 m.
- *Planta terrestre*: latitud y longitud del reactor. Sin casco ni rumbo. Barrido propuesto: 50–1.200 m,
  paso 50 m. El mapa muestra por defecto EAB, LPZ y zona de planificación.
- *Potencia (MWt)*: se escribe en todos los `.psf` (el inventario `.nif` va en Ci/MWt).

El transporte en RADTRAD y los criterios de dosis son los mismos en los dos casos; cambian la geometría,
el barrido de distancias propuesto y lo que se dibuja en el mapa.

### Sección RADTRAD — Cálculo de consecuencias

Activa o desactiva con el toggle ON/OFF. Cuando está activa:

**Generación de PSF**  
Dos modos:
- *Usar plantilla existente* — selecciona un `.psf` ya preparado.
- *Generar desde cero* — usa el `.psf` del Generador PSF (pestaña 2, botón «Usar en el cálculo»).

En los dos modos la cadena sustituye en cada caso el inventario, los ficheros `.inp` y `.rft`, la potencia,
las fracciones del yodo y el X/Q de las dose locations 1 y 2, que deben estar en el Environment y tener
tabla de X/Q de usuario. Si el `.psf` no lo cumple, la ejecución se detiene y lo dice.

**NIF — Archivo de inventario de nucléidos**  
Tres modos:
- *Existente* — usa un `.NIF` ya disponible en `INPUT/NIF/`.
- *Desde TXT* — genera el NIF a partir de un `Variables_NIF.txt`.
- *Desde Excel automático* — genera el NIF cruzando `NIF_Actividades.xlsx` con `isotopes_db.txt`.

**Archivos de soporte**
- `.rft` — fracciones de liberación y tiempos.
- `.inp` — factores de conversión de dosis (FGR 11 & 12).
- Ejecutable RADTRAD.

**Análisis de sensibilidad**  
Permite ejecutar RADTRAD con múltiples sets de fracciones de yodo (aerosol / elemental / orgánico) para estudiar la sensibilidad de los resultados. Dos modos:
- *Aleatorio* — genera N sets aleatorios que suman 1.
- *Manual* — define cada fracción manualmente.

### Ejecución

El botón **▶ EJECUTAR PIPELINE** lanza la ejecución. El modo varía según qué secciones estén activas:
- Solo ARCON96 activo → calcula solo X/Q.
- Solo RADTRAD activo → calcula solo consecuencias (usa X/Q existente).
- Ambos activos → pipeline completo.

La consola de log muestra la salida en tiempo real con colores por nivel (INFO, WARNING, ERROR, fase).

---

## Pestaña 2 — Generador PSF

Construye un archivo `.psf` de RADTRAD 3.03 desde cero sin necesidad de plantilla.

**Barra superior**
- *Preajuste*: «Embarcación — KP-FHR a bordo» y «Planta terrestre — KP-FHR» cargan el modelo validado con
  RADTRAD (el de `template_kpfhr.psf`: descarga directa al ambiente y sala de control); «Vacío» deja lo mínimo.
- *Guardar config / Cargar config*: guarda y recupera todo el contenido del generador en un `.json`.
- *Guardar PSF…*: escribe el `.psf` donde se indique.
- *Usar en el cálculo*: lo valida, lo guarda en `INPUT/PSF/generated.psf` y lo selecciona en la pestaña 1.

**Alcance.** Escribe compartimentos (con filtros de recirculación y deposición natural), caminos de tipo
Filter, Air Leakage y Suppression Pool, y dose locations. No escribe sprays, «overlying pool» ni las tablas
de Piping: si se activan, avisa en lugar de generar un fichero incoherente. El término fuente entra siempre
en el compartimento 1. Volúmenes en m³ y caudales en m³/s (el fichero va en ft³ y cfm).

### Sub-pestañas

**Global**  
Parámetros del modelo completo: nombre del caso, archivos NIF/INP/RFT, potencia de planta, fracciones de yodo (con suma en tiempo real), opciones de decay/daughters y salidas.

**Compartimentos**  
Añade hasta 10 compartimentos. Para cada uno:
- Nombre, tipo (1=Control Room / 2=Environment / 3=Other) y volumen en m³.
- Toggles ON/OFF para sprays, filtros de recirculación, deposición natural y overlying pool.
- Al activar filtros: caudal normalizado y tabla de eficiencias (aerosol / elemental / orgánico).
- Al activar deposición: selector de modelo (ninguno / usuario / Henry / Powers) con sus parámetros.

**Pathways**  
Añade hasta 25 pathways. Para cada uno:
- Nombre, compartimento origen, compartimento destino.
- Tipo de mecanismo: Piping / Filter / Suppression Pool / Air Leakage.
- Tabla de caudales o eficiencias según el mecanismo elegido.

**Dose Locations**  
Añade hasta 10 locations. Para cada una:
- Nombre y compartimento donde está ubicada.
- Modelo X/Q (constante 1.0 o tabla usuario con pares tiempo/X/Q).
- Tabla de breathing rate.
- Tabla de occupancy factors (solo para Control Room).

**Vista previa**  
Muestra en tiempo real:
- **Diagrama de planta** — esquema visual con compartimentos, pathways y dose locations coloreados por tipo.
- **Texto PSF** — contenido exacto del archivo que se generará.

Botones disponibles:
- `↺ Actualizar` — regenera diagrama y texto.
- `⬇ Guardar PSF` — guarda el archivo `.psf` directamente.
- `🖼 Exportar diagrama` — guarda el diagrama como PNG (requiere Pillow) o EPS vectorial.

---

## Archivos de referencia

### isotopes_db.txt
Base de datos de isótopos para la generación automática de NIF. Formato:
```
ISOTOPE  HALF_LIFE_S  ENERGY_MeV  ...
```

### NIF_Actividades.xlsx
Excel con las actividades por isótopo para el inventario del reactor. Se cruza con `isotopes_db.txt` para generar el `.NIF`.

### template_master.psf
Plantilla PSF de referencia. Solo se usa cuando el modo PSF es "plantilla existente". Si usas el Generador PSF no necesitas esta plantilla.

---

## Resultados

Cada ejecución genera una carpeta `RUN_N/OUTPUT/` con:

| Archivo | Contenido |
|---------|-----------|
| `99_5th_PERCENTILE_XQ_VALUES_Sector_BY_HOUR.xlsx` | X/Q al percentil 95 por hora y sector (Bridge Excel) |
| `TOTAL_XQs_BY_HOUR.xlsx` | X/Q totales por hora |
| `Sets_Worst2h.xlsx` | Peores 2 horas de dosis por set de fracciones de yodo |
| `zonas_emergencia.json`, `mapa_zonas.html`, `mapa_zonas.png` | Radios de las zonas de la Tabla 4 y mapa |
| `E2/`, `SENS_F1/` | Escenario E2 y caso de sensibilidad meteorológica |

---

## Pestaña «Mapa de zonas»

Al terminar una ejecución la pestaña se abre con sus resultados. El selector muestra todas las
ejecuciones (caso base y sensibilidad clase F, 1 m/s).

- **Zonas:** marca las que quieras ver y cambia el límite (mSv) para recalcular el radio.
- **Instalación:** embarcación o planta terrestre. Embarcación: latitud, longitud y rumbo (dirección de la
  proa) del centro del buque, eslora, manga y distancia del reactor a la popa; las zonas se centran en el
  reactor. Planta terrestre: latitud y longitud del reactor, sin casco.
- **Mapa:** buque, reactor y zonas a escala sobre OpenStreetMap, callejero o satélite de Esri (o sin
  mapa), con cuadrícula de latitud y longitud y las coordenadas del cursor (decimal y grados,
  minutos y segundos) y su distancia al reactor. Rueda: zoom; arrastrar: mover; clic derecho:
  situar ahí el centro del buque o el reactor de la planta; doble clic: ajustar. Las teselas se guardan en `cache_teselas/`.
- **Abrir mapa en el navegador:** guarda los cambios y abre el mapa sobre OpenStreetMap o satélite.
- **Guardar buque y criterios:** reescribe `zonas_emergencia.json`, `mapa_zonas.html` y `mapa_zonas.png`.

---

## Solución de problemas frecuentes

**La ventana no se abre al hacer doble clic**  
Usa `LANZAR_RADTRAD.bat` para ver el error en la consola.

**`ModuleNotFoundError: No module named 'numpy'`**  
```bash
pip install numpy pandas openpyxl
```

**`ModuleNotFoundError: No module named 'tkinter'`**  
En Linux/Mac: `sudo apt install python3-tk` o `brew install python-tk`.

**El pipeline se lanza pero ARCON96 no corre**  
Verifica que la ruta al ejecutable `arcon96f.exe` es correcta y que los archivos MET están en `INPUT/MET/`.

**El PSF generado da error al cargarlo en RADTRAD**  
Verifica en Vista previa que las fracciones de yodo suman exactamente 1.0 y que todos los pathways referencian compartimentos existentes.

---

## Contacto

Jon Ander Goiti Larrinaga — IDOM · 2025
"""


class ReadmeWindow(tk.Toplevel):
    """Ventana flotante con el README del programa."""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("RADTRAD Tool — Manual de usuario")
        self.geometry("820x680")
        self.minsize(600, 400)
        self.configure(bg=BG_APP)

        # Barra superior
        bar = tk.Frame(self, bg=BG_CARD, height=46)
        bar.pack(fill="x"); bar.pack_propagate(False)
        tk.Label(bar, text="Manual de usuario — RADTRAD Tool",
                 bg=BG_CARD, fg=TEXT,
                 font=("Segoe UI Semibold", 11)).pack(side="left", padx=14, pady=12)
        tk.Button(bar, text="✕  Cerrar", bg=BG_INPUT, fg=MUTED,
                  relief="flat", font=FONT_SM, bd=0, padx=10, pady=6,
                  cursor="hand2", activebackground=RED, activeforeground=WHITE,
                  command=self.destroy).pack(side="right", padx=8, pady=6)

        # Área de texto con scroll
        txt = scrolledtext.ScrolledText(
            self, bg=CARD, fg=TEXT, font=("Segoe UI", 10),
            relief="flat", bd=0, padx=20, pady=14,
            wrap="word", state="normal")
        txt.pack(fill="both", expand=True, padx=0, pady=0)

        # Insertar texto con formato básico
        self._render(txt, README_TEXT)
        txt.config(state="disabled")

        # Centrar sobre la ventana padre
        self.update_idletasks()
        px = parent.winfo_rootx() + parent.winfo_width()//2 - 410
        py = parent.winfo_rooty() + parent.winfo_height()//2 - 340
        self.geometry(f"+{max(0,px)}+{max(0,py)}")
        self.lift()
        self.focus_set()

    def _render(self, txt, content):
        """Inserta el README con estilos básicos de Markdown."""
        txt.tag_configure("h1",  font=("Segoe UI Semibold", 16), foreground=BLUE,
                           spacing1=12, spacing3=4)
        txt.tag_configure("h2",  font=("Segoe UI Semibold", 13), foreground=BLUE,
                           spacing1=10, spacing3=2)
        txt.tag_configure("h3",  font=("Segoe UI Semibold", 11), foreground=TEXT,
                           spacing1=8, spacing3=2)
        txt.tag_configure("bold", font=("Segoe UI Semibold", 10))
        txt.tag_configure("code", font=("Consolas", 9), background="#F0F2F5",
                           foreground="#C0392B")
        txt.tag_configure("block", font=("Consolas", 9), background="#F8F9FA",
                           foreground="#2C3E50", lmargin1=20, lmargin2=20,
                           spacing1=2, spacing3=2)
        txt.tag_configure("table_head", font=("Segoe UI Semibold", 9),
                           background="#EBF5FF", foreground=BLUE)
        txt.tag_configure("table_row", font=("Segoe UI", 9),
                           background=CARD)
        txt.tag_configure("sep",  foreground=BORDER)
        txt.tag_configure("body", font=("Segoe UI", 10))

        in_code_block = False
        for line in content.splitlines():
            raw = line.rstrip()

            if raw.startswith("```"):
                in_code_block = not in_code_block
                continue

            if in_code_block:
                txt.insert("end", raw + "\n", "block")
                continue

            if raw.startswith("# "):
                txt.insert("end", raw[2:] + "\n", "h1")
            elif raw.startswith("## "):
                txt.insert("end", raw[3:] + "\n", "h2")
            elif raw.startswith("### "):
                txt.insert("end", raw[4:] + "\n", "h3")
            elif raw.startswith("---"):
                txt.insert("end", "─" * 80 + "\n", "sep")
            elif raw.startswith("|"):
                tag = "table_head" if "---" in raw else "table_row"
                txt.insert("end", raw + "\n", tag)
            elif raw.startswith("> "):
                txt.insert("end", "  " + raw[2:] + "\n", "block")
            else:
                # Negrita inline: **texto**
                import re as _re
                parts = _re.split(r"(\*\*[^*]+\*\*)", raw)
                for part in parts:
                    if part.startswith("**") and part.endswith("**"):
                        txt.insert("end", part[2:-2], "bold")
                    else:
                        txt.insert("end", part, "body")
                txt.insert("end", "\n", "body")


# =============================================================================
# PIPELINE GUI
# =============================================================================

# =============================================================================
# HELPERS — Bridge Excel
# =============================================================================

def read_distances_from_bridge_excel(path: Path):
    try:
        from openpyxl import load_workbook
        wb = load_workbook(path, data_only=True, read_only=True)
        ws = wb[wb.sheetnames[0]]
        distances = []
        for row in ws.iter_rows(min_row=3, min_col=1, max_col=1, values_only=True):
            v = row[0]
            if v is None:
                break
            try:
                distances.append(int(v))
            except (TypeError, ValueError):
                break
        wb.close()
    except Exception as e:
        raise ValueError(f"No se pudo leer el Bridge Excel: {e}")
    if len(distances) < 2:
        raise ValueError("El Bridge Excel no contiene suficientes distancias.")
    distances = sorted(set(distances))
    diffs = [distances[i+1] - distances[i] for i in range(len(distances)-1)]
    delta = min(set(diffs), key=lambda x: -diffs.count(x))
    return distances[0], distances[-1], delta


# =============================================================================
# COMPONENTES BASE
# =============================================================================

class SE(tk.Entry):
    """Styled Entry."""
    def __init__(self, parent, **kw):
        kw.setdefault("bg", BG_INPUT); kw.setdefault("fg", TEXT)
        kw.setdefault("insertbackground", BLUE); kw.setdefault("relief", "flat")
        kw.setdefault("font", FONT_UI); kw.setdefault("bd", 0)
        super().__init__(parent, **kw)
        self.config(highlightthickness=1, highlightbackground=BORDER)
        self.bind("<FocusIn>",  lambda e: self.config(highlightbackground=BLUE))
        self.bind("<FocusOut>", lambda e: self.config(highlightbackground=BORDER))


class SS(tk.Spinbox):
    """Styled Spinbox."""
    def __init__(self, parent, **kw):
        kw.setdefault("bg", BG_INPUT); kw.setdefault("fg", TEXT)
        kw.setdefault("buttonbackground", BG_CARD)
        kw.setdefault("relief", "flat"); kw.setdefault("font", FONT_UI); kw.setdefault("bd", 0)
        super().__init__(parent, **kw)
        self.config(highlightthickness=1, highlightbackground=BORDER)


class FL(tk.Label):
    """Field Label."""
    def __init__(self, parent, text, width=20, **kw):
        kw.setdefault("bg", BG_CARD); kw.setdefault("fg", MUTED)
        kw.setdefault("font", FONT_SM); kw.setdefault("anchor", "w")
        super().__init__(parent, text=text, width=width, **kw)


def hline(parent, color=BORDER, pady=6, bg=None):
    tk.Frame(parent, bg=bg or color, height=1).pack(fill="x", pady=pady)


class FilePicker(tk.Frame):
    def __init__(self, parent, label, default="", filetypes=None,
                 lw=20, on_change=None, **kw):
        kw.setdefault("bg", BG_CARD)
        super().__init__(parent, **kw)
        self.filetypes = filetypes or [("All", "*.*")]
        self._on_change = on_change
        FL(self, label, width=lw).pack(side="left", padx=(0, 6))
        self.var = tk.StringVar(value=str(default))
        if on_change:
            self.var.trace_add("write", lambda *_: on_change(self.var.get()))
        SE(self, textvariable=self.var, width=42).pack(side="left", ipady=4, padx=(0, 4))
        tk.Button(self, text="…", bg=BG_INPUT, fg=MUTED,
                  activebackground=BLUE, activeforeground=WHITE,
                  relief="flat", font=FONT_SM, bd=0, padx=6, cursor="hand2",
                  command=self._browse).pack(side="left")

    def _browse(self):
        p = filedialog.askopenfilename(filetypes=self.filetypes)
        if p:
            self.var.set(p)

    def get(self):
        return self.var.get()


class IntField(tk.Frame):
    def __init__(self, parent, label, default, lo=1, hi=99999, w=8, lw=20, **kw):
        kw.setdefault("bg", BG_CARD)
        super().__init__(parent, **kw)
        FL(self, label, width=lw).pack(side="left", padx=(0, 6))
        self.var = tk.IntVar(value=default)
        SS(self, from_=lo, to=hi, textvariable=self.var, width=w).pack(side="left", ipady=4)

    def get(self):
        return self.var.get()

    def set(self, v):
        self.var.set(v)


# =============================================================================
# TOGGLE SWITCH  — Canvas animado estilo iOS
# =============================================================================

class Toggle(tk.Canvas):
    """
    Toggle switch con animación suave.
    Verde + círculo a la derecha = ON
    Gris  + círculo a la izquierda = OFF
    """
    W, H   = 64, 32          # dimensiones del widget
    R      = 14              # radio del círculo
    STEPS  = 8               # pasos de animación
    MS     = 12              # ms entre pasos

    ON_TRACK  = "#2ECC40"    # verde
    OFF_TRACK = "#AAAAAA"    # gris

    def __init__(self, parent, initial=True, callback=None, bg=None, **kw):
        bg = bg or BG_CARD
        super().__init__(parent, width=self.W, height=self.H,
                         bg=bg, highlightthickness=0, cursor="hand2", **kw)
        self._state    = initial
        self._callback = callback
        self._animating = False

        # Posición X del centro del círculo
        self._cx = self._cx_for(initial)

        self._draw_static()
        self.bind("<Button-1>", lambda e: self._on_click())

    def _cx_for(self, state):
        """Posición X central del thumb según estado."""
        return self.W - self.H // 2 - 2 if state else self.H // 2 + 2

    def _draw_static(self):
        self.delete("all")
        color = self.ON_TRACK if self._state else self.OFF_TRACK
        r = self.H // 2
        # Track redondeado (dos semicírculos + rectángulo)
        self.create_arc(0, 0, self.H, self.H,
                        start=90, extent=180, fill=color, outline=color)
        self.create_arc(self.W - self.H, 0, self.W, self.H,
                        start=270, extent=180, fill=color, outline=color)
        self.create_rectangle(r, 0, self.W - r, self.H,
                               fill=color, outline=color)
        # Texto ON / OFF
        tx = self.W * 0.3 if self._state else self.W * 0.67
        self.create_text(tx, self.H // 2,
                         text="ON" if self._state else "OFF",
                         fill=WHITE, font=("Segoe UI Semibold", 8))
        # Thumb (círculo blanco)
        cx = self._cx
        self.create_oval(cx - self.R, self.H // 2 - self.R,
                         cx + self.R, self.H // 2 + self.R,
                         fill=WHITE, outline=WHITE)

    def _on_click(self):
        if self._animating:
            return
        self._state = not self._state
        if self._callback:
            self._callback(self._state)
        self._animate()

    def _animate(self):
        target = self._cx_for(self._state)
        start  = self._cx
        dist   = target - start
        step   = dist / self.STEPS
        self._animating = True

        def _step(i):
            if i >= self.STEPS:
                self._cx = target
                self._draw_static()
                self._animating = False
                return
            self._cx = start + step * i
            self._draw_frame()
            self.after(self.MS, lambda: _step(i + 1))

        _step(1)

    def _draw_frame(self):
        """Redibuja solo el thumb en posición intermedia (durante animación)."""
        # Redibujar track con color final
        color = self.ON_TRACK if self._state else self.OFF_TRACK
        self.delete("all")
        r = self.H // 2
        self.create_arc(0, 0, self.H, self.H,
                        start=90, extent=180, fill=color, outline=color)
        self.create_arc(self.W - self.H, 0, self.W, self.H,
                        start=270, extent=180, fill=color, outline=color)
        self.create_rectangle(r, 0, self.W - r, self.H,
                               fill=color, outline=color)
        cx = int(self._cx)
        self.create_oval(cx - self.R, self.H // 2 - self.R,
                         cx + self.R, self.H // 2 + self.R,
                         fill=WHITE, outline=WHITE)

    def get(self):
        return self._state

    def set(self, v):
        self._state = bool(v)
        self._cx    = self._cx_for(self._state)
        self._draw_static()


# =============================================================================
# SECCIÓN COLAPSABLE CON TOGGLE
# =============================================================================

class Section(tk.Frame):
    """
    Sección con cabecera coloreada, toggle ON/OFF animado y cuerpo colapsable.
    """
    def __init__(self, parent, title, color,
                 initial=True, on_toggle=None, **kw):
        kw.setdefault("bg", BG_CARD)
        super().__init__(parent, **kw)
        self.config(highlightthickness=1, highlightbackground=BORDER)
        self._on_toggle = on_toggle

        # ── Cabecera ──────────────────────────────────────────────────────────
        hdr = tk.Frame(self, bg=color)
        hdr.pack(fill="x")

        tk.Label(hdr, text=title, bg=color, fg=WHITE,
                 font=FONT_SECTION, anchor="w",
                 padx=14, pady=10).pack(side="left")

        self.toggle = Toggle(hdr, initial=initial,
                             callback=self._handle_toggle,
                             bg=color)
        self.toggle.pack(side="right", padx=14, pady=10)

        # ── Cuerpo ────────────────────────────────────────────────────────────
        self.body = tk.Frame(self, bg=BG_CARD)
        if initial:
            self.body.pack(fill="x")

    def _handle_toggle(self, state):
        if state:
            self.body.pack(fill="x")
        else:
            self.body.pack_forget()
        if self._on_toggle:
            self._on_toggle(state)

    def is_active(self):
        return self.toggle.get()

    def set_active(self, v):
        self.toggle.set(v)
        self._handle_toggle(v)


# =============================================================================
# SUB-SECCIÓN (dentro de Section)
# =============================================================================

class SubSection(tk.Frame):
    """Subsección con línea lateral de color y título."""
    def __init__(self, parent, title, color=BLUE, **kw):
        kw.setdefault("bg", BG_CARD)
        super().__init__(parent, **kw)
        # Línea lateral
        tk.Frame(self, bg=color, width=3).pack(side="left", fill="y")
        content = tk.Frame(self, bg=BG_CARD)
        content.pack(side="left", fill="both", expand=True, padx=(10, 0))
        tk.Label(content, text=title, bg=BG_CARD, fg=color,
                 font=FONT_BOLD, anchor="w").pack(fill="x", pady=(8, 6))
        self.content = content


# =============================================================================
# PANEL MET
# =============================================================================

class MetFileRow(tk.Frame):
    def __init__(self, parent, name, ok=True):
        super().__init__(parent, bg=BG_CARD)
        bg_p = BG_OK   if ok else BG_WARN
        fg_p = SUCCESS if ok else WARN
        sym  = "✓"     if ok else "!"
        tk.Label(self, text=f" {sym} ", bg=bg_p, fg=fg_p,
                 font=("Segoe UI Semibold", 8)).pack(side="left", padx=(0, 6))
        tk.Label(self, text=name, bg=BG_CARD,
                 fg=TEXT if ok else WARN, font=FONT_SM).pack(side="left")


class MetWidget(tk.Frame):
    """Widget completo de datos MET para incrustar en el body de Section."""
    def __init__(self, parent):
        super().__init__(parent, bg=BG_CARD)
        sub = SubSection(self, "Datos meteorológicos", color=BLUE)
        sub.pack(fill="x", padx=12, pady=(6, 2))
        body = sub.content

        # Selector de modo
        mode_row = tk.Frame(body, bg=BG_CARD)
        mode_row.pack(fill="x", pady=(0, 8))
        self._mode = tk.StringVar(value="files")
        self._btn_files = self._mode_btn(mode_row, "Archivos .MET",
                                          "MET01.MET, MET02.MET…", "files")
        self._btn_excel = self._mode_btn(mode_row, "Excel de referencia",
                                          "MET*.xlsx — una pestaña por año", "excel")
        self._btn_files.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self._btn_excel.pack(side="left", fill="x", expand=True)

        # Panel archivos
        self._pf = tk.Frame(body, bg=BG_CARD)
        num_r = tk.Frame(self._pf, bg=BG_CARD)
        num_r.pack(fill="x", pady=(0, 6))
        FL(num_r, "Número de archivos MET:", width=24).pack(side="left", padx=(0, 6))
        self.num_met_var = tk.IntVar(value=max(1, len(list(DIR_MET.glob("MET*.MET"))) if DIR_MET.exists() else 1))
        sb = SS(num_r, from_=1, to=99, textvariable=self.num_met_var,
                width=6, command=self._refresh_list)
        sb.pack(side="left", ipady=4)
        sb.bind("<FocusOut>", lambda e: self._refresh_list())

        dz = tk.Frame(self._pf, bg=BG_INPUT,
                      highlightthickness=1, highlightbackground=BORDER)
        dz.pack(fill="x", pady=(0, 6))
        self._drop_lbl = tk.Label(dz, text="Arrastra aquí los archivos .MET  o",
                                  bg=BG_INPUT, fg=MUTED, font=FONT_SM)
        self._drop_lbl.pack(pady=(8, 4))
        br = tk.Frame(dz, bg=BG_INPUT)
        br.pack(pady=(0, 8))
        for lbl, cmd in (("Buscar archivos…",        self._browse_met),
                         ("Buscar en carpeta 01MET", self._scan_folder)):
            tk.Button(br, text=lbl, bg=BG_CARD, fg=TEXT,
                      activebackground=BLUE, activeforeground=WHITE,
                      relief="flat", font=FONT_SM, bd=0, padx=8, pady=3,
                      highlightthickness=1, highlightbackground=BORDER,
                      cursor="hand2", command=cmd).pack(side="left", padx=3)
        self._drop_zone = dz
        self._list_frame = tk.Frame(self._pf, bg=BG_CARD)
        self._list_frame.pack(fill="x")
        self._met_paths: list[Path] = []
        self._try_dnd()

        # Panel Excel
        self._pe = tk.Frame(body, bg=BG_CARD)
        edz = tk.Frame(self._pe, bg=BG_INPUT,
                       highlightthickness=1, highlightbackground=BORDER)
        edz.pack(fill="x", pady=(0, 6))
        self._excel_lbl = tk.Label(edz, text="Arrastra aquí el archivo MET*.xlsx  o",
                                   bg=BG_INPUT, fg=MUTED, font=FONT_SM)
        self._excel_lbl.pack(pady=(8, 4))
        tk.Button(edz, text="Buscar archivo…", bg=BG_CARD, fg=TEXT,
                  activebackground=BLUE, activeforeground=WHITE,
                  relief="flat", font=FONT_SM, bd=0, padx=8, pady=3,
                  highlightthickness=1, highlightbackground=BORDER,
                  cursor="hand2", command=self._browse_excel).pack(pady=(0, 8))
        self._excel_drop = edz
        self.excel_var = tk.StringVar(value="")
        SE(self._pe, textvariable=self.excel_var, width=58
           ).pack(fill="x", ipady=4, pady=(0, 6))
        self._sheets_f = tk.Frame(self._pe, bg=BG_CARD)
        self._sheets_f.pack(fill="x")

        self._set_mode("files")

    def _mode_btn(self, parent, title, sub, mode):
        f = tk.Frame(parent, bg=BG_INPUT, cursor="hand2",
                     highlightthickness=1, highlightbackground=BORDER)
        tk.Label(f, text=title, bg=BG_INPUT, fg=TEXT,
                 font=("Segoe UI Semibold", 9), anchor="w"
                 ).pack(fill="x", padx=8, pady=(5, 0))
        tk.Label(f, text=sub, bg=BG_INPUT, fg=MUTED,
                 font=FONT_SM, anchor="w").pack(fill="x", padx=8, pady=(0, 5))
        f.bind("<Button-1>", lambda e: self._set_mode(mode))
        for c in f.winfo_children():
            c.bind("<Button-1>", lambda e: self._set_mode(mode))
        return f

    def _set_mode(self, mode):
        self._mode.set(mode)
        for btn, m in ((self._btn_files, "files"), (self._btn_excel, "excel")):
            active = (m == mode)
            bg = BG_SEL if active else BG_INPUT
            btn.config(bg=bg, highlightbackground=BORDER_SEL if active else BORDER)
            ch = btn.winfo_children()
            if ch:
                ch[0].config(bg=bg, fg=BLUE if active else TEXT)
                if len(ch) > 1:
                    ch[1].config(bg=bg)
        if mode == "files":
            self._pe.pack_forget(); self._pf.pack(fill="x")
        else:
            self._pf.pack_forget(); self._pe.pack(fill="x")

    def _try_dnd(self):
        try:
            import tkinterdnd2  # noqa
            self._drop_zone.drop_target_register("DND_Files")
            self._drop_zone.dnd_bind("<<Drop>>",
                lambda e: self._add_met([p for p in self._parse_drop(e.data)
                                         if p.suffix.upper() == ".MET"]))
            self._excel_drop.drop_target_register("DND_Files")
            self._excel_drop.dnd_bind("<<Drop>>",
                lambda e: self._set_excel(
                    next((p for p in self._parse_drop(e.data)
                          if p.suffix.lower() in (".xlsx", ".xls")), None)))
            self._drop_lbl.config(text="↓  Arrastra aquí los archivos .MET  o")
            self._excel_lbl.config(text="↓  Arrastra aquí el archivo MET*.xlsx  o")
        except (ImportError, Exception):
            pass

    @staticmethod
    def _parse_drop(data):
        import re
        return [Path(a or b) for a, b in re.findall(r'\{([^}]+)\}|(\S+)', data) if a or b]

    def _browse_met(self):
        ps = filedialog.askopenfilenames(
            filetypes=[("MET files", "*.MET *.met"), ("All", "*.*")],
            initialdir=str(DIR_MET) if DIR_MET.exists() else str(SCRIPT_DIR))
        if ps:
            self._add_met([Path(p) for p in ps])

    def _scan_folder(self):
        if not DIR_MET.exists():
            messagebox.showwarning("No encontrada", f"No existe:\n{DIR_MET}"); return
        found = sorted(DIR_MET.glob("[Mm][Ee][Tt]*.MET")) + \
                sorted(DIR_MET.glob("[Mm][Ee][Tt]*.met"))
        if not found:
            messagebox.showinfo("Sin archivos", "No se encontraron .MET en 01MET/"); return
        self._add_met(found)

    def _add_met(self, paths):
        for p in paths:
            if p not in self._met_paths:
                self._met_paths.append(p)
        self.num_met_var.set(len(self._met_paths))
        self._refresh_list()

    def _refresh_list(self):
        for w in self._list_frame.winfo_children():
            w.destroy()
        n = self.num_met_var.get()
        expected = {f"MET{i:02d}.MET" for i in range(1, n+1)}
        loaded   = {p.name.upper() for p in self._met_paths}
        for p in self._met_paths[:n]:
            MetFileRow(self._list_frame, p.name, ok=True).pack(fill="x", pady=1)
        for name in sorted(expected - loaded):
            MetFileRow(self._list_frame, f"{name} — pendiente", ok=False).pack(fill="x", pady=1)

    def _browse_excel(self):
        p = filedialog.askopenfilename(
            filetypes=[("Excel", "*.xlsx *.xls"), ("All", "*.*")],
            initialdir=str(DIR_INFO) if DIR_INFO.exists() else str(SCRIPT_DIR))
        if p:
            self._set_excel(Path(p))

    def _set_excel(self, path):
        if path is None: return
        self.excel_var.set(str(path))
        self._detect_sheets(path)

    def _detect_sheets(self, path):
        for w in self._sheets_f.winfo_children():
            w.destroy()
        try:
            import pandas as pd
            xl = pd.ExcelFile(path, engine="openpyxl")
            sheets = xl.sheet_names
        except Exception as e:
            tk.Label(self._sheets_f, text=f"Error: {e}",
                     bg=BG_CARD, fg=RED, font=FONT_SM).pack(anchor="w"); return
        tk.Label(self._sheets_f, text="Pestañas detectadas:",
                 bg=BG_CARD, fg=MUTED, font=FONT_SM).pack(anchor="w", pady=(4, 3))
        pills = tk.Frame(self._sheets_f, bg=BG_CARD)
        pills.pack(fill="x")
        valid = 0
        for s in sheets:
            try:
                df = xl.parse(s, header=2, nrows=5)
                ok = {"Dir_10m","Vel_10m"}.issubset(set(str(c).strip() for c in df.columns))
            except Exception:
                ok = False
            valid += ok
            tk.Label(pills, text=f"  {s}  ",
                     bg=BG_SEL if ok else BG_INPUT,
                     fg=BLUE   if ok else MUTED,
                     font=FONT_SM).pack(side="left", padx=3, pady=2)
        tk.Label(self._sheets_f,
                 text=f"Se generarán {valid} archivos MET automáticamente.",
                 bg=BG_CARD, fg=MUTED, font=FONT_SM).pack(anchor="w", pady=(4, 0))

    def get(self):
        mode = self._mode.get()
        if mode == "files":
            n = self.num_met_var.get()
            return {"met_mode": "files", "num_met": n,
                    "met_paths": self._met_paths[:n], "excel_path": ""}
        return {"met_mode": "excel", "num_met": 0,
                "met_paths": [], "excel_path": self.excel_var.get()}


# =============================================================================
# WIDGET ARCON96
# =============================================================================

class ArconWidget(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG_CARD)
        sub = SubSection(self, "ARCON96 — Parámetros de dispersión", color=BLUE)
        sub.pack(fill="x", padx=12, pady=(2, 8))
        body = sub.content

        self.dist_min = IntField(body, "Distancia mín [m]:", 10,  1, 99999, lw=24)
        self.dist_max = IntField(body, "Distancia máx [m]:", 400, 2, 99999, lw=24)
        self.delta    = IntField(body, "Paso [m]:",          10,  1, 9999,  lw=24)
        for f in (self.dist_min, self.dist_max, self.delta):
            f.pack(fill="x", pady=3)

        exe_row = tk.Frame(body, bg=BG_CARD)
        exe_row.pack(fill="x", pady=3)
        FL(exe_row, "arcon96f.exe:", width=24).pack(side="left", padx=(0, 6))
        self.arcon_exe = tk.StringVar(value=str(ARCON_EXE_DEFAULT))
        SE(exe_row, textvariable=self.arcon_exe, width=40
           ).pack(side="left", ipady=4, padx=(0, 4))
        tk.Button(exe_row, text="…", bg=BG_INPUT, fg=MUTED,
                  activebackground=BLUE, activeforeground=WHITE,
                  relief="flat", font=FONT_SM, bd=0, padx=6, cursor="hand2",
                  command=self._browse).pack(side="left")

        hline(body, pady=8)

        del_card = tk.Frame(body, bg=BG_WARN,
                            highlightthickness=1, highlightbackground="#D4A017")
        del_card.pack(fill="x", pady=(0, 4))
        self.delete_dirs = tk.BooleanVar(value=False)
        tk.Checkbutton(del_card,
                       text="Borrar directorios de ejecución ARCON96 al finalizar",
                       variable=self.delete_dirs, bg=BG_WARN, fg=TEXT,
                       selectcolor=BG_CARD, activebackground=BG_WARN,
                       font=FONT_SM).pack(anchor="w", padx=8, pady=(6, 2))
        tk.Label(del_card,
                 text="Los resultados (Bridge Excel, TXT) se conservan. "
                      "Se eliminan subdirectorios de cálculo (*.log, *.cfd, *.out).",
                 bg=BG_WARN, fg=WARN, font=("Segoe UI", 8),
                 wraplength=480, justify="left").pack(anchor="w", padx=8, pady=(0, 6))

        # Keep WORK folder
        work_card = tk.Frame(body, bg=BG_CARD,
                             highlightthickness=1, highlightbackground=BORDER)
        work_card.pack(fill="x", pady=(4, 4))
        self.keep_work = tk.BooleanVar(value=True)
        tk.Checkbutton(work_card,
                       text="Conservar carpeta WORK de la ejecución",
                       variable=self.keep_work, bg=BG_CARD, fg=TEXT,
                       selectcolor=BG_CARD, activebackground=BG_CARD,
                       font=FONT_SM).pack(anchor="w", padx=8, pady=(6, 2))
        tk.Label(work_card,
                 text="Si está marcado: RUN_N/WORK/ se conserva con los runs completos "
                      "de ARCON96 y RADTRAD.  Si no: WORK/ no se crea (ahorra espacio).",
                 bg=BG_CARD, fg=MUTED, font=("Segoe UI", 8),
                 wraplength=480, justify="left").pack(anchor="w", padx=8, pady=(0, 6))

        # Meteorological sensitivity (memoria, chapter 10): class F, 1 m/s every hour
        sens_card = tk.Frame(body, bg=BG_CARD,
                             highlightthickness=1, highlightbackground=BORDER)
        sens_card.pack(fill="x", pady=(4, 4))
        self.sens_met = tk.BooleanVar(value=False)
        tk.Checkbutton(sens_card,
                       text="Sensibilidad meteorológica (clase F, 1 m/s)",
                       variable=self.sens_met, bg=BG_CARD, fg=TEXT,
                       selectcolor=BG_CARD, activebackground=BG_CARD,
                       font=FONT_SM).pack(anchor="w", padx=8, pady=(6, 2))
        tk.Label(sens_card,
                 text="Tras el caso base, repite ARCON96, RADTRAD y las zonas con meteorología "
                      "constante, clase F y 1 m/s (accidente de referencia de ARPANSA). "
                      "Resultados en RUN_N/OUTPUT/SENS_F1.",
                 bg=BG_CARD, fg=MUTED, font=("Segoe UI", 8),
                 wraplength=480, justify="left").pack(anchor="w", padx=8, pady=(0, 6))

    def _browse(self):
        p = filedialog.askopenfilename(filetypes=[("Exe", "*.exe"), ("All", "*.*")])
        if p:
            self.arcon_exe.set(p)

    def set_distances(self, dmin, dmax, delta):
        self.dist_min.set(dmin); self.dist_max.set(dmax); self.delta.set(delta)

    def get(self):
        return dict(dist_min=self.dist_min.get(), dist_max=self.dist_max.get(),
                    delta=self.delta.get(), arcon_exe=self.arcon_exe.get(),
                    delete_arcon_dirs=self.delete_dirs.get(),
                    keep_work=self.keep_work.get(),
                    sensibilidad_met=self.sens_met.get())


# =============================================================================
# WIDGET TIPO DE INSTALACIÓN
# =============================================================================
class InstalacionWidget(tk.Frame):
    """Ship or land plant. It sets what changes between both: the position that is asked for (centre of
    the ship and heading, or the reactor of the plant), the distance sweep proposed for ARCON96, the
    zones shown on the map and the thermal power written in every .psf."""
    DEFAULTS = {"buque": (10, 400, 10), "terrestre": (50, 1200, 50)}

    def __init__(self, parent, on_change=None):
        super().__init__(parent, bg=BG_CARD, highlightthickness=1, highlightbackground=BORDER)
        self._on_change = on_change
        try:
            import zonas_emergencia as ZE
            lat, lon, rumbo = ZE.DEFAULT_LAT, ZE.DEFAULT_LON, ZE.DEFAULT_HEADING
        except Exception:
            lat, lon, rumbo = 43.3605, -3.0820, 300.0
        self._ship_default = (lat, lon, rumbo)
        tk.Label(self, text="Tipo de instalación", bg=BG_CARD, fg=TEXT, font=FONT_BOLD,
                 anchor="w").pack(fill="x", padx=12, pady=(8, 2))
        row = tk.Frame(self, bg=BG_CARD); row.pack(fill="x", padx=12)
        self.tipo = tk.StringVar(value="buque")
        for val, label in (("buque", "Embarcación (reactor a bordo)"), ("terrestre", "Planta terrestre")):
            tk.Radiobutton(row, text=label, variable=self.tipo, value=val, bg=BG_CARD, fg=TEXT, font=FONT_UI,
                           activebackground=BG_CARD, selectcolor=BG_CARD,
                           command=self._changed).pack(side="left", padx=(0, 16))
        grid = tk.Frame(self, bg=BG_CARD); grid.pack(fill="x", padx=12, pady=(6, 2))
        self.v = {"lat": tk.StringVar(value=f"{lat:.5f}"), "lon": tk.StringVar(value=f"{lon:.5f}"),
                  "rumbo": tk.StringVar(value=f"{rumbo:g}"), "potencia": tk.StringVar(value="320")}
        self._lbl, self._ent = {}, {}
        for i, (k, txt) in enumerate((("lat", "Latitud"), ("lon", "Longitud"), ("rumbo", "Rumbo (°)"),
                                      ("potencia", "Potencia (MWt)"))):
            self._lbl[k] = tk.Label(grid, text=txt, bg=BG_CARD, fg=MUTED, font=FONT_SM, anchor="w")
            self._lbl[k].grid(row=0, column=i, sticky="w", padx=(0, 8))
            self._ent[k] = SE(grid, textvariable=self.v[k], width=12)
            self._ent[k].grid(row=1, column=i, sticky="we", padx=(0, 8), ipady=4)
            grid.columnconfigure(i, weight=1)
        self._hint = tk.Label(self, text="", bg=BG_CARD, fg=MUTED, font=("Segoe UI", 8), wraplength=560,
                              justify="left", anchor="w")
        self._hint.pack(fill="x", padx=12, pady=(4, 8))
        self._refresh()

    def _refresh(self):
        buque = self.tipo.get() == "buque"
        self._lbl["lat"].config(text="Latitud (centro del buque)" if buque else "Latitud (reactor)")
        self._lbl["lon"].config(text="Longitud (centro del buque)" if buque else "Longitud (reactor)")
        self._ent["rumbo"].config(state="normal" if buque else "disabled")
        self._hint.config(text=(
            "Buque: las zonas se centran en el reactor, a popa, y el casco se dibuja a escala con su rumbo. "
            "Por defecto, atraque de metaneros de BBG (Zierbena). En el mapa: EAB, LPZ, evacuación, confinamiento "
            "y planificación." if buque else
            "Planta terrestre: las zonas se centran en el punto indicado (el reactor), sin casco ni rumbo. No hay "
            "emplazamiento por defecto: escribe sus coordenadas o sitúalo después en la pestaña del mapa. En el mapa: "
            "EAB, LPZ y planificación (las demás se pueden activar). Barrido propuesto: 50–1.200 m, el intervalo "
            "en el que se validó ARCON96."))

    def _changed(self):
        self._refresh()
        if self._on_change:
            self._on_change(self.tipo.get())

    def get(self):
        def num(k, d):
            try: return float(self.v[k].get().replace(",", "."))
            except ValueError: return d
        lat, lon, rumbo = (num("lat", self._ship_default[0]), num("lon", self._ship_default[1]),
                           num("rumbo", self._ship_default[2]) % 360)
        pot = num("potencia", 320.0)
        if pot <= 0:
            raise ValueError("La potencia térmica debe ser mayor que 0 MWt")
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise ValueError("Latitud o longitud fuera de rango")
        return {"instalacion": self.tipo.get(), "plant_power": pot,
                "ship": [lat, lon, rumbo if self.tipo.get() == "buque" else 0.0]}

    def set(self, d: dict):
        self.tipo.set("terrestre" if str(d.get("instalacion", "buque")).startswith("terr") else "buque")
        if d.get("ship") and len(d["ship"]) >= 3:
            self.v["lat"].set(f"{float(d['ship'][0]):.5f}"); self.v["lon"].set(f"{float(d['ship'][1]):.5f}")
            self.v["rumbo"].set(f"{float(d['ship'][2]):g}")
        if d.get("plant_power"):
            self.v["potencia"].set(f"{float(d['plant_power']):g}")
        self._refresh()


# =============================================================================
# WIDGET NIF
# =============================================================================

class NifWidget(tk.Frame):
    """Selector de archivo NIF con tres modos."""
    def __init__(self, parent):
        super().__init__(parent, bg=BG_CARD)
        sub = SubSection(self, "Generación de NIF", color=AMBER)
        sub.pack(fill="x", padx=12, pady=(2, 2))
        body = sub.content

        self._mode = tk.StringVar(value="existing")
        modes = [
            ("existing", "Usar .nif existente",       "Selecciona un archivo .nif ya generado"),
            ("txt",      "Generar desde TXT",          "Variables_NIF.txt → .nif"),
            ("excel",    "Generar desde Excel",        "NIF_Actividades.xlsx + isotopes_db.txt"),
        ]
        mode_row = tk.Frame(body, bg=BG_CARD)
        mode_row.pack(fill="x", pady=(0, 8))
        self._mode_btns = {}
        for i, (val, title, sub_lbl) in enumerate(modes):
            f = tk.Frame(mode_row, bg=BG_INPUT, cursor="hand2",
                         highlightthickness=1, highlightbackground=BORDER)
            tk.Label(f, text=title, bg=BG_INPUT, fg=TEXT,
                     font=("Segoe UI Semibold", 9), anchor="w"
                     ).pack(fill="x", padx=6, pady=(4, 0))
            tk.Label(f, text=sub_lbl, bg=BG_INPUT, fg=MUTED,
                     font=("Segoe UI", 8), anchor="w").pack(fill="x", padx=6, pady=(0, 4))
            f.bind("<Button-1>", lambda e, v=val: self._set_nif_mode(v))
            for c in f.winfo_children():
                c.bind("<Button-1>", lambda e, v=val: self._set_nif_mode(v))
            f.pack(side="left", fill="x", expand=True, padx=(0 if i == 0 else 4, 0))
            self._mode_btns[val] = f

        # Panel modo 1: archivo existente
        self._p_existing = tk.Frame(body, bg=BG_CARD)
        nif_def = self._first(DIR_NIF, "*.NIF") or self._first(DIR_NIF, "*.nif") or ""
        self._nif_picker = FilePicker(self._p_existing, ".nif:", nif_def,
                                      filetypes=[("NIF", "*.nif *.NIF"), ("All", "*.*")],
                                      lw=8)
        self._nif_picker.pack(fill="x", pady=3)

        # Panel modo 2: desde TXT
        self._p_txt = tk.Frame(body, bg=BG_CARD)
        self._txt_picker = FilePicker(self._p_txt, "Variables TXT:", "",
                                       filetypes=[("TXT", "*.txt"), ("All", "*.*")],
                                       lw=14)
        self._txt_picker.pack(fill="x", pady=3)

        # Panel modo 3: desde Excel (automático desde 00INFO/)
        self._p_excel = tk.Frame(body, bg=BG_CARD)
        tk.Label(self._p_excel,
                 text="Se usará 00INFO/NIF_Actividades.xlsx + 00INFO/isotopes_db.txt "
                      "automáticamente.",
                 bg=BG_CARD, fg=MUTED, font=FONT_SM,
                 wraplength=460, justify="left").pack(anchor="w", pady=4)

        self._set_nif_mode("existing")

    @staticmethod
    def _first(folder, pattern):
        if folder.exists():
            c = sorted(folder.glob(pattern))
            if c: return str(c[0])
        return ""

    def _set_nif_mode(self, mode):
        self._mode.set(mode)
        for val, btn in self._mode_btns.items():
            active = (val == mode)
            bg = BG_SEL if active else BG_INPUT
            btn.config(bg=bg, highlightbackground=BORDER_SEL if active else BORDER)
            ch = btn.winfo_children()
            if ch:
                ch[0].config(bg=bg, fg=AMBER if active else TEXT)
                if len(ch) > 1: ch[1].config(bg=bg)
        for p in (self._p_existing, self._p_txt, self._p_excel):
            p.pack_forget()
        {"existing": self._p_existing,
         "txt":      self._p_txt,
         "excel":    self._p_excel}[mode].pack(fill="x")

    def get(self):
        mode = self._mode.get()
        return {"nif_mode": mode,
                "nif_path": self._nif_picker.get() if mode == "existing" else "",
                "nif_txt":  self._txt_picker.get() if mode == "txt"      else ""}


# =============================================================================
# WIDGET PSF
# =============================================================================

class PsfWidget(tk.Frame):
    """
    Widget PSF con dos modos:
      - Plantilla existente: seleccionar un .psf ya hecho
      - Desde cero: abrir el Generador PSF para construirlo
    """
    def __init__(self, parent):
        super().__init__(parent, bg=BG_CARD)
        sub = SubSection(self, "Generación de PSF", color=AMBER)
        sub.pack(fill="x", padx=12, pady=(2, 2))
        body = sub.content

        # ── Selector de modo ──────────────────────────────────────────────────
        mode_row = tk.Frame(body, bg=BG_CARD)
        mode_row.pack(fill="x", pady=(0, 6))
        tk.Label(mode_row, text="Modo PSF:", bg=BG_CARD, fg=MUTED,
                 font=FONT_SM, width=14, anchor="w").pack(side="left", padx=(0, 6))
        self._mode = tk.StringVar(value="template")
        for val, label in (("template", "Usar plantilla existente"),
                           ("scratch",  "Generar desde cero")):
            tk.Radiobutton(mode_row, text=label, variable=self._mode,
                           value=val, bg=BG_CARD, fg=TEXT, font=FONT_SM,
                           activebackground=BG_CARD, selectcolor=BG_CARD,
                           command=self._refresh_mode).pack(side="left", padx=(0, 12))

        # ── Panel: plantilla existente ────────────────────────────────────────
        self._tpl_frame = tk.Frame(body, bg=BG_CARD)
        tpl = str(DIR_PSF / "template_kpfhr.psf")
        self._psf = FilePicker(self._tpl_frame, "Plantilla PSF:", tpl,
                               filetypes=[("PSF", "*.psf"), ("All", "*.*")], lw=14)
        self._psf.pack(fill="x", pady=3)

        # ── Panel: desde cero ─────────────────────────────────────────────────
        self._scratch_frame = tk.Frame(body, bg=BG_OK,
                                        highlightthickness=1,
                                        highlightbackground="#1A7A3C")
        sc = tk.Frame(self._scratch_frame, bg=BG_OK)
        sc.pack(fill="x", padx=8, pady=8)
        tk.Label(sc, text="Construye el modelo en la pestaña «Generador PSF» y pulsa «Usar en el cálculo».",
                 bg=BG_OK, fg=SUCCESS, font=("Segoe UI", 9),
                 anchor="w").pack(fill="x", pady=(0, 4))
        self._scratch_out_var = tk.StringVar(
            value=str(DIR_PSF / "generated.psf"))
        out_row = tk.Frame(sc, bg=BG_OK)
        out_row.pack(fill="x", pady=(0, 6))
        tk.Label(out_row, text="Guardar PSF en:", bg=BG_OK, fg=MUTED,
                 font=FONT_SM, width=14, anchor="w").pack(side="left", padx=(0, 6))
        tk.Entry(out_row, textvariable=self._scratch_out_var,
                 bg=BG_CARD, fg=TEXT, relief="flat", font=FONT_UI,
                 highlightthickness=1, highlightbackground=BORDER, bd=0
                 ).pack(side="left", fill="x", expand=True, ipady=4, padx=(0, 4))
        tk.Button(out_row, text="…", bg=BG_INPUT, fg=MUTED,
                  activebackground=AMBER, activeforeground=WHITE,
                  relief="flat", font=FONT_SM, bd=0, padx=6, cursor="hand2",
                  command=self._browse_scratch_out).pack(side="left")
        self._open_gen_btn = tk.Button(
            sc, text="Abrir Generador PSF  →",
            bg=SUCCESS, fg=WHITE,
            activebackground="#145C2E", activeforeground=WHITE,
            relief="flat", font=FONT_BOLD, bd=0, padx=14, pady=6,
            cursor="hand2", command=self._open_generator)
        self._open_gen_btn.pack(anchor="w", pady=(2, 0))

        # ── Bridge Excel ──────────────────────────────────────────────────────
        self._bridge_frame = tk.Frame(body, bg=BG_WARN,
                                       highlightthickness=1,
                                       highlightbackground="#D4A017")
        bi = tk.Frame(self._bridge_frame, bg=BG_WARN)
        bi.pack(fill="x", padx=8, pady=8)
        tk.Label(bi, text="Bridge Excel de ARCON96 (input X/Q):",
                 bg=BG_WARN, fg=TEXT, font=("Segoe UI Semibold", 9),
                 anchor="w").pack(fill="x", pady=(0, 3))
        tk.Label(bi, text="Distancias y paso se leerán automáticamente del archivo.",
                 bg=BG_WARN, fg=WARN, font=("Segoe UI", 8),
                 anchor="w").pack(fill="x", pady=(0, 6))
        pr = tk.Frame(bi, bg=BG_WARN)
        pr.pack(fill="x")
        self.bridge_var = tk.StringVar(value=self._autodetect_bridge())
        tk.Entry(pr, textvariable=self.bridge_var, bg=BG_CARD, fg=TEXT,
                 relief="flat", font=FONT_UI,
                 highlightthickness=1, highlightbackground=BORDER, bd=0
                 ).pack(side="left", fill="x", expand=True, ipady=4, padx=(0, 4))
        tk.Button(pr, text="…", bg=BG_INPUT, fg=MUTED,
                  activebackground=AMBER, activeforeground=WHITE,
                  relief="flat", font=FONT_SM, bd=0, padx=6, cursor="hand2",
                  command=self._browse_bridge).pack(side="left")

        # referencia al notebook principal (se inyecta desde PipelineGUI)
        self._notebook_ref = None

        self._refresh_mode()

    def _refresh_mode(self):
        if self._mode.get() == "template":
            self._tpl_frame.pack(fill="x", pady=3)
            self._scratch_frame.pack_forget()
        else:
            self._tpl_frame.pack_forget()
            self._scratch_frame.pack(fill="x", pady=(3, 0))

    def _browse_scratch_out(self):
        p = filedialog.asksaveasfilename(
            defaultextension=".psf",
            filetypes=[("PSF", "*.psf"), ("All", "*.*")],
            initialdir=str(DIR_PSF) if DIR_PSF.exists() else str(SCRIPT_DIR))
        if p: self._scratch_out_var.set(p)

    def _open_generator(self):
        """Salta a la pestaña del Generador PSF."""
        if self._notebook_ref is not None:
            try:
                # El notebook tiene: tab0=Pipeline, tab1=PSF
                self._notebook_ref.select(1)
                return
            except Exception:
                pass
        messagebox.showinfo("Generador PSF",
                            "Cambia a la pestaña 'Generador PSF' para construir el archivo.")

    def use_generated(self, path):
        """Select «desde cero» with the .psf the generator has just written."""
        self._scratch_out_var.set(str(path))
        self._mode.set("scratch")
        self._refresh_mode()

    def set_notebook(self, nb):
        """Llamar desde PipelineGUI para registrar el notebook principal."""
        self._notebook_ref = nb

    def _autodetect_bridge(self):
        # Buscar en todos los RUN_N existentes, del más reciente al más antiguo
        run_dirs = sorted(SCRIPT_DIR.glob("RUN_*/OUTPUT"),
                          key=lambda p: p.parent.name, reverse=True)
        for output_dir in run_dirs:
            c = list(output_dir.glob("99_5th_PERCENTILE*.xlsx"))
            if c: return str(c[0])
        return ""

    def _browse_bridge(self):
        p = filedialog.askopenfilename(
            filetypes=[("Excel", "*.xlsx"), ("All", "*.*")],
            initialdir=str(DIR_RESULTS) if DIR_RESULTS.exists() else str(SCRIPT_DIR))
        if p: self.bridge_var.set(p)

    def show_bridge(self, show):
        if show:
            self._bridge_frame.pack(fill="x", pady=(8, 0))
        else:
            self._bridge_frame.pack_forget()

    def get(self):
        if self._mode.get() == "scratch":
            return {"template_path": self._scratch_out_var.get(),
                    "psf_from_scratch": True,
                    "bridge_excel": self.bridge_var.get()}
        return {"template_path": self._psf.get(),
                "psf_from_scratch": False,
                "bridge_excel":  self.bridge_var.get()}


# =============================================================================
# WIDGET ANÁLISIS DE SENSIBILIDAD
# =============================================================================

class SensitivityWidget(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG_CARD)
        sub = SubSection(self, "Análisis de sensibilidad", color=AMBER)
        sub.pack(fill="x", padx=12, pady=(2, 2))
        body = sub.content

        # Tipo de análisis — toggle
        type_row = tk.Frame(body, bg=BG_CARD)
        type_row.pack(fill="x", pady=(0, 8))

        self._sens_iodo = tk.BooleanVar(value=False)
        iodo_btn = tk.Frame(type_row, bg=BG_INPUT, cursor="hand2",
                            highlightthickness=1, highlightbackground=BORDER)
        tk.Label(iodo_btn, text="Fracciones de yodo",
                 bg=BG_INPUT, fg=TEXT,
                 font=("Segoe UI Semibold", 9), anchor="w"
                 ).pack(fill="x", padx=8, pady=(5, 0))
        tk.Label(iodo_btn, text="Muestreo de AER / I₂ / CH₃I por set",
                 bg=BG_INPUT, fg=MUTED,
                 font=("Segoe UI", 8), anchor="w"
                 ).pack(fill="x", padx=8, pady=(0, 5))
        iodo_btn.bind("<Button-1>", lambda e: self._toggle_iodo())
        for c in iodo_btn.winfo_children():
            c.bind("<Button-1>", lambda e: self._toggle_iodo())
        iodo_btn.pack(side="left", padx=(0, 6))
        self._iodo_btn = iodo_btn

        # Placeholder para futuros análisis
        ph = tk.Frame(type_row, bg=BG_INPUT,
                      highlightthickness=1, highlightbackground=BORDER)
        tk.Label(ph, text="Más análisis",
                 bg=BG_INPUT, fg=MUTED,
                 font=("Segoe UI Semibold", 9), anchor="w"
                 ).pack(fill="x", padx=8, pady=(5, 0))
        tk.Label(ph, text="Próximamente…",
                 bg=BG_INPUT, fg=MUTED,
                 font=("Segoe UI", 8), anchor="w"
                 ).pack(fill="x", padx=8, pady=(0, 5))
        ph.pack(side="left")

        # Panel fracciones de yodo
        self._iodo_panel = tk.Frame(body, bg=BG_CARD)

        sets_row = tk.Frame(self._iodo_panel, bg=BG_CARD)
        sets_row.pack(fill="x", pady=(0, 6))
        FL(sets_row, "Número de sets:", width=20).pack(side="left", padx=(0, 6))
        self.nsets_var = tk.IntVar(value=6)
        SS(sets_row, from_=1, to=999, textvariable=self.nsets_var,
           width=6, command=self._rebuild).pack(side="left", ipady=4)

        self._frac_frame = tk.Frame(self._iodo_panel, bg=BG_CARD)
        self._frac_frame.pack(fill="x")
        self._frac_rows: list = []
        self._rebuild()

    def _toggle_iodo(self):
        self._sens_iodo.set(not self._sens_iodo.get())
        active = self._sens_iodo.get()
        self._iodo_btn.config(bg=BG_SEL if active else BG_INPUT,
                              highlightbackground=BORDER_SEL if active else BORDER)
        for c in self._iodo_btn.winfo_children():
            c.config(bg=BG_SEL if active else BG_INPUT,
                     fg=AMBER if active else (TEXT if "Semibold" in str(c.cget("font")) else MUTED))
        if active:
            self._iodo_panel.pack(fill="x", pady=(8, 0))
        else:
            self._iodo_panel.pack_forget()

    def _rebuild(self):
        for w in self._frac_frame.winfo_children():
            w.destroy()
        self._frac_rows = []
        try: n = int(self.nsets_var.get())
        except Exception: n = 6
        for k in range(1, n+1):
            row = FractionRow(self._frac_frame, k)
            row.pack(fill="x", pady=2)
            self._frac_rows.append(row)

    def get(self):
        if not self._sens_iodo.get():
            return {"nsets": 1, "fixed_sets": [None]}
        fixed = []
        for i, row in enumerate(self._frac_rows, 1):
            try:
                fixed.append(row.get())
            except ValueError:
                raise ValueError(f"Set {i}: fracciones inválidas")
        return {"nsets": self.nsets_var.get(), "fixed_sets": fixed}


class FractionRow(tk.Frame):
    def __init__(self, parent, k):
        super().__init__(parent, bg=BG_CARD)
        tk.Label(self, text=f"Set {k:02d}", bg=BG_CARD, fg=MUTED,
                 font=FONT_SM, width=6, anchor="w").pack(side="left")
        self.rnd = tk.BooleanVar(value=True)
        tk.Checkbutton(self, text="Aleatorio", variable=self.rnd,
                       bg=BG_CARD, fg=MUTED, selectcolor=BG_INPUT,
                       activebackground=BG_CARD, font=FONT_SM,
                       command=self._toggle).pack(side="left", padx=(4, 8))
        self.fvars = []
        for lbl in ("AER", "I₂", "CH₃I"):
            tk.Label(self, text=lbl, bg=BG_CARD, fg=MUTED,
                     font=FONT_SM, width=4).pack(side="left")
            v = tk.StringVar(value="")
            e = SE(self, textvariable=v, width=7)
            e.pack(side="left", ipady=3, padx=(0, 4))
            e.config(state="disabled", disabledbackground=BG_INPUT,
                     disabledforeground=MUTED)
            self.fvars.append((v, e))

    def _toggle(self):
        s = "disabled" if self.rnd.get() else "normal"
        for _, e in self.fvars: e.config(state=s)

    def get(self):
        if self.rnd.get(): return None
        try:
            vals = [float(v.get()) for v, _ in self.fvars]
            if len(vals) != 3 or sum(vals) <= 0: raise ValueError
            s = sum(vals); return tuple(x/s for x in vals)
        except ValueError: raise ValueError("Fracciones inválidas")


# =============================================================================
# CONSOLA DE LOG
# =============================================================================

class LogConsole(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG_APP)
        hdr = tk.Frame(self, bg=BG_APP)
        hdr.pack(fill="x", pady=(0, 4))
        tk.Label(hdr, text="Registro de ejecución", bg=BG_APP,
                 fg=MUTED, font=FONT_BOLD).pack(side="left")
        tk.Button(hdr, text="Limpiar", bg=BG_INPUT, fg=MUTED,
                  relief="flat", font=FONT_SM, bd=0, padx=8, cursor="hand2",
                  activebackground=BORDER, activeforeground=TEXT,
                  command=self.clear).pack(side="right")
        self.text = scrolledtext.ScrolledText(
            self, wrap="word", bg="#FAFBFC", fg=TEXT,
            font=FONT_MONO, relief="flat", bd=0,
            insertbackground=BLUE, selectbackground="#C8D8F0")
        self.text.pack(fill="both", expand=True)
        self.text.tag_config("INFO",    foreground=TEXT)
        self.text.tag_config("WARNING", foreground=WARN)
        self.text.tag_config("ERROR",   foreground=RED)
        self.text.tag_config("SUCCESS", foreground=SUCCESS)
        self.text.tag_config("PHASE",   foreground=BLUE)
        self.text.tag_config("MUTED",   foreground=MUTED)
        self.text.tag_config("TITLE",   foreground=BLUE)

    def append(self, text, tag="INFO"):
        self.text.config(state="normal")
        self.text.insert("end", text+"\n", tag)
        self.text.see("end")
        self.text.config(state="disabled")

    def clear(self):
        self.text.config(state="normal")
        self.text.delete("1.0", "end")
        self.text.config(state="disabled")


# =============================================================================
# BARRA DE ESTADO
# =============================================================================

class StatusBar(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG_INPUT, height=32)
        self.pack_propagate(False)
        self.sv = tk.StringVar(value="Listo")
        tk.Label(self, textvariable=self.sv, bg=BG_INPUT, fg=MUTED,
                 font=FONT_SM, anchor="w").pack(side="left", padx=10)
        self.pb = ttk.Progressbar(self, mode="indeterminate", length=200)
        self.pb.pack(side="right", padx=10, pady=6)
        s = ttk.Style(); s.theme_use("default")
        s.configure("TProgressbar", troughcolor=BG_APP,
                     background=BLUE, borderwidth=0)

    def set_running(self, msg="Ejecutando…"):
        self.sv.set(msg); self.pb.start(15)

    def set_idle(self, msg="Listo"):
        self.sv.set(msg); self.pb.stop()


# =============================================================================
# VENTANA PRINCIPAL
# =============================================================================

class PipelineGUI(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG_APP)
        self._running = False
        self._build_titlebar()
        self._build_main()

    # ── Titlebar ──────────────────────────────────────────────────────────────

    def _build_titlebar(self):
        bar = tk.Frame(self, bg=BG_CARD, height=54)
        bar.pack(fill="x"); bar.pack_propagate(False)
        tk.Label(bar, text="⚛", bg=BG_CARD, fg=BLUE,
                 font=("Segoe UI", 22)).pack(side="left", padx=(14, 6), pady=4)
        tf = tk.Frame(bar, bg=BG_CARD); tf.pack(side="left", pady=4)
        tk.Label(tf, text="ARCON96 + RADTRAD Pipeline",
                 bg=BG_CARD, fg=TEXT,
                 font=("Segoe UI Semibold", 13)).pack(anchor="w")
        tk.Label(tf, text="IDOM · Jon Ander Goiti Larrinaga · 2025",
                 bg=BG_CARD, fg=MUTED, font=("Segoe UI", 8)).pack(anchor="w")

        self.run_btn = tk.Button(
            bar, text="▶  EJECUTAR PIPELINE",
            bg=BLUE, fg=WHITE, activebackground="#2563EB", activeforeground=WHITE,
            relief="flat", font=("Segoe UI Semibold", 10),
            bd=0, padx=20, pady=8, cursor="hand2",
            command=self._run)
        self.run_btn.pack(side="right", padx=14, pady=8)

        for label, cmd in (("💾  Guardar config", self._save),
                           ("📂  Cargar config",  self._load)):
            tk.Button(bar, text=label, bg=BG_INPUT, fg=MUTED,
                      activebackground=BORDER, activeforeground=TEXT,
                      relief="flat", font=FONT_SM, bd=0, padx=12, pady=8,
                      cursor="hand2", command=cmd).pack(side="right", padx=3, pady=8)
        tk.Button(bar, text="?  Ayuda", bg=BG_INPUT, fg=BLUE,
                  activebackground=BLUE, activeforeground=WHITE,
                  relief="flat", font=("Segoe UI Semibold", 9), bd=0,
                  padx=10, pady=8, cursor="hand2",
                  command=lambda: ReadmeWindow(self)).pack(side="right", padx=3, pady=8)

    # ── Layout principal ──────────────────────────────────────────────────────

    def _build_main(self):
        paned = tk.PanedWindow(self, orient="horizontal", bg=BG_APP,
                               sashwidth=4, sashrelief="flat")
        paned.pack(fill="both", expand=True)

        # Panel izquierdo con scroll
        left = tk.Frame(paned, bg=BG_APP)
        paned.add(left, minsize=580, width=640)

        canvas = tk.Canvas(left, bg=BG_APP, highlightthickness=0)
        vsb = tk.Scrollbar(left, orient="vertical", command=canvas.yview,
                           bg=BG_INPUT, troughcolor=BG_APP, activebackground=BORDER)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        sf = tk.Frame(canvas, bg=BG_APP)
        cw = canvas.create_window((0, 0), window=sf, anchor="nw")

        def _resize(e=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(cw, width=canvas.winfo_width())

        sf.bind("<Configure>", _resize)
        canvas.bind("<Configure>", _resize)
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        # ── Tipo de instalación (embarcación / planta terrestre) ───────────────
        self.inst_widget = InstalacionWidget(sf, on_change=self._on_instalacion)
        self.inst_widget.pack(fill="x", padx=8, pady=(8, 0))

        # ── SECCIÓN 1: Factores de dispersión X/Q ─────────────────────────────
        self.sec_xq = Section(
            sf, "  Cálculo de factores de dispersión X/Q",
            color=BLUE, on_toggle=self._on_xq_toggle)
        self.sec_xq.pack(fill="x", padx=8, pady=(8, 4))

        self.met_widget   = MetWidget(self.sec_xq.body)
        self.arcon_widget = ArconWidget(self.sec_xq.body)
        self.met_widget.pack(fill="x", pady=(8, 0))
        self.arcon_widget.pack(fill="x", pady=(4, 8))

        # ── SECCIÓN 2: Consecuencias radiológicas ─────────────────────────────
        self.sec_rad = Section(
            sf, "  Cálculo de consecuencias radiológicas",
            color=AMBER, on_toggle=self._on_rad_toggle)
        self.sec_rad.pack(fill="x", padx=8, pady=(4, 8))

        self.psf_widget  = PsfWidget(self.sec_rad.body)
        self.nif_widget  = NifWidget(self.sec_rad.body)
        self.sens_widget = SensitivityWidget(self.sec_rad.body)

        # RFT
        rft_sub = SubSection(self.sec_rad.body, "Archivo RFT", color=AMBER)
        rft_sub.pack(fill="x", padx=12, pady=(2, 2))
        rft_def = self._first(DIR_RFT, "*.rft") or "tid_dba.rft"
        self.rft_picker = FilePicker(rft_sub.content, ".rft:", rft_def,
                                      filetypes=[("RFT", "*.rft"), ("All", "*.*")], lw=8)
        self.rft_picker.pack(fill="x", pady=3)

        # INP
        inp_sub = SubSection(self.sec_rad.body, "Archivo INP", color=AMBER)
        inp_sub.pack(fill="x", padx=12, pady=(2, 2))
        inp_def = self._first(DIR_INP, "*.inp") or "fgr11&12.inp"
        self.inp_picker = FilePicker(inp_sub.content, ".inp:", inp_def,
                                      filetypes=[("INP", "*.inp"), ("All", "*.*")], lw=8)
        self.inp_picker.pack(fill="x", pady=3)

        # RADTRAD exe
        exe_sub = SubSection(self.sec_rad.body, "Ejecutable RADTRAD", color=AMBER)
        exe_sub.pack(fill="x", padx=12, pady=(2, 2))
        exe_row = tk.Frame(exe_sub.content, bg=BG_CARD)
        exe_row.pack(fill="x", pady=3)
        FL(exe_row, "radtrad.exe:", width=14).pack(side="left", padx=(0, 6))
        self.radtrad_exe = tk.StringVar(value=str(RADTRAD_EXE_DEFAULT))
        SE(exe_row, textvariable=self.radtrad_exe, width=40
           ).pack(side="left", ipady=4, padx=(0, 4))
        tk.Button(exe_row, text="…", bg=BG_INPUT, fg=MUTED,
                  activebackground=AMBER, activeforeground=WHITE,
                  relief="flat", font=FONT_SM, bd=0, padx=6, cursor="hand2",
                  command=self._browse_radtrad).pack(side="left")

        # PSF, NIF, sensibilidad
        self.psf_widget.pack(fill="x", pady=(2, 2))
        self.nif_widget.pack(fill="x", pady=(2, 2))
        self.sens_widget.pack(fill="x", pady=(2, 2))

        # Borrar directorios RADTRAD
        del_sub = SubSection(self.sec_rad.body, "Limpieza", color=AMBER)
        del_sub.pack(fill="x", padx=12, pady=(2, 8))
        del_card = tk.Frame(del_sub.content, bg=BG_WARN,
                            highlightthickness=1, highlightbackground="#D4A017")
        del_card.pack(fill="x")
        self.delete_radtrad = tk.BooleanVar(value=False)
        tk.Checkbutton(del_card,
                       text="Borrar directorios de ejecución RADTRAD al finalizar",
                       variable=self.delete_radtrad, bg=BG_WARN, fg=TEXT,
                       selectcolor=BG_CARD, activebackground=BG_WARN,
                       font=FONT_SM).pack(anchor="w", padx=8, pady=(6, 2))
        tk.Label(del_card,
                 text="Se conserva Sets_Worst2h.xlsx. "
                      "Se eliminan subdirectorios frac_set_XX/ con PSFs y .o0.",
                 bg=BG_WARN, fg=WARN, font=("Segoe UI", 8),
                 wraplength=480, justify="left").pack(anchor="w", padx=8, pady=(0, 6))

        # Panel derecho: consola
        right = tk.Frame(paned, bg=BG_APP)
        paned.add(right, minsize=340)
        self.log = LogConsole(right)
        self.log.pack(fill="both", expand=True, padx=8, pady=(8, 4))
        self.status = StatusBar(right)
        self.status.pack(fill="x", pady=(0, 4))
        self._welcome()

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _first(folder, pattern):
        if folder.exists():
            c = sorted(folder.glob(pattern))
            if c: return c[0].name
        return None

    def _browse_radtrad(self):
        p = filedialog.askopenfilename(filetypes=[("Exe", "*.exe"), ("All", "*.*")])
        if p: self.radtrad_exe.set(p)

    def _welcome(self):
        for t, tag in [
            ("ARCON96 + RADTRAD  — Unified Pipeline", "TITLE"),
            ("", "INFO"),
            ("Activa las secciones con los toggles y pulsa EJECUTAR.", "MUTED"),
            ("", "INFO"),
            ("  FASE 0a  NIF generation   (auto)", "MUTED"),
            ("  FASE 0b  MET: revisión y formato ARCON96 (o desde Excel)", "MUTED"),
            ("  FASE 1   ARCON96  batch   → Bridge Excel X/Q", "MUTED"),
            ("  FASE 2   RADTRAD  PSF+run → .o0 outputs", "MUTED"),
            ("  FASE 3   Post-proc        → Sets_Worst2h.xlsx", "MUTED"),
            ("  FASE 4   Zonas EAB/LPZ    → mapa_zonas.html", "MUTED"),
            ("", "INFO"),
            ("Resultados en RUN_N/OUTPUT/", "MUTED"),
            ("", "INFO"),
        ]:
            self.log.append(t, tag)

    # ── Callbacks toggle ──────────────────────────────────────────────────────

    def _on_instalacion(self, tipo):
        """Propose the distance sweep of the installation type (it can still be edited)."""
        dmin, dmax, dd = InstalacionWidget.DEFAULTS[tipo]
        self.arcon_widget.set_distances(dmin, dmax, dd)
        self.log.append(f"Instalación: {'embarcación' if tipo == 'buque' else 'planta terrestre'} · "
                        f"barrido propuesto {dmin}–{dmax} m, paso {dd} m", "MUTED")

    def _on_xq_toggle(self, state):
        # Si X/Q está OFF → mostrar bridge picker en PSF
        self.psf_widget.show_bridge(not state and self.sec_rad.is_active())
        self._update_run_label()

    def _on_rad_toggle(self, state):
        self.psf_widget.show_bridge(not self.sec_xq.is_active() and state)
        self._update_run_label()

    def _update_run_label(self):
        xq  = self.sec_xq.is_active()
        rad = self.sec_rad.is_active()
        if xq and rad:   lbl = "▶  EJECUTAR PIPELINE COMPLETO"
        elif xq:         lbl = "▶  EJECUTAR  ARCON96"
        elif rad:        lbl = "▶  EJECUTAR  RADTRAD"
        else:            lbl = "▶  EJECUTAR"
        self.run_btn.config(text=lbl)

    # ── Recopilar parámetros ──────────────────────────────────────────────────

    def _collect(self):
        p = {}
        p.update(self.met_widget.get())
        p.update(self.arcon_widget.get())
        p.update(self.psf_widget.get())
        p.update(self.nif_widget.get())
        p.update(self.sens_widget.get())
        p.update(self.inst_widget.get())
        nif_data = self.nif_widget.get()
        p["support_names"] = (
            Path(self.rft_picker.get()).name,
            Path(nif_data["nif_path"]).name if nif_data["nif_mode"] == "existing"
            else "i_SMR.NIF",
            Path(self.inp_picker.get()).name,
        )
        p["radtrad_exe"]      = self.radtrad_exe.get()
        p["delete_radtrad"]   = self.delete_radtrad.get()
        p["no_run"]           = False
        p["out_root"]         = str(SCRIPT_DIR)  # ENGINE calcula RUN_N automáticamente
        p["run_arcon"]        = self.sec_xq.is_active()
        p["run_radtrad"]      = self.sec_rad.is_active()
        return p

    # ── Guardar / cargar ──────────────────────────────────────────────────────

    def _save(self):
        try: p = self._collect()
        except Exception as e:
            messagebox.showerror("Error", str(e)); return
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json"), ("All", "*.*")],
            initialfile="pipeline_config.json")
        if not path: return
        p["fixed_sets"] = [list(s) if s else None for s in p.get("fixed_sets", [])]
        p["met_paths"]  = [str(x) for x in p.get("met_paths", [])]
        Path(path).write_text(json.dumps(p, indent=2), encoding="utf-8")
        self.log.append(f"✓ Configuración guardada: {path}", "SUCCESS")

    def _load(self):
        path = filedialog.askopenfilename(
            filetypes=[("JSON", "*.json"), ("All", "*.*")])
        if not path: return
        try:
            d = json.loads(Path(path).read_text(encoding="utf-8"))
            mw = self.met_widget
            mode = d.get("met_mode", "files")
            mw._set_mode(mode)
            if mode == "files":
                mw.num_met_var.set(d.get("num_met", 1))
                mw._met_paths = [Path(x) for x in d.get("met_paths", [])]
                mw._refresh_list()
            else:
                ep = d.get("excel_path", "")
                mw.excel_var.set(ep)
                if ep: mw._detect_sheets(Path(ep))

            aw = self.arcon_widget
            aw.dist_min.set(d.get("dist_min", 10))
            aw.dist_max.set(d.get("dist_max", 400))
            aw.delta.set(d.get("delta", 10))
            if "arcon_exe" in d: aw.arcon_exe.set(d["arcon_exe"])
            aw.delete_dirs.set(d.get("delete_arcon_dirs", False))

            self.inst_widget.set(d)
            aw.keep_work.set(d.get("keep_work", True)); aw.sens_met.set(d.get("sensibilidad_met", False))
            if d.get("psf_from_scratch") and d.get("template_path"):
                self.psf_widget.use_generated(d["template_path"])
            elif "template_path" in d:
                self.psf_widget._mode.set("template"); self.psf_widget._refresh_mode()
                self.psf_widget._psf.var.set(d["template_path"])
            if "bridge_excel"  in d: self.psf_widget.bridge_var.set(d["bridge_excel"])
            if "radtrad_exe"   in d: self.radtrad_exe.set(d["radtrad_exe"])
            self.delete_radtrad.set(d.get("delete_radtrad", False))

            sw = self.sens_widget
            sw.nsets_var.set(d.get("nsets", 6))
            sw._rebuild()
            for i, s in enumerate(d.get("fixed_sets", [])):
                if i < len(sw._frac_rows):
                    row = sw._frac_rows[i]
                    if s is None: row.rnd.set(True); row._toggle()
                    else:
                        row.rnd.set(False); row._toggle()
                        for j, (v, _) in enumerate(row.fvars):
                            v.set(str(s[j]) if j < len(s) else "")

            sn = d.get("support_names", ("","",""))
            if len(sn) >= 3:
                self.rft_picker.var.set(sn[0])
                self.inp_picker.var.set(sn[2])

            self.sec_xq.set_active(d.get("run_arcon",   True))
            self.sec_rad.set_active(d.get("run_radtrad", True))
            self._update_run_label()
            self.log.append(f"✓ Configuración cargada: {path}", "SUCCESS")
        except Exception as e:
            messagebox.showerror("Error al cargar", str(e))

    # ── Ejecución ─────────────────────────────────────────────────────────────

    def _run(self):
        if self._running: return
        # Verificar dependencias del pipeline
        try:
            from RADTRAD_ENGINE import _PIPELINE_DEPS_OK, _PIPELINE_DEPS_ERROR
            if not _PIPELINE_DEPS_OK:
                messagebox.showerror(
                    "Dependencias no instaladas",
                    f"No se puede ejecutar el pipeline:\n{_PIPELINE_DEPS_ERROR}\n\n"
                    "Instala con:\n  pip install numpy pandas openpyxl")
                return
        except Exception:
            pass
        try: params = self._collect()
        except Exception as e:
            messagebox.showerror("Error de validación", str(e)); return

        run_xq  = params["run_arcon"]
        run_rad = params["run_radtrad"]

        if not run_xq and not run_rad:
            messagebox.showwarning("Sin fases activas",
                                   "Activa al menos una sección para ejecutar."); return

        errors = []
        if run_xq:
            if params["dist_max"] <= params["dist_min"]:
                errors.append("dist_max debe ser mayor que dist_min")
            if params["met_mode"] == "files" and params["num_met"] < 1:
                errors.append("Indica al menos 1 archivo MET")
            if params["met_mode"] == "excel" and not params["excel_path"]:
                errors.append("Selecciona el archivo Excel MET*.xlsx")

        if run_rad and not Path(params.get("template_path") or "").is_file():
            errors.append("No existe el PSF: " + str(params.get("template_path") or "(sin indicar)")
                          + ("\nGenéralo en la pestaña «Generador PSF» con «Usar en el cálculo»."
                             if params.get("psf_from_scratch") else ""))
        if run_xq and params["dist_max"] > 1200:
            if not messagebox.askyesno("Distancia máxima", "ARCON96 se validó hasta unos 1.200 m; por encima, el "
                                       "X/Q es una extrapolación.\n\n¿Continuar?"):
                return

        if run_rad and not run_xq:
            bridge = params.get("bridge_excel", "").strip()
            if not bridge or not Path(bridge).exists():
                errors.append("Selecciona un Bridge Excel válido de ARCON96")
            else:
                try:
                    dmin, dmax, dd = read_distances_from_bridge_excel(Path(bridge))
                    params["dist_min"] = dmin
                    params["dist_max"] = dmax
                    params["delta"]    = dd
                    self.arcon_widget.set_distances(dmin, dmax, dd)
                    self.log.append(
                        f"  Distancias del Bridge Excel: {dmin}–{dmax} m, paso {dd} m",
                        "MUTED")
                except ValueError as e:
                    errors.append(str(e))

        if errors:
            messagebox.showerror("Parámetros inválidos", "\n".join(errors)); return

        if run_xq:
            if params["met_mode"] == "files" and params["met_paths"]:
                self._copy_mets(params["met_paths"])
            if params["met_mode"] == "excel" and params["excel_path"]:
                self._copy_excel(Path(params["excel_path"]))

        self._running = True
        self.run_btn.config(state="disabled", text="⏳  Ejecutando…",
                            bg=BG_INPUT, fg=MUTED)
        self.status.set_running()
        self.log.clear()
        lbl = ("ARCON96 + RADTRAD" if run_xq and run_rad
               else "Solo ARCON96" if run_xq else "Solo RADTRAD")
        self.log.append(f"▶  {lbl}", "PHASE")
        self.log.append("", "INFO")

        threading.Thread(target=self._execute, args=(params,), daemon=True).start()

    def _copy_mets(self, paths):
        DIR_MET.mkdir(parents=True, exist_ok=True)
        for i, src in enumerate(paths, 1):
            dst = DIR_MET / f"MET{i:02d}.MET"
            if src.resolve() != dst.resolve():
                try:
                    shutil.copy2(src, dst)
                    self.log.append(f"  Copiado: {src.name} → {dst.name}", "MUTED")
                except Exception as e:
                    self.log.append(f"  Error: {e}", "ERROR")

    def _copy_excel(self, src):
        DIR_NIF.mkdir(parents=True, exist_ok=True)
        dst = DIR_INFO / src.name
        if src.resolve() != dst.resolve():
            try:
                shutil.copy2(src, dst)
                self.log.append(f"  Excel copiado a 00INFO/: {src.name}", "MUTED")
            except Exception as e:
                self.log.append(f"  Error: {e}", "ERROR")

    def _execute(self, params):
        """
        Lanza RADTRAD_ENGINE.py en modo GUI usando --gui-mode y --params <json>.
        No usa stdin — los parámetros viajan en un JSON temporal.
        """
        import tempfile, os
        pipeline = SCRIPT_DIR / "RADTRAD_ENGINE.py"
        if not pipeline.exists():
            self._lt(f"✗ No se encontró RADTRAD_ENGINE.py en: {SCRIPT_DIR}", "ERROR")
            self._finish(False); return

        # Serializar parámetros a JSON
        p_json = dict(params)
        p_json["template_path"] = str(params.get("template_path", ""))
        p_json["radtrad_exe"]   = str(params.get("radtrad_exe", ""))
        p_json["out_root"]      = str(params.get("out_root", str(DIR_RADTRAD)))
        p_json["fixed_sets"]    = [
            list(s) if s else None for s in params.get("fixed_sets", [None])
        ]
        p_json["support_names"] = list(params.get("support_names", ("", "", "")))
        p_json["met_paths"]     = [str(x) for x in params.get("met_paths", [])]

        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False,
            encoding="utf-8", dir=str(SCRIPT_DIR))
        json.dump(p_json, tmp, indent=2)
        tmp.close()
        tmp_path = tmp.name

        try:
            proc = subprocess.Popen(
                [sys.executable, str(pipeline),
                 "--gui-mode", "--params", tmp_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True, encoding="utf-8", errors="replace",
                cwd=str(SCRIPT_DIR))
            for line in proc.stdout:
                line = line.rstrip()
                self._lt(line, self._tag(line))
            proc.wait()
            success = proc.returncode == 0
        except FileNotFoundError:
            self._lt("✗ Python no encontrado.", "ERROR"); success = False
        except Exception as e:
            self._lt(f"✗ Error: {e}", "ERROR"); success = False
        finally:
            try: os.unlink(tmp_path)
            except Exception: pass
        self._finish(success)

    def _tag(self, line):
        ll = line.lower()
        if "error" in ll or "✗" in ll or "failed" in ll: return "ERROR"
        if "warning" in ll or "warn" in ll: return "WARNING"
        if "phase" in ll or "==" in line:   return "PHASE"
        if "complete" in ll or "✓" in ll or " ok" in ll: return "SUCCESS"
        if line.startswith("  ") and ":" in line: return "MUTED"
        return "INFO"

    def _lt(self, text, tag="INFO"):
        self.after(0, lambda: self.log.append(text, tag))

    def _finish(self, success):
        def _f():
            self._running = False
            self._update_run_label()
            self.run_btn.config(state="normal", bg=BLUE, fg=WHITE)
            if success:
                self.status.set_idle("✓ Completado")
                self.log.append("", "INFO")
                self.log.append("✓ COMPLETADO", "SUCCESS")
                if getattr(self, "on_run_finished", None):
                    try:
                        self.on_run_finished(True)      # map tab: load the new results
                    except Exception as e:
                        self.log.append(f"Mapa de zonas: {e}", "WARN")
            else:
                self.status.set_idle("✗ Error")
                self.log.append("", "INFO")
                self.log.append("✗ Finalizó con errores.", "ERROR")
        self.after(0, _f)



# =============================================================================
# PSF GUI
# =============================================================================


class SCombo(ttk.Combobox):
    def __init__(self, parent, values, width=18, **kw):
        super().__init__(parent, values=values, width=width,
                         state="readonly", font=FONT_UI, **kw)
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TCombobox", fieldbackground=INPUT,
                        background=INPUT, foreground=TEXT,
                        selectbackground=BLUE, selectforeground=WHITE)


def FL(parent, text, width=20, color=MUTED, bg=CARD):
    return tk.Label(parent, text=text, bg=bg, fg=color,
                    font=FONT_SM, anchor="w", width=width)




class ToggleSwitch(tk.Canvas):
    """Toggle ON/OFF animado."""
    W, H, R = 52, 26, 11
    ON_COLOR  = "#2ECC40"
    OFF_COLOR = "#AAAAAA"
    STEPS, MS = 6, 10

    def __init__(self, parent, initial=False, callback=None, bg=CARD, **kw):
        super().__init__(parent, width=self.W, height=self.H,
                         bg=bg, highlightthickness=0, cursor="hand2", **kw)
        self._state    = initial
        self._callback = callback
        self._cx       = self._target_cx(initial)
        self._anim     = False
        self._draw()
        self.bind("<Button-1>", lambda e: self._click())

    def _target_cx(self, state):
        return self.W - self.H // 2 - 2 if state else self.H // 2 + 2

    def _draw(self):
        self.delete("all")
        c = self.ON_COLOR if self._state else self.OFF_COLOR
        r = self.H // 2
        self.create_arc(0, 0, self.H, self.H, start=90, extent=180,
                        fill=c, outline=c)
        self.create_arc(self.W - self.H, 0, self.W, self.H, start=270,
                        extent=180, fill=c, outline=c)
        self.create_rectangle(r, 0, self.W - r, self.H, fill=c, outline=c)
        cx = int(self._cx)
        self.create_oval(cx - self.R, self.H // 2 - self.R,
                         cx + self.R, self.H // 2 + self.R,
                         fill=WHITE, outline=WHITE)

    def _click(self):
        if self._anim: return
        self._state = not self._state
        if self._callback: self._callback(self._state)
        self._animate()

    def _animate(self):
        target = self._target_cx(self._state)
        start  = self._cx
        step   = (target - start) / self.STEPS
        self._anim = True
        def _s(i):
            if i >= self.STEPS:
                self._cx = target; self._draw(); self._anim = False; return
            self._cx = start + step * i; self._draw()
            self.after(self.MS, lambda: _s(i + 1))
        _s(1)

    def get(self): return self._state
    def set(self, v):
        self._state = bool(v)
        self._cx    = self._target_cx(self._state)
        self._draw()


class FieldRow(tk.Frame):
    """Fila: label + widget (entry / combo / toggle), opcional unidad."""
    def __init__(self, parent, label, widget_factory,
                 unit="", lw=22, bg=CARD, **kw):
        super().__init__(parent, bg=bg, **kw)
        FL(self, label, width=lw, bg=bg).pack(side="left", padx=(0, 6))
        self.widget = widget_factory(self)
        self.widget.pack(side="left", ipady=4 if isinstance(self.widget, SE) else 0)
        if unit:
            tk.Label(self, text=unit, bg=bg, fg=MUTED,
                     font=FONT_SM).pack(side="left", padx=(4, 0))

    def get(self):
        w = self.widget
        if hasattr(w, "get"): return w.get()

    def set(self, v):
        w = self.widget
        if isinstance(w, ToggleSwitch): w.set(v)
        elif isinstance(w, tk.Entry):
            w.delete(0, "end"); w.insert(0, str(v))
        elif isinstance(w, ttk.Combobox): w.set(str(v))


class SectionCard(tk.Frame):
    """Tarjeta con cabecera coloreada y cuerpo scrollable."""
    def __init__(self, parent, title, color=BLUE, **kw):
        kw.setdefault("bg", CARD)
        super().__init__(parent, highlightthickness=1,
                         highlightbackground=BORDER, **kw)
        hdr = tk.Frame(self, bg=color)
        hdr.pack(fill="x")
        tk.Label(hdr, text=title, bg=color, fg=WHITE,
                 font=FONT_BOLD, anchor="w", padx=12, pady=8).pack(side="left")
        self.body = tk.Frame(self, bg=CARD)
        self.body.pack(fill="both", expand=True, padx=12, pady=10)


# =============================================================================
# TABLA EDITABLE (tiempo + 1..4 columnas)
# =============================================================================

class TimeTable(tk.Frame):
    """
    Widget de tabla editable con N filas y M columnas de valores.
    Columnas: tiempo + cols (nombres de los valores).
    """
    MAX_ROWS = 10

    def __init__(self, parent, col_names: list[str], bg=CARD,
                 default_rows=2, **kw):
        super().__init__(parent, bg=bg, **kw)
        self._cols  = col_names  # sin contar tiempo
        self._rows  = []         # lista de listas de StringVar

        # Cabecera
        hdr = tk.Frame(self, bg=bg)
        hdr.pack(fill="x")
        for j, name in enumerate(["Tiempo (h)"] + col_names):
            tk.Label(hdr, text=name, bg=bg, fg=MUTED,
                     font=("Segoe UI Semibold", 8),
                     width=12, anchor="center").grid(row=0, column=j, padx=2)

        # Contenedor de filas
        self._row_frame = tk.Frame(self, bg=bg)
        self._row_frame.pack(fill="x")

        # Botones +/-
        btn_row = tk.Frame(self, bg=bg)
        btn_row.pack(anchor="w", pady=(4, 0))
        for text, cmd in (("+  Fila", self._add_row),
                          ("−  Fila", self._del_row)):
            tk.Button(btn_row, text=text, bg=INPUT, fg=TEXT,
                      relief="flat", font=FONT_SM, bd=0, padx=8, pady=2,
                      cursor="hand2",
                      activebackground=BLUE, activeforeground=WHITE,
                      command=cmd).pack(side="left", padx=(0, 4))

        for _ in range(default_rows):
            self._add_row()
        if default_rows == 2:                    # 0 h and 720 h: RADTRAD needs increasing times
            self._rows[1][0].set("720.0")

    def _add_row(self):
        if len(self._rows) >= self.MAX_ROWS:
            return
        row_vars = [tk.StringVar(value="0.0") for _ in range(len(self._cols) + 1)]
        self._rows.append(row_vars)
        self._redraw()

    def _del_row(self):
        if len(self._rows) > 1:
            self._rows.pop()
            self._redraw()

    def _redraw(self):
        for w in self._row_frame.winfo_children():
            w.destroy()
        for i, row_vars in enumerate(self._rows):
            for j, var in enumerate(row_vars):
                e = SE(self._row_frame, width=10, textvariable=var)
                e.grid(row=i, column=j, padx=2, pady=1, ipady=3)

    def get_data(self) -> dict:
        """Devuelve {col_name: [float, ...]} incluyendo 'tiempo'."""
        out = {n: [] for n in ["tiempo"] + self._cols}
        for row_vars in self._rows:
            vals = []
            for v in row_vars:
                try:
                    vals.append(float(v.get()))
                except ValueError:
                    vals.append(0.0)
            out["tiempo"].append(vals[0])
            for j, name in enumerate(self._cols):
                out[name].append(vals[j + 1])
        return out

    def set_data(self, data: dict):
        """Carga datos desde dict {col_name: [float, ...]}."""
        times = data.get("tiempo", [])
        n = len(times)
        while len(self._rows) < n:
            self._add_row()
        while len(self._rows) > max(n, 1):
            self._del_row()
        for i, t in enumerate(times):
            self._rows[i][0].set(str(t))
            for j, name in enumerate(self._cols):
                vals = data.get(name, [])
                self._rows[i][j + 1].set(str(vals[i]) if i < len(vals) else "0.0")
        self._redraw()


# =============================================================================
# PANEL DE COMPARTIMENTO
# =============================================================================

class CompPanel(tk.Frame):
    """Panel de edición para un compartimento."""
    def __init__(self, parent, index: int, on_delete, bg=CARD, **kw):
        super().__init__(parent, bg=bg, highlightthickness=1,
                         highlightbackground=BORDER, **kw)
        self._idx = index

        # ── Cabecera ─────────────────────────────────────────────────────────
        hdr = tk.Frame(self, bg=GREEN)
        hdr.pack(fill="x")
        self._title_lbl = tk.Label(hdr, text=f"Compartimento {index}",
                                   bg=GREEN, fg=WHITE, font=FONT_BOLD,
                                   anchor="w", padx=10, pady=6)
        self._title_lbl.pack(side="left")
        tk.Button(hdr, text="✕ Eliminar", bg=GREEN, fg=WHITE,
                  activebackground="#CF222E", activeforeground=WHITE,
                  relief="flat", font=FONT_SM, bd=0, padx=8,
                  cursor="hand2", command=on_delete).pack(side="right", padx=6)

        body = tk.Frame(self, bg=CARD)
        body.pack(fill="x", padx=10, pady=8)

        # ── Campos básicos ────────────────────────────────────────────────────
        self.name_var  = tk.StringVar(value=f"Compartment {index}")
        self.vol_var   = tk.StringVar(value="0.0")

        r1 = tk.Frame(body, bg=CARD); r1.pack(fill="x", pady=2)
        FL(r1, "Nombre:", width=20).pack(side="left", padx=(0,6))
        SE(r1, textvariable=self.name_var, width=30).pack(side="left", ipady=4)

        r2 = tk.Frame(body, bg=CARD); r2.pack(fill="x", pady=2)
        FL(r2, "Tipo:", width=20).pack(side="left", padx=(0,6))
        self.type_combo = SCombo(r2, ["1 – Control Room",
                                       "2 – Environment",
                                       "3 – Other"], width=20)
        self.type_combo.current(2)
        self.type_combo.pack(side="left")

        r3 = tk.Frame(body, bg=CARD); r3.pack(fill="x", pady=2)
        FL(r3, "Volumen:", width=20).pack(side="left", padx=(0,6))
        SE(r3, textvariable=self.vol_var, width=14).pack(side="left", ipady=4)
        tk.Label(r3, text="m³", bg=CARD, fg=MUTED, font=FONT_SM).pack(side="left", padx=(4,0))

        # ── Flags con toggles ─────────────────────────────────────────────────
        hline(body, pady=6)
        tk.Label(body, text="Características físicas", bg=CARD, fg=MUTED,
                 font=("Segoe UI Semibold", 8)).pack(anchor="w", pady=(0,4))

        flags_row = tk.Frame(body, bg=CARD)
        flags_row.pack(fill="x", pady=2)

        self._flags = {}
        flag_defs = [
            ("sprays",     "Sprays"),
            ("filters",    "Filtros recirc."),
            ("deposition", "Dep. natural"),
            ("opool",      "Overlying pool"),
            ("detail",     "Output detallado"),
            ("decay",      "Decay chain"),
        ]
        for i, (key, label) in enumerate(flag_defs):
            col = tk.Frame(flags_row, bg=CARD)
            col.pack(side="left", padx=(0, 16))
            tk.Label(col, text=label, bg=CARD, fg=MUTED,
                     font=FONT_SM).pack(anchor="w")
            t = ToggleSwitch(col, initial=False,
                             bg=CARD, callback=lambda v, k=key: self._on_flag(k, v))
            t.pack(anchor="w", pady=2)
            self._flags[key] = t

        # ── Sección filtros (visible si filters=ON) ───────────────────────────
        self._filter_sec = tk.Frame(body, bg=BG_WARN,
                                    highlightthickness=1,
                                    highlightbackground="#D4A017")
        fs = self._filter_sec
        tk.Label(fs, text="Filtros de recirculación", bg=BG_WARN, fg=WARN,
                 font=FONT_BOLD, anchor="w").pack(fill="x", padx=8, pady=(6,2))
        r_flow = tk.Frame(fs, bg=BG_WARN); r_flow.pack(fill="x", padx=8, pady=2)
        FL(r_flow, "Caudal normalizado:", width=22, bg=BG_WARN).pack(side="left", padx=(0,6))
        self.filter_flow_var = tk.StringVar(value="0.0")
        SE(r_flow, textvariable=self.filter_flow_var, width=12).pack(side="left", ipady=4)
        tk.Label(r_flow, text="1/s", bg=BG_WARN, fg=MUTED, font=FONT_SM).pack(side="left", padx=4)
        tk.Label(fs, text="Eficiencias (tiempo h, Aerosol%, Elemental%, Orgánico%)",
                 bg=BG_WARN, fg=MUTED, font=FONT_SM, anchor="w").pack(fill="x", padx=8)
        self.filter_table = TimeTable(fs,
                                       col_names=["Aerosol %", "Elemental %", "Orgánico %"],
                                       bg=BG_WARN, default_rows=2)
        self.filter_table.pack(padx=8, pady=(2,8))

        # ── Sección deposición (visible si deposition=ON) ─────────────────────
        self._dep_sec = tk.Frame(body, bg="#EBF5FF",
                                  highlightthickness=1,
                                  highlightbackground=BORDER)
        ds = self._dep_sec
        tk.Label(ds, text="Deposición natural — Aerosoles", bg="#EBF5FF", fg=BLUE,
                 font=FONT_BOLD, anchor="w").pack(fill="x", padx=8, pady=(6,2))
        dm_row = tk.Frame(ds, bg="#EBF5FF"); dm_row.pack(fill="x", padx=8, pady=2)
        FL(dm_row, "Modelo aerosoles:", width=20, bg="#EBF5FF").pack(side="left", padx=(0,6))
        self.dep_aer_combo = SCombo(dm_row,
            ["0 – Ninguno", "1 – Usuario", "2 – Henry", "3 – Powers"], width=18)
        self.dep_aer_combo.current(0)
        self.dep_aer_combo.pack(side="left")
        self.dep_aer_combo.bind("<<ComboboxSelected>>", lambda e: self._refresh_dep())

        # Sub-panel usuario
        self._dep_user_frame = tk.Frame(ds, bg="#EBF5FF")
        tk.Label(self._dep_user_frame, text="Coeficientes usuario (t h, coef /s)",
                 bg="#EBF5FF", fg=MUTED, font=FONT_SM, anchor="w").pack(fill="x", padx=8)
        self.dep_user_table = TimeTable(self._dep_user_frame, ["Coef (/s)"],
                                         bg="#EBF5FF", default_rows=2)
        self.dep_user_table.pack(padx=8, pady=(0,6))

        # Sub-panel Henry
        self._dep_henry_frame = tk.Frame(ds, bg="#EBF5FF")
        tk.Label(self._dep_henry_frame, text="Modelo Henry (t h, altura m, densidad g/cc)",
                 bg="#EBF5FF", fg=MUTED, font=FONT_SM, anchor="w").pack(fill="x", padx=8)
        self.dep_henry_table = TimeTable(self._dep_henry_frame,
                                          ["Altura (m)", "Densidad (g/cc)"],
                                          bg="#EBF5FF", default_rows=2)
        self.dep_henry_table.pack(padx=8, pady=(0,6))

        # Sub-panel Powers
        self._dep_powers_frame = tk.Frame(ds, bg="#EBF5FF")
        pf = self._dep_powers_frame
        pr_row = tk.Frame(pf, bg="#EBF5FF"); pr_row.pack(fill="x", padx=8, pady=2)
        FL(pr_row, "Reactor / accidente:", width=20, bg="#EBF5FF").pack(side="left", padx=(0,6))
        self.dep_powers_reactor = SCombo(pr_row,
            ["1 – PWR-DBA", "2 – PWR-SA", "3 – BWR-DBA",
             "4 – BWR-SA", "5 – APWR-DBA"], width=18)
        self.dep_powers_reactor.current(0)
        self.dep_powers_reactor.pack(side="left")
        pp_row = tk.Frame(pf, bg="#EBF5FF"); pp_row.pack(fill="x", padx=8, pady=2)
        FL(pp_row, "Percentil:", width=20, bg="#EBF5FF").pack(side="left", padx=(0,6))
        self.dep_powers_pctile = SCombo(pp_row, ["10.0", "50.0", "90.0"], width=8)
        self.dep_powers_pctile.current(1)
        self.dep_powers_pctile.pack(side="left")

        # Deposición elemental
        hline(ds, color="#B5D4F4", bg="#EBF5FF")
        tk.Label(ds, text="Deposición elemental", bg="#EBF5FF", fg=BLUE,
                 font=("Segoe UI Semibold", 9), anchor="w").pack(fill="x", padx=8)
        de_row = tk.Frame(ds, bg="#EBF5FF"); de_row.pack(fill="x", padx=8, pady=2)
        FL(de_row, "Modelo elemental:", width=20, bg="#EBF5FF").pack(side="left", padx=(0,6))
        self.dep_elem_combo = SCombo(de_row, ["0 – Ninguno", "1 – Usuario"], width=14)
        self.dep_elem_combo.current(0)
        self.dep_elem_combo.pack(side="left")
        self.dep_elem_combo.bind("<<ComboboxSelected>>", lambda e: self._refresh_dep_elem())
        self._dep_elem_frame = tk.Frame(ds, bg="#EBF5FF")
        tk.Label(self._dep_elem_frame, text="Coeficientes (t h, coef /s)",
                 bg="#EBF5FF", fg=MUTED, font=FONT_SM, anchor="w").pack(fill="x", padx=8)
        self.dep_elem_table = TimeTable(self._dep_elem_frame, ["Coef (/s)"],
                                         bg="#EBF5FF", default_rows=2)
        self.dep_elem_table.pack(padx=8, pady=(0,6))

        self._refresh_dep()
        self._refresh_dep_elem()

    def _on_flag(self, key, value):
        if key == "filters":
            self._show_frame(self._filter_sec, value)
        elif key == "deposition":
            self._show_frame(self._dep_sec, value)

    def _show_frame(self, frame, show):
        if show:
            frame.pack(fill="x", pady=(4,0))
        else:
            frame.pack_forget()

    def _refresh_dep(self):
        model = self.dep_aer_combo.current()
        for f in (self._dep_user_frame, self._dep_henry_frame, self._dep_powers_frame):
            f.pack_forget()
        if   model == 1: self._dep_user_frame.pack(fill="x")
        elif model == 2: self._dep_henry_frame.pack(fill="x")
        elif model == 3: self._dep_powers_frame.pack(fill="x")

    def _refresh_dep_elem(self):
        if self.dep_elem_combo.current() == 1:
            self._dep_elem_frame.pack(fill="x")
        else:
            self._dep_elem_frame.pack_forget()

    def set_index(self, i):
        self._idx = i
        self._title_lbl.config(text=f"Compartimento {i}")

    def get_data(self) -> dict:
        return {
            "name":      self.name_var.get(),
            "comp_type": self.type_combo.current() + 1,
            "volume_m3": float(self.vol_var.get() or 0),
            "has_sprays":     self._flags["sprays"].get(),
            "has_filters":    self._flags["filters"].get(),
            "has_deposition": self._flags["deposition"].get(),
            "has_opool":      self._flags["opool"].get(),
            "detail_output":  self._flags["detail"].get(),
            "decay":          self._flags["decay"].get(),
            "filter_flow_rate": float(self.filter_flow_var.get() or 0),
            "filter_eff_table": self.filter_table.get_data(),
            "deposit_aerosol_model": self.dep_aer_combo.current(),
            "deposit_aerosol_user":  self.dep_user_table.get_data(),
            "deposit_henry":         self.dep_henry_table.get_data(),
            "deposit_powers_reactor": self.dep_powers_reactor.current() + 1,
            "deposit_powers_pctile":  float(self.dep_powers_pctile.get()),
            "deposit_elemental_model": self.dep_elem_combo.current(),
            "deposit_elemental":       self.dep_elem_table.get_data(),
        }

    def set_data(self, d: dict):
        self.name_var.set(d.get("name", self.name_var.get()))
        self.type_combo.current(int(d.get("comp_type", 3)) - 1)
        self.vol_var.set(str(d.get("volume_m3", 0.0)))
        for key, k in (("sprays", "has_sprays"), ("filters", "has_filters"), ("deposition", "has_deposition"),
                       ("opool", "has_opool"), ("detail", "detail_output"), ("decay", "decay")):
            self._flags[key].set(bool(d.get(k, False)))
        self.filter_flow_var.set(str(d.get("filter_flow_rate", 0.0)))
        for tbl, k in ((self.filter_table, "filter_eff_table"), (self.dep_user_table, "deposit_aerosol_user"),
                       (self.dep_henry_table, "deposit_henry"), (self.dep_elem_table, "deposit_elemental")):
            if d.get(k): tbl.set_data(d[k])
        self.dep_aer_combo.current(int(d.get("deposit_aerosol_model", 0)))
        self.dep_powers_reactor.current(int(d.get("deposit_powers_reactor", 1)) - 1)
        pct = str(float(d.get("deposit_powers_pctile", 50.0)))
        if pct in self.dep_powers_pctile["values"]: self.dep_powers_pctile.set(pct)
        self.dep_elem_combo.current(int(d.get("deposit_elemental_model", 0)))
        self._show_frame(self._filter_sec, self._flags["filters"].get())
        self._show_frame(self._dep_sec, self._flags["deposition"].get())
        self._refresh_dep(); self._refresh_dep_elem()


# =============================================================================
# PANEL DE PATHWAY
# =============================================================================

class PathPanel(tk.Frame):
    def __init__(self, parent, index: int, comp_names: list[str], on_delete, **kw):
        kw.setdefault("bg", CARD)
        super().__init__(parent, highlightthickness=1,
                         highlightbackground=BORDER, **kw)

        hdr = tk.Frame(self, bg=AMBER)
        hdr.pack(fill="x")
        self._title_lbl = tk.Label(hdr, text=f"Pathway {index}",
                                   bg=AMBER, fg=WHITE, font=FONT_BOLD,
                                   anchor="w", padx=10, pady=6)
        self._title_lbl.pack(side="left")
        tk.Button(hdr, text="✕ Eliminar", bg=AMBER, fg=WHITE,
                  activebackground=RED, activeforeground=WHITE,
                  relief="flat", font=FONT_SM, bd=0, padx=8,
                  cursor="hand2", command=on_delete).pack(side="right", padx=6)

        body = tk.Frame(self, bg=CARD)
        body.pack(fill="x", padx=10, pady=8)

        self.name_var = tk.StringVar(value=f"Pathway {index}")

        r1 = tk.Frame(body, bg=CARD); r1.pack(fill="x", pady=2)
        FL(r1, "Nombre:", width=18).pack(side="left", padx=(0,6))
        SE(r1, textvariable=self.name_var, width=34).pack(side="left", ipady=4)

        r2 = tk.Frame(body, bg=CARD); r2.pack(fill="x", pady=2)
        FL(r2, "Desde compartimento:", width=22).pack(side="left", padx=(0,6))
        self.from_combo = SCombo(r2, comp_names, width=22)
        if comp_names: self.from_combo.current(0)
        self.from_combo.pack(side="left")

        r3 = tk.Frame(body, bg=CARD); r3.pack(fill="x", pady=2)
        FL(r3, "Hasta compartimento:", width=22).pack(side="left", padx=(0,6))
        self.to_combo = SCombo(r3, comp_names, width=22)
        if len(comp_names) > 1: self.to_combo.current(1)
        self.to_combo.pack(side="left")

        r4 = tk.Frame(body, bg=CARD); r4.pack(fill="x", pady=2)
        FL(r4, "Mecanismo:", width=22).pack(side="left", padx=(0,6))
        self.type_combo = SCombo(r4,
            ["1 – Piping", "2 – Filter", "3 – Suppression Pool",
             "4 – Air Leakage"], width=22)
        self.type_combo.current(3)
        self.type_combo.pack(side="left")
        self.type_combo.bind("<<ComboboxSelected>>", lambda e: self._refresh_type())

        # ── Paneles condicionales ─────────────────────────────────────────────
        # Air leakage / piping → caudal de convección
        self._conv_frame = tk.Frame(body, bg=BG_WARN,
                                     highlightthickness=1,
                                     highlightbackground="#D4A017")
        tk.Label(self._conv_frame, text="Caudal normalizado (t h, flow /s)",
                 bg=BG_WARN, fg=WARN, font=FONT_SM, anchor="w").pack(fill="x", padx=8, pady=(6,2))
        self.conv_table = TimeTable(self._conv_frame, ["Flow (/s)"],
                                     bg=BG_WARN, default_rows=2)
        self.conv_table.pack(padx=8, pady=(0,8))

        # Filter pathway
        self._filter_frame = tk.Frame(body, bg=BG_WARN,
                                       highlightthickness=1,
                                       highlightbackground="#D4A017")
        tk.Label(self._filter_frame,
                 text="Filtro (t h, flow m³/s, Aerosol%, Elemental%, Orgánico%)",
                 bg=BG_WARN, fg=WARN, font=FONT_SM, anchor="w").pack(fill="x", padx=8, pady=(6,2))
        self.filter_table = TimeTable(self._filter_frame,
                                       ["Flow (m³/s)", "Aerosol %", "Elemental %", "Orgánico %"],
                                       bg=BG_WARN, default_rows=2)
        self.filter_table.pack(padx=8, pady=(0,8))

        # Suppression pool
        self._sp_frame = tk.Frame(body, bg=BG_WARN,
                                   highlightthickness=1,
                                   highlightbackground="#D4A017")
        sp = self._sp_frame
        sv_row = tk.Frame(sp, bg=BG_WARN); sv_row.pack(fill="x", padx=8, pady=(6,2))
        FL(sv_row, "Volumen inicial:", width=18, bg=BG_WARN).pack(side="left", padx=(0,6))
        self.sp_vol_var = tk.StringVar(value="0.0")
        SE(sv_row, textvariable=self.sp_vol_var, width=12).pack(side="left", ipady=4)
        tk.Label(sv_row, text="m³", bg=BG_WARN, fg=MUTED, font=FONT_SM).pack(side="left", padx=4)
        for label, attr in [
            ("Aerosol DF (t h, DF≥1)", "sp_aer_table"),
            ("Elemental DF", "sp_elem_table"),
            ("Orgánico DF", "sp_org_table"),
        ]:
            tk.Label(sp, text=label, bg=BG_WARN, fg=MUTED,
                     font=FONT_SM, anchor="w").pack(fill="x", padx=8, pady=(4,0))
            tbl = TimeTable(sp, ["DF (≥1)"], bg=BG_WARN, default_rows=2)
            tbl.pack(padx=8, pady=(0,4))
            setattr(self, attr, tbl)

        self._refresh_type()

    def _refresh_type(self):
        t = self.type_combo.current()  # 0=piping,1=filter,2=sp,3=air
        for f in (self._conv_frame, self._filter_frame, self._sp_frame):
            f.pack_forget()
        if   t == 0: self._conv_frame.pack(fill="x", pady=(4,0))    # piping simplificado
        elif t == 1: self._filter_frame.pack(fill="x", pady=(4,0))
        elif t == 2: self._sp_frame.pack(fill="x", pady=(4,0))
        elif t == 3: self._conv_frame.pack(fill="x", pady=(4,0))

    def update_comp_names(self, names):
        cur_f = self.from_combo.current()
        cur_t = self.to_combo.current()
        self.from_combo.config(values=names)
        self.to_combo.config(values=names)
        if cur_f < len(names): self.from_combo.current(cur_f)
        if cur_t < len(names): self.to_combo.current(cur_t)

    def set_index(self, i):
        self._title_lbl.config(text=f"Pathway {i}")

    def get_data(self) -> dict:
        t = self.type_combo.current() + 1
        return {
            "name":      self.name_var.get(),
            "from_comp": self.from_combo.current() + 1,
            "to_comp":   self.to_combo.current() + 1,
            "path_type": t,
            "conv_table":   self.conv_table.get_data(),
            "filter_table": self.filter_table.get_data(),
            "sp_vol":       float(self.sp_vol_var.get() or 0),
            "sp_aer":       self.sp_aer_table.get_data(),
            "sp_elem":      self.sp_elem_table.get_data(),
            "sp_org":       self.sp_org_table.get_data(),
        }

    def set_data(self, d: dict):
        self.name_var.set(d.get("name", self.name_var.get()))
        n = len(self.from_combo["values"])
        self.from_combo.current(min(max(int(d.get("from_comp", 1)) - 1, 0), n - 1))
        self.to_combo.current(min(max(int(d.get("to_comp", 2)) - 1, 0), n - 1))
        self.type_combo.current(int(d.get("path_type", 4)) - 1)
        self.sp_vol_var.set(str(d.get("sp_vol", 0.0)))
        for tbl, k in ((self.conv_table, "conv_table"), (self.filter_table, "filter_table"),
                       (self.sp_aer_table, "sp_aer"), (self.sp_elem_table, "sp_elem"), (self.sp_org_table, "sp_org")):
            if d.get(k): tbl.set_data(d[k])
        self._refresh_type()


# =============================================================================
# PANEL DE DOSE LOCATION
# =============================================================================

class DosePanel(tk.Frame):
    def __init__(self, parent, index: int, comp_names: list[str], on_delete, **kw):
        kw.setdefault("bg", CARD)
        super().__init__(parent, highlightthickness=1,
                         highlightbackground=BORDER, **kw)

        hdr = tk.Frame(self, bg=PURPLE)
        hdr.pack(fill="x")
        self._title_lbl = tk.Label(hdr, text=f"Dose Location {index}",
                                   bg=PURPLE, fg=WHITE, font=FONT_BOLD,
                                   anchor="w", padx=10, pady=6)
        self._title_lbl.pack(side="left")
        tk.Button(hdr, text="✕ Eliminar", bg=PURPLE, fg=WHITE,
                  activebackground=RED, activeforeground=WHITE,
                  relief="flat", font=FONT_SM, bd=0, padx=8,
                  cursor="hand2", command=on_delete).pack(side="right", padx=6)

        body = tk.Frame(self, bg=CARD)
        body.pack(fill="x", padx=10, pady=8)

        self.name_var = tk.StringVar(value=f"Location {index}")

        r1 = tk.Frame(body, bg=CARD); r1.pack(fill="x", pady=2)
        FL(r1, "Nombre:", width=20).pack(side="left", padx=(0,6))
        SE(r1, textvariable=self.name_var, width=30).pack(side="left", ipady=4)

        r2 = tk.Frame(body, bg=CARD); r2.pack(fill="x", pady=2)
        FL(r2, "Compartimento:", width=20).pack(side="left", padx=(0,6))
        self.comp_combo = SCombo(r2, comp_names, width=24)
        if comp_names: self.comp_combo.current(0)
        self.comp_combo.pack(side="left")

        hline(body, pady=6)

        # X/Q
        xq_row = tk.Frame(body, bg=CARD); xq_row.pack(fill="x", pady=2)
        FL(xq_row, "Modelo X/Q:", width=20).pack(side="left", padx=(0,6))
        self.xq_combo = SCombo(xq_row, ["0 – Constante 1.0", "1 – Usuario"], width=18)
        self.xq_combo.current(0)
        self.xq_combo.pack(side="left")
        self.xq_combo.bind("<<ComboboxSelected>>", lambda e: self._refresh())
        self._xq_frame = tk.Frame(body, bg=CARD)
        tk.Label(self._xq_frame, text="X/Q (tiempo h, X/Q s/m³)",
                 bg=CARD, fg=MUTED, font=FONT_SM, anchor="w").pack(fill="x")
        self.xq_table = TimeTable(self._xq_frame, ["X/Q (s/m³)"],
                                   bg=CARD, default_rows=2)
        self.xq_table.pack()

        # Breathing rate
        hline(body, pady=4)
        br_lbl = tk.Frame(body, bg=CARD); br_lbl.pack(fill="x", pady=2)
        FL(br_lbl, "Breathing rate:", width=20).pack(side="left", padx=(0,6))
        self.br_toggle = ToggleSwitch(br_lbl, initial=True, bg=CARD,
                                       callback=lambda v: self._refresh())
        self.br_toggle.pack(side="left")
        self._br_frame = tk.Frame(body, bg=CARD)
        tk.Label(self._br_frame, text="BR (tiempo h, BR m³/s)",
                 bg=CARD, fg=MUTED, font=FONT_SM, anchor="w").pack(fill="x")
        self.br_table = TimeTable(self._br_frame, ["BR (m³/s)"],
                                   bg=CARD, default_rows=2)
        self.br_table.pack()

        # Occupancy
        hline(body, pady=4)
        occ_lbl = tk.Frame(body, bg=CARD); occ_lbl.pack(fill="x", pady=2)
        FL(occ_lbl, "Occupancy (solo CR):", width=20).pack(side="left", padx=(0,6))
        self.occ_toggle = ToggleSwitch(occ_lbl, initial=False, bg=CARD,
                                        callback=lambda v: self._refresh())
        self.occ_toggle.pack(side="left")
        self._occ_frame = tk.Frame(body, bg=CARD)
        tk.Label(self._occ_frame, text="Occupancy (tiempo h, factor -)",
                 bg=CARD, fg=MUTED, font=FONT_SM, anchor="w").pack(fill="x")
        self.occ_table = TimeTable(self._occ_frame, ["Factor (-)"],
                                    bg=CARD, default_rows=2)
        self.occ_table.pack()

        self._refresh()

    def _refresh(self):
        if self.xq_combo.current() == 1:
            self._xq_frame.pack(fill="x", pady=(2,0))
        else:
            self._xq_frame.pack_forget()
        if self.br_toggle.get():
            self._br_frame.pack(fill="x", pady=(2,0))
        else:
            self._br_frame.pack_forget()
        if self.occ_toggle.get():
            self._occ_frame.pack(fill="x", pady=(2,0))
        else:
            self._occ_frame.pack_forget()

    def update_comp_names(self, names):
        cur = self.comp_combo.current()
        self.comp_combo.config(values=names)
        if cur < len(names): self.comp_combo.current(cur)

    def set_index(self, i):
        self._title_lbl.config(text=f"Dose Location {i}")

    def get_data(self) -> dict:
        return {
            "name":           self.name_var.get(),
            "comp_number":    self.comp_combo.current() + 1,
            "xq_model":       self.xq_combo.current(),
            "xq_table":       self.xq_table.get_data(),
            "has_br":         self.br_toggle.get(),
            "br_table":       self.br_table.get_data(),
            "has_occupancy":  self.occ_toggle.get(),
            "occ_table":      self.occ_table.get_data(),
        }

    def set_data(self, d: dict):
        self.name_var.set(d.get("name", self.name_var.get()))
        n = len(self.comp_combo["values"])
        self.comp_combo.current(min(max(int(d.get("comp_number", 1)) - 1, 0), n - 1))
        self.xq_combo.current(int(d.get("xq_model", 0)))
        self.br_toggle.set(bool(d.get("has_br", True)))
        self.occ_toggle.set(bool(d.get("has_occupancy", False)))
        for tbl, k in ((self.xq_table, "xq_table"), (self.br_table, "br_table"), (self.occ_table, "occ_table")):
            if d.get(k): tbl.set_data(d[k])
        self._refresh()


# =============================================================================
# PESTAÑA GLOBAL
# =============================================================================

# =============================================================================
# PREAJUSTES DEL GENERADOR PSF
# =============================================================================
# Both presets are the RADTRAD model validated with the real code (template_kpfhr.psf): the attenuated
# source term goes to a holdup volume and from there straight to the environment (KP-TR-012 takes no
# credit for the building in the transport); dose locations 1 and 2 are the outdoor receptors whose X/Q
# the chain overwrites, and 3 is the control room. Ship and land plant share the transport model: they
# differ in the names and in what the chain does around it (distances, map, zones shown).
PSF_PRESET_KEYS = {
    "Embarcación — KP-FHR a bordo (320 MWt)": "buque",
    "Planta terrestre — KP-FHR (320 MWt por unidad)": "terrestre",
    "Vacío (3 compartimentos)": "vacio",
}
_FT3, _CFM = 35.314667, 2118.88            # as RADTRAD_ENGINE (m³ → ft³, m³/s → cfm)


def psf_preset(kind: str) -> dict:
    def tt(times, **cols):
        return dict({"tiempo": list(times)}, **{k: list(v) for k, v in cols.items()})

    def filt(cfm, aer, elem):
        q = cfm / _CFM
        return tt([0.0, 720.0], **{"Flow (m³/s)": [q, q], "Aerosol %": [aer, aer], "Elemental %": [elem, elem],
                                   "Orgánico %": [0.0, 0.0]})

    if kind == "vacio":
        return {"global": {"plant_model_name": "Plant Model", "ev_active": False},
                "compartments": [{"name": "Source", "comp_type": 3, "volume_m3": 1000.0},
                                 {"name": "Environment", "comp_type": 2, "volume_m3": 0.0},
                                 {"name": "Control Room", "comp_type": 1, "volume_m3": 1000.0}],
                "pathways": [{"name": "Release to Environment", "from_comp": 1, "to_comp": 2, "path_type": 2,
                              "filter_table": filt(1.0e6, 0.0, 0.0)}],
                "dose_locations": [
                    {"name": "Exclusion Area Boundary", "comp_number": 2, "xq_model": 1,
                     "xq_table": tt([0.0, 720.0], **{"X/Q (s/m³)": [1.0e-3, 1.0e-3]})},
                    {"name": "Low Population Zone", "comp_number": 2, "xq_model": 1,
                     "xq_table": tt([0.0, 720.0], **{"X/Q (s/m³)": [1.0e-3, 1.0e-3]})}]}
    tierra = kind == "terrestre"
    xq = tt([0, 2, 4, 8, 12, 24, 96, 168, 360, 720], **{"X/Q (s/m³)": [1.0e-3] * 10})
    br = tt([0, 8, 24], **{"BR (m³/s)": [3.47e-4, 1.75e-4, 2.32e-4]})
    return {
        "global": {
            "plant_model_name": ("KP-FHR land plant - attenuated source term released directly to the environment"
                                 if tierra else
                                 "KP-FHR - attenuated source term released directly to the environment"),
            "scenario_name": "", "nif_file": "defaults\\kpfhr_terminofuente.nif",
            "inp_file": "defaults\\fgr11&12.inp", "rft_file": "defaults\\kpfhr_directo.rft",
            "plant_power_mwt": "320", "output_filename": "Test16.o0",
            "frac_aerosol": "0.95", "frac_elemental": "0.0485", "frac_organic": "0.0015",
            "calculate_daughters": False, "show_plant": True, "show_scenario": True, "show_event": True,
            "show_step": False, "show_model": False, "ev_active": True,
            "ev_table": tt([0, 8, 24, 96], **{"X/Q (-)": [3.32e-4, 1.96e-4, 7.64e-5, 2.19e-5]})},
        "compartments": [
            {"name": "Release Holdup", "comp_type": 3, "volume_m3": 3.892e5 / _FT3},
            {"name": "Environment", "comp_type": 2, "volume_m3": 0.0},
            {"name": "Reactor Building" if tierra else "Auxiliary Building", "comp_type": 3,
             "volume_m3": 1.0e6 / _FT3},
            {"name": "Control Room", "comp_type": 1, "volume_m3": 1.1e5 / _FT3, "detail_output": True}],
        "pathways": [
            {"name": "Unused (zero flow)", "from_comp": 1, "to_comp": 3, "path_type": 4,
             "conv_table": tt([0.0, 720.0], **{"Flow (/s)": [0.0, 0.0]})},
            {"name": "Direct Release to Environment", "from_comp": 1, "to_comp": 2, "path_type": 2,
             "filter_table": filt(1.0e6, 0.0, 0.0)},
            {"name": "Filter 2  Environment to CR", "from_comp": 2, "to_comp": 4, "path_type": 2,
             "filter_table": filt(5800.0, 99.0, 99.0)},
            {"name": "Unfiltered  Environment to CR", "from_comp": 2, "to_comp": 4, "path_type": 2,
             "filter_table": filt(10.0, 0.0, 0.0)},
            {"name": "Control Room Exhaust", "from_comp": 4, "to_comp": 2, "path_type": 2,
             "filter_table": filt(5810.0, 0.0, 0.0)}],
        "dose_locations": [
            {"name": "Exclusion Area Boundary", "comp_number": 2, "xq_model": 1, "xq_table": xq,
             "has_br": True, "br_table": br},
            {"name": "Low Population Zone", "comp_number": 2, "xq_model": 1, "xq_table": xq,
             "has_br": True, "br_table": br},
            {"name": "Control Room", "comp_number": 4, "xq_model": 0, "has_br": True,
             "br_table": tt([0.0, 720.0], **{"BR (m³/s)": [3.47e-4, 0.0]}), "has_occupancy": True,
             "occ_table": tt([0, 24, 96, 720], **{"Factor (-)": [1.0, 0.6, 0.4, 0.0]})}],
    }


class GlobalTab(tk.Frame):
    def __init__(self, parent, **kw):
        kw.setdefault("bg", BG)
        super().__init__(parent, **kw)

        card = SectionCard(self, "Parámetros globales del modelo", color=BLUE)
        card.pack(fill="x", padx=8, pady=8)
        b = card.body

        self._fields = {}
        defs = [
            ("plant_model_name", "Título del modelo:",        "KP-FHR - direct release to the environment", ""),
            ("scenario_name",    "Nombre escenario:",         "",                       ""),
            ("nif_file",         "Archivo NIF:",              "defaults\\kpfhr_terminofuente.nif", ""),
            ("inp_file",         "Archivo INP (DCF):",        "defaults\\fgr11&12.inp", ""),
            ("rft_file",         "Archivo RFT:",              "defaults\\kpfhr_directo.rft",  ""),
            ("plant_power_mwt",  "Potencia de planta:",       "320",                    "MWt"),
            ("output_filename",  "Archivo de salida:",        "Test16.o0",              ""),
        ]
        for key, label, default, unit in defs:
            row = tk.Frame(b, bg=CARD); row.pack(fill="x", pady=3)
            FL(row, label, width=24).pack(side="left", padx=(0,6))
            if key in ("nif_file", "inp_file", "rft_file", "output_filename"):
                var = tk.StringVar(value=default)
                SE(row, textvariable=var, width=38).pack(side="left", ipady=4, padx=(0,4))
                tk.Button(row, text="…", bg=INPUT, fg=MUTED,
                          relief="flat", font=FONT_SM, bd=0, padx=6,
                          cursor="hand2", activebackground=BLUE,
                          activeforeground=WHITE,
                          command=lambda v=var, k=key: self._browse(v, k)
                          ).pack(side="left")
            else:
                var = tk.StringVar(value=default)
                SE(row, textvariable=var, width=60 if key == "plant_model_name" else 20).pack(side="left", ipady=4)
                if unit:
                    tk.Label(row, text=unit, bg=CARD, fg=MUTED,
                             font=FONT_SM).pack(side="left", padx=(4,0))
            self._fields[key] = var

        # ── Fracciones de yodo ────────────────────────────────────────────────
        card2 = SectionCard(self, "Fracciones de yodo  (deben sumar 1.0)", color=BLUE)
        card2.pack(fill="x", padx=8, pady=(0,8))
        b2 = card2.body

        self._iodo = {}
        iodo_row = tk.Frame(b2, bg=CARD); iodo_row.pack(fill="x", pady=4)
        for key, label, default in [
            ("frac_aerosol",   "Aerosol:",   "0.95"),
            ("frac_elemental", "Elemental:", "0.0485"),
            ("frac_organic",   "Orgánico:",  "0.0015"),
        ]:
            tk.Label(iodo_row, text=label, bg=CARD, fg=MUTED,
                     font=FONT_SM).pack(side="left", padx=(0,4))
            var = tk.StringVar(value=default)
            SE(iodo_row, textvariable=var, width=10).pack(side="left", ipady=4, padx=(0,12))
            self._iodo[key] = var

        # Suma en tiempo real
        self._sum_lbl = tk.Label(b2, text="Suma: 1.0000", bg=CARD,
                                  fg=SUCCESS, font=FONT_SM)
        self._sum_lbl.pack(anchor="w", pady=(2,0))
        for v in self._iodo.values():
            v.trace_add("write", lambda *_: self._update_sum())
        self._update_sum()

        # ── Opciones de escenario ─────────────────────────────────────────────
        card3 = SectionCard(self, "Opciones de escenario", color=BLUE)
        card3.pack(fill="x", padx=8, pady=(0,8))
        b3 = card3.body

        opts_row = tk.Frame(b3, bg=CARD); opts_row.pack(fill="x")
        self._opts = {}
        for key, label, init in [
            ("calculate_daughters", "Decay / daughters", False),
            ("show_plant",          "Show plant",        True),
            ("show_scenario",       "Show scenario",     True),
            ("show_event",          "Show events",       True),
            ("show_step",           "Show steps",        False),
            ("show_model",          "Show model",        False),
        ]:
            col = tk.Frame(opts_row, bg=CARD)
            col.pack(side="left", padx=(0,20))
            tk.Label(col, text=label, bg=CARD, fg=MUTED,
                     font=FONT_SM).pack(anchor="w")
            t = ToggleSwitch(col, initial=init, bg=CARD)
            t.pack(anchor="w", pady=2)
            self._opts[key] = t

        # ── Effective Volume X/Q ──────────────────────────────────────────────
        card4 = SectionCard(self, "Effective Volume X/Q  (sala de control)", color=BLUE)
        card4.pack(fill="x", padx=8, pady=(0,8))
        b4 = card4.body

        ev_row = tk.Frame(b4, bg=CARD); ev_row.pack(fill="x", pady=2)
        FL(ev_row, "Activar:", width=10).pack(side="left", padx=(0,6))
        self.ev_toggle = ToggleSwitch(ev_row, initial=True, bg=CARD,
                                       callback=lambda v: self._refresh_ev())
        self.ev_toggle.pack(side="left")
        self._ev_frame = tk.Frame(b4, bg=CARD)
        tk.Label(self._ev_frame, text="X/Q efectivo (tiempo h, X/Q -)",
                 bg=CARD, fg=MUTED, font=FONT_SM, anchor="w").pack(fill="x")
        self.ev_table = TimeTable(self._ev_frame, ["X/Q (-)"],
                                   bg=CARD, default_rows=2)
        self.ev_table.pack()
        self._refresh_ev()

    def _browse(self, var, key):
        if key == "output_filename":
            p = filedialog.asksaveasfilename(
                defaultextension=".psf",
                filetypes=[("PSF", "*.psf"), ("All", "*.*")])
        else:
            p = filedialog.askopenfilename(
                filetypes=[("All", "*.*")])
        if p:
            var.set(p)

    def _update_sum(self):
        try:
            s = sum(float(v.get()) for v in self._iodo.values())
            ok = abs(s - 1.0) < 1e-4
            self._sum_lbl.config(
                text=f"Suma: {s:.4f}",
                fg=SUCCESS if ok else RED)
        except ValueError:
            self._sum_lbl.config(text="Suma: error", fg=RED)

    def _refresh_ev(self):
        if self.ev_toggle.get():
            self._ev_frame.pack(fill="x", pady=(4,0))
        else:
            self._ev_frame.pack_forget()

    def get_data(self) -> dict:
        d = {k: v.get() for k, v in self._fields.items()}
        d.update({k: v.get() for k, v in self._iodo.items()})
        d.update({k: v.get() for k, v in self._opts.items()})
        d["ev_active"] = self.ev_toggle.get()
        d["ev_table"]  = self.ev_table.get_data()
        return d

    def set_data(self, d: dict):
        for k, v in self._fields.items():
            if k in d: v.set(str(d[k]))
        for k, v in self._iodo.items():
            if k in d: v.set(str(d[k]))
        for k, t in self._opts.items():
            if k in d: t.set(bool(d[k]))
        self.ev_toggle.set(bool(d.get("ev_active", False)))
        if d.get("ev_table"): self.ev_table.set_data(d["ev_table"])
        self._refresh_ev()


# =============================================================================
# VENTANA PRINCIPAL
# =============================================================================

class PSFApp(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self._comp_panels = []
        self._path_panels = []
        self._dose_panels = []
        self._build_notebook()

    # ── Titlebar ──────────────────────────────────────────────────────────────

    def _build_titlebar(self):
        bar = tk.Frame(self, bg=CARD, height=54)
        bar.pack(fill="x"); bar.pack_propagate(False)

        tk.Label(bar, text="⚙", bg=CARD, fg=BLUE,
                 font=("Segoe UI", 22)).pack(side="left", padx=(14,6))
        tf = tk.Frame(bar, bg=CARD); tf.pack(side="left")
        tk.Label(tf, text="PSF Generator", bg=CARD, fg=TEXT,
                 font=("Segoe UI Semibold", 13)).pack(anchor="w")
        tk.Label(tf, text="RADTRAD 3.03 — Generador de archivos PSF",
                 bg=CARD, fg=MUTED, font=("Segoe UI", 8)).pack(anchor="w")

        for text, cmd, color in [
            ("▶  Generar PSF",    self._generate,     BLUE),
            ("💾  Guardar config", self._save_config,  INPUT),
            ("📂  Cargar config",  self._load_config,  INPUT),
        ]:
            fg_ = WHITE if color == BLUE else MUTED
            tk.Button(bar, text=text, bg=color, fg=fg_,
                      activebackground="#2563EB" if color==BLUE else BORDER,
                      activeforeground=WHITE if color==BLUE else TEXT,
                      relief="flat", font=FONT_SM if color!=BLUE else FONT_BOLD,
                      bd=0, padx=14, pady=8, cursor="hand2",
                      command=cmd).pack(side="right", padx=4, pady=8)
        tk.Button(bar, text="?  Ayuda", bg=INPUT, fg=BLUE,
                  activebackground=BLUE, activeforeground=WHITE,
                  relief="flat", font=("Segoe UI Semibold", 9), bd=0,
                  padx=10, pady=8, cursor="hand2",
                  command=lambda: ReadmeWindow(self)).pack(side="right", padx=4, pady=8)

    # ── Notebook ──────────────────────────────────────────────────────────────

    def _build_notebook(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook",        background=BG, borderwidth=0)
        style.configure("TNotebook.Tab",    background=INPUT, foreground=MUTED,
                        padding=[14, 6], font=FONT_SM)
        style.map("TNotebook.Tab",
                  background=[("selected", CARD)],
                  foreground=[("selected", TEXT)])

        # ── Barra: preajustes, configuración y enlace con la pestaña de cálculo ──
        bar = tk.Frame(self, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
        bar.pack(fill="x", padx=8, pady=(8, 4))
        tk.Label(bar, text="Preajuste:", bg=CARD, fg=MUTED, font=FONT_SM).pack(side="left", padx=(10, 4), pady=8)
        self._preset_var = tk.StringVar(value=list(PSF_PRESET_KEYS)[0])
        SCombo(bar, list(PSF_PRESET_KEYS), width=34, textvariable=self._preset_var).pack(side="left")
        def _b(text, cmd, color=INPUT, fg=TEXT):
            return tk.Button(bar, text=text, bg=color, fg=fg, relief="flat", font=FONT_SM, bd=0, padx=10, pady=5,
                             cursor="hand2", activebackground=BLUE, activeforeground=WHITE, command=cmd)
        _b("Cargar preajuste", self._load_preset).pack(side="left", padx=(6, 0))
        _b("Usar en el cálculo  →", self._use_in_pipeline, GREEN, WHITE).pack(side="right", padx=(4, 10))
        _b("Guardar PSF…", self._save_psf_from_preview, BLUE, WHITE).pack(side="right", padx=4)
        _b("Cargar config", self._load_config).pack(side="right", padx=4)
        _b("Guardar config", self._save_config).pack(side="right", padx=4)
        tk.Label(self, text="Alcance: compartimentos (filtros de recirculación y deposición natural), caminos de tipo "
                            "Filter, Air Leakage y Suppression Pool, y dose locations. No escribe sprays, «overlying "
                            "pool» ni las tablas de Piping. Volúmenes en m³ y caudales en m³/s (el fichero va en "
                            "ft³ y cfm).", bg=BG, fg=MUTED, font=FONT_SM, anchor="w", justify="left",
                 wraplength=1050).pack(fill="x", padx=12, pady=(0, 4))

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=0, pady=0)

        # ── Tab Global ────────────────────────────────────────────────────────
        self.global_tab = GlobalTab(nb)
        nb.add(self.global_tab, text="  Global  ")

        # ── Tab Compartimentos ────────────────────────────────────────────────
        self._comp_tab_frame = self._make_list_tab(
            nb, "  Compartimentos  ", GREEN,
            "Compartimento", self._add_comp)

        # ── Tab Pathways ──────────────────────────────────────────────────────
        self._path_tab_frame = self._make_list_tab(
            nb, "  Pathways  ", AMBER,
            "Pathway", self._add_path)

        # ── Tab Dose Locations ────────────────────────────────────────────────
        self._dose_tab_frame = self._make_list_tab(
            nb, "  Dose Locations  ", PURPLE,
            "Dose Location", self._add_dose)

        # ── Tab Vista previa ──────────────────────────────────────────────────
        preview_tab = tk.Frame(nb, bg=BG)
        nb.add(preview_tab, text="  Vista previa  ")

        # Barra de botones
        preview_bar = tk.Frame(preview_tab, bg=BG)
        preview_bar.pack(fill="x", padx=8, pady=6)
        tk.Button(preview_bar, text="↺  Actualizar", bg=INPUT, fg=TEXT,
                  relief="flat", font=FONT_SM, bd=0, padx=10, pady=4,
                  cursor="hand2", activebackground=BLUE, activeforeground=WHITE,
                  command=self._refresh_preview).pack(side="left", padx=(0, 6))
        tk.Button(preview_bar, text="⬇  Guardar PSF", bg=GREEN, fg=WHITE,
                  relief="flat", font=FONT_SM, bd=0, padx=10, pady=4,
                  cursor="hand2", activebackground="#145C2E", activeforeground=WHITE,
                  command=self._save_psf_from_preview).pack(side="left", padx=(0, 6))
        tk.Button(preview_bar, text="🖼  Exportar diagrama", bg=PURPLE, fg=WHITE,
                  relief="flat", font=FONT_SM, bd=0, padx=10, pady=4,
                  cursor="hand2", activebackground="#4A2980", activeforeground=WHITE,
                  command=self._export_diagram).pack(side="left")

        # PanedWindow vertical: diagrama arriba, texto abajo
        paned = tk.PanedWindow(preview_tab, orient="vertical", bg=BG,
                               sashwidth=5, sashrelief="flat")
        paned.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        # Panel superior: diagrama de planta (Canvas tkinter)
        diagram_frame = tk.Frame(paned, bg=CARD,
                                 highlightthickness=1,
                                 highlightbackground=BORDER)
        paned.add(diagram_frame, minsize=280, height=320)
        self._diagram_canvas = tk.Canvas(diagram_frame, bg=CARD,
                                          highlightthickness=0)
        self._diagram_canvas.pack(fill="both", expand=True)
        self._diagram_canvas.bind("<Configure>", lambda e: self._draw_diagram())

        # Panel inferior: texto PSF
        text_frame = tk.Frame(paned, bg=CARD)
        paned.add(text_frame, minsize=120)
        self._preview_text = scrolledtext.ScrolledText(
            text_frame, bg="#FAFBFC", fg=TEXT, font=FONT_MONO,
            relief="flat", bd=0, wrap="none")
        self._preview_text.pack(fill="both", expand=True)

        # Contenido inicial: el modelo KP-FHR validado (el mismo que template_kpfhr.psf)
        try:
            self._apply_config(psf_preset("buque"))
        except Exception:
            self._add_comp(); self._add_comp(); self._add_comp(); self._add_path(); self._add_dose()

    def _make_list_tab(self, nb, tab_name, color, item_name, add_cmd):
        outer = tk.Frame(nb, bg=BG)
        nb.add(outer, text=tab_name)

        # Barra de acciones
        bar = tk.Frame(outer, bg=BG)
        bar.pack(fill="x", padx=8, pady=6)
        tk.Button(bar, text=f"+  Añadir {item_name}",
                  bg=color, fg=WHITE,
                  activebackground=BLUE, activeforeground=WHITE,
                  relief="flat", font=FONT_SM, bd=0, padx=12, pady=5,
                  cursor="hand2", command=add_cmd).pack(side="left")

        # Canvas + scrollbar
        canvas = tk.Canvas(outer, bg=BG, highlightthickness=0)
        vsb = tk.Scrollbar(outer, orient="vertical", command=canvas.yview,
                           bg=INPUT, troughcolor=BG, activebackground=BORDER)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        sf = tk.Frame(canvas, bg=BG)
        cw = canvas.create_window((0, 0), window=sf, anchor="nw")

        def _resize(e=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(cw, width=canvas.winfo_width())
        sf.bind("<Configure>", _resize)
        canvas.bind("<Configure>", _resize)
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        return sf

    # ── Añadir / eliminar elementos ───────────────────────────────────────────

    def _add_comp(self):
        idx = len(self._comp_panels) + 1
        holder = []
        p = CompPanel(self._comp_tab_frame, idx, on_delete=lambda: self._del_comp(holder[0]))
        holder.append(p)
        p.pack(fill="x", padx=8, pady=6)
        self._comp_panels.append(p)
        # the pathway and dose location lists show the compartment names: keep them in step
        p.name_var.trace_add("write", lambda *_: (self._update_path_comp_names(),
                                                   self._update_dose_comp_names()))
        self._update_path_comp_names()
        self._update_dose_comp_names()
        return p

    def _del_comp(self, panel):
        # the panel itself is passed: an index fixed when it was created went stale after a deletion
        if len(self._comp_panels) <= 1:
            messagebox.showwarning("Mínimo", "Debe haber al menos 1 compartimento.")
            return
        n = self._comp_panels.index(panel) + 1
        usados = [f"pathway {i}" for i, q in enumerate(self._path_panels, 1)
                  if n in (q.from_combo.current() + 1, q.to_combo.current() + 1)]
        usados += [f"dose location {i}" for i, q in enumerate(self._dose_panels, 1)
                   if q.comp_combo.current() + 1 == n]
        if usados and not messagebox.askyesno(
                "Compartimento en uso", f"El compartimento {n} se usa en: {', '.join(usados)}.\n"
                "Si lo eliminas, esos elementos apuntarán a otro compartimento y habrá que revisarlos.\n\n"
                "¿Eliminarlo?"):
            return
        self._comp_panels.remove(panel)
        panel.destroy()
        for i, p in enumerate(self._comp_panels, 1):
            p.set_index(i)
        self._update_path_comp_names()
        self._update_dose_comp_names()

    def _add_path(self):
        idx    = len(self._path_panels) + 1
        names  = self._comp_names()
        holder = []
        p = PathPanel(self._path_tab_frame, idx, names, on_delete=lambda: self._del_path(holder[0]))
        holder.append(p)
        p.pack(fill="x", padx=8, pady=6)
        self._path_panels.append(p)
        return p

    def _del_path(self, panel):
        if len(self._path_panels) <= 1:
            messagebox.showwarning("Mínimo", "Debe haber al menos 1 pathway.")
            return
        self._path_panels.remove(panel); panel.destroy()
        for i, p in enumerate(self._path_panels, 1):
            p.set_index(i)

    def _add_dose(self):
        idx   = len(self._dose_panels) + 1
        names = self._comp_names()
        holder = []
        p = DosePanel(self._dose_tab_frame, idx, names, on_delete=lambda: self._del_dose(holder[0]))
        holder.append(p)
        p.pack(fill="x", padx=8, pady=6)
        self._dose_panels.append(p)
        return p

    def _del_dose(self, panel):
        if len(self._dose_panels) <= 1:
            messagebox.showwarning("Mínimo", "Debe haber al menos 1 dose location.")
            return
        self._dose_panels.remove(panel); panel.destroy()
        for i, p in enumerate(self._dose_panels, 1):
            p.set_index(i)

    def _comp_names(self) -> list[str]:
        names = []
        for i, p in enumerate(self._comp_panels, 1):
            try:
                n = p.name_var.get() or f"Comp {i}"
            except Exception:
                n = f"Comp {i}"
            names.append(f"{i} – {n}")
        return names or ["1 – Compartment 1"]

    def _update_path_comp_names(self):
        names = self._comp_names()
        for p in self._path_panels:
            p.update_comp_names(names)

    def _update_dose_comp_names(self):
        names = self._comp_names()
        for p in self._dose_panels:
            p.update_comp_names(names)

    # ── Construir PSFModel desde la GUI ───────────────────────────────────────

    def _build_model(self):
        gd = self.global_tab.get_data()

        model = PSFModel(
            title            = gd.get("title", ""),
            plant_model_name = gd["plant_model_name"],
            scenario_name    = gd["scenario_name"],
            nif_file         = gd["nif_file"],
            inp_file         = gd["inp_file"],
            rft_file         = gd["rft_file"],
            plant_power_mwt  = float(gd["plant_power_mwt"] or 0),
            output_filename  = gd["output_filename"],
            frac_aerosol     = float(gd["frac_aerosol"] or 0),
            frac_elemental   = float(gd["frac_elemental"] or 0),
            frac_organic     = float(gd["frac_organic"] or 0),
            calculate_daughters = gd["calculate_daughters"],
            show_plant       = gd["show_plant"],
            show_scenario    = gd["show_scenario"],
            show_event       = gd["show_event"],
            show_step        = gd["show_step"],
            show_model       = gd["show_model"],
        )

        # Effective Volume
        if gd["ev_active"]:
            ev = gd["ev_table"]
            model.eff_vol_xq_table = TimeValueTable(
                times=ev["tiempo"], values=ev["X/Q (-)"])

        # Compartimentos
        for cd in [p.get_data() for p in self._comp_panels]:
            dep_aer = cd["deposit_aerosol_model"]
            dep_h   = cd["deposit_henry"]
            dep_u   = cd["deposit_aerosol_user"]
            dep_e   = cd["deposit_elemental"]

            henry_tbl = None
            if dep_aer == DEPOSIT_AEROSOL_HENRY:
                henry_tbl = TimeValue3Table(
                    times=dep_h["tiempo"],
                    v1=dep_h["Altura (m)"],
                    v2=dep_h["Densidad (g/cc)"],
                    v3=[0.0] * len(dep_h["tiempo"]),
                )
            user_tbl = None
            if dep_aer == DEPOSIT_AEROSOL_USER:
                user_tbl = TimeValueTable(
                    times=dep_u["tiempo"], values=dep_u["Coef (/s)"])

            elem_tbl = None
            if cd["deposit_elemental_model"] == 1:
                elem_tbl = TimeValueTable(
                    times=dep_e["tiempo"], values=dep_e["Coef (/s)"])

            fe = cd["filter_eff_table"]
            filter_tbl = None
            if cd["has_filters"]:
                filter_tbl = TimeValue3Table(
                    times=fe["tiempo"],
                    v1=fe["Aerosol %"],
                    v2=fe["Elemental %"],
                    v3=fe["Orgánico %"],
                )

            model.add_compartment(Compartment(
                name       = cd["name"],
                comp_type  = cd["comp_type"],
                volume_m3  = cd["volume_m3"],
                has_sprays     = cd["has_sprays"],
                has_filters    = cd["has_filters"],
                has_deposition = cd["has_deposition"],
                has_opool      = cd["has_opool"],
                detail_output  = cd["detail_output"],
                decay          = cd["decay"],
                filter_flow_rate       = cd["filter_flow_rate"],
                filter_eff_table       = filter_tbl,
                deposit_aerosol_model  = dep_aer,
                deposit_aerosol_table  = user_tbl,
                deposit_henry_table    = henry_tbl,
                deposit_powers_reactor = cd["deposit_powers_reactor"],
                deposit_powers_pctile  = cd["deposit_powers_pctile"],
                deposit_elemental_model= cd["deposit_elemental_model"],
                deposit_elemental_table= elem_tbl,
            ))

        # Pathways
        for pd_ in [p.get_data() for p in self._path_panels]:
            t = pd_["path_type"]
            conv = pd_["conv_table"]
            flt  = pd_["filter_table"]
            sp_a = pd_["sp_aer"]
            sp_e = pd_["sp_elem"]
            sp_o = pd_["sp_org"]

            conv_tbl = TimeValueTable(
                times=conv["tiempo"], values=conv["Flow (/s)"])

            flt_tbl = FilterTable(
                times=flt["tiempo"],
                flow =flt["Flow (m³/s)"],
                aer  =flt["Aerosol %"],
                elem =flt["Elemental %"],
                org  =flt["Orgánico %"],
            ) if t == PATH_TYPE_FILTER else None

            sp_aer_tbl  = TimeValueTable(times=sp_a["tiempo"], values=sp_a["DF (≥1)"]) if t == PATH_TYPE_SUPPRESSION_POOL else None
            sp_elem_tbl = TimeValueTable(times=sp_e["tiempo"], values=sp_e["DF (≥1)"]) if t == PATH_TYPE_SUPPRESSION_POOL else None
            sp_org_tbl  = TimeValueTable(times=sp_o["tiempo"], values=sp_o["DF (≥1)"]) if t == PATH_TYPE_SUPPRESSION_POOL else None

            model.add_pathway(Pathway(
                name      = pd_["name"],
                from_comp = pd_["from_comp"],
                to_comp   = pd_["to_comp"],
                path_type = t,
                convection_table  = conv_tbl if t in (PATH_TYPE_AIR_LEAKAGE, PATH_TYPE_PIPING) else None,
                filter_table      = flt_tbl,
                sp_initial_volume = pd_["sp_vol"],
                sp_aerosol_table  = sp_aer_tbl,
                sp_elemental_table= sp_elem_tbl,
                sp_organic_table  = sp_org_tbl,
            ))

        # Dose Locations
        for dd in [p.get_data() for p in self._dose_panels]:
            xq_tbl = None
            if dd["xq_model"] == 1:
                xq = dd["xq_table"]
                xq_tbl = TimeValueTable(times=xq["tiempo"], values=xq["X/Q (s/m³)"])
            br_tbl = None
            if dd["has_br"]:
                br = dd["br_table"]
                br_tbl = TimeValueTable(times=br["tiempo"], values=br["BR (m³/s)"])
            occ_tbl = None
            if dd["has_occupancy"]:
                oc = dd["occ_table"]
                occ_tbl = TimeValueTable(times=oc["tiempo"], values=oc["Factor (-)"])

            model.add_dose_location(DoseLocation(
                name               = dd["name"],
                compartment_number = dd["comp_number"],
                xq_model           = dd["xq_model"],
                xq_table           = xq_tbl,
                br_table           = br_tbl,
                has_occupancy      = dd["has_occupancy"],
                occupancy_table    = occ_tbl,
            ))

        return model

    # ── Generar ───────────────────────────────────────────────────────────────

    def _generate(self):
        if not GENERATOR_OK:
            messagebox.showerror("Error", "PSF_GENERATOR.py no está disponible.")
            return
        try:
            model = self._build_model()
        except Exception as e:
            messagebox.showerror("Error construyendo modelo", str(e))
            return

        errors = model.validate()
        if errors:
            messagebox.showerror("Errores de validación",
                                 "\n".join(f"• {e}" for e in errors))
            return

        out = self.global_tab._fields["output_filename"].get()
        if not out.endswith(".psf"):
            out = Path(out).with_suffix(".psf")

        path = filedialog.asksaveasfilename(
            defaultextension=".psf",
            filetypes=[("PSF files", "*.psf"), ("All", "*.*")],
            initialfile=str(out))
        if not path:
            return

        try:
            model.write(path)
            messagebox.showinfo("PSF generado",
                                f"Archivo generado correctamente:\n{path}")
        except Exception as e:
            messagebox.showerror("Error al escribir PSF", str(e))

    # ── Vista previa ──────────────────────────────────────────────────────────

    def _refresh_preview(self):
        if not GENERATOR_OK:
            return
        try:
            model = self._build_model()
            content = model.to_string()
        except Exception as e:
            content = f"[ERROR]\n{e}"
            model   = None
        self._preview_text.config(state="normal")
        self._preview_text.delete("1.0", "end")
        self._preview_text.insert("1.0", content)
        self._preview_text.config(state="disabled")
        self._draw_diagram()

    def _draw_diagram(self):
        """Dibuja el esquema de planta en el canvas a partir de los paneles actuales."""
        c = self._diagram_canvas
        c.delete("all")
        W = c.winfo_width()  or 700
        H = c.winfo_height() or 320
        if W < 100: W = 700

        # ── Colores del diagrama ──────────────────────────────────────────────
        COL = {"1": "#D6EAF8", "2": "#D5F5E3", "3": "#FEF9E7", "?": "#F2F3F4"}
        BDR = {"1": "#2E86C1", "2": "#1E8449", "3": "#B7950B", "?": "#7F8C8D"}
        TXT = "#1F2328"
        ARR = "#5D6D7E"
        DOT = "#884EA0"

        # ── Recoger datos de los paneles ──────────────────────────────────────
        comps = [p.get_data() for p in self._comp_panels]
        paths = [p.get_data() for p in self._path_panels]
        doses = [p.get_data() for p in self._dose_panels]

        n = len(comps)
        if n == 0:
            c.create_text(W//2, H//2, text="Sin compartimentos definidos",
                          fill="#AAAAAA", font=("Segoe UI", 11))
            return

        # ── Layout automático: compartimentos en fila ─────────────────────────
        MARGIN  = 40
        BOX_H   = 64
        BOX_W   = max(110, min(160, (W - 2*MARGIN - (n-1)*30) // n))
        gap     = (W - 2*MARGIN - n*BOX_W) // max(n-1, 1) if n > 1 else 0
        y_comp  = H // 2 - BOX_H // 2

        box_cx = []  # centro X de cada compartimento
        box_cy = y_comp + BOX_H // 2

        comp_rects = {}
        for i, cd in enumerate(comps):
            x0 = MARGIN + i * (BOX_W + gap)
            x1 = x0 + BOX_W
            y0 = y_comp
            y1 = y_comp + BOX_H
            cx = (x0 + x1) // 2
            box_cx.append(cx)

            ctype = str(cd.get("comp_type", 3))
            fill  = COL.get(ctype, COL["?"])
            bdr   = BDR.get(ctype, BDR["?"])

            # Rectángulo
            c.create_rectangle(x0, y0, x1, y1,
                                fill=fill, outline=bdr, width=1.5)

            # Nombre (truncar si hace falta)
            name  = cd.get("name", f"Comp {i+1}")
            label = name if len(name) <= 16 else name[:14] + "…"
            c.create_text(cx, y0 + 20, text=label,
                          font=("Segoe UI Semibold", 9), fill=TXT, anchor="center")
            c.create_text(cx, y0 + 36, text=f"C{i+1}",
                          font=("Segoe UI", 8), fill=bdr, anchor="center")

            # Flags de features
            feats = []
            if cd.get("has_filters"):     feats.append("F")
            if cd.get("has_deposition"):  feats.append("D")
            if cd.get("has_sprays"):      feats.append("S")
            if cd.get("has_opool"):       feats.append("O")
            if feats:
                c.create_text(cx, y0 + 52,
                              text=" ".join(feats),
                              font=("Consolas", 7), fill=bdr, anchor="center")

            comp_rects[i+1] = (x0, y0, x1, y1, cx, box_cy)

        # ── Pathways ─────────────────────────────────────────────────────────
        PATH_COLORS = {1: "#884EA0", 2: "#E67E22", 3: "#1ABC9C", 4: "#2E86C1"}
        PATH_NAMES  = {1: "Pip", 2: "Fil", 3: "SP", 4: "Air"}

        for pi, pd in enumerate(paths):
            fc = pd.get("from_comp", 1)
            tc = pd.get("to_comp",   1)
            pt = pd.get("path_type", 4)
            col = PATH_COLORS.get(pt, ARR)

            if fc not in comp_rects or tc not in comp_rects:
                continue

            x0f, y0f, x1f, y1f, cxf, cyf = comp_rects[fc]
            x0t, y0t, x1t, y1t, cxt, cyt = comp_rects[tc]

            # Offset vertical para evitar solapamiento entre flechas paralelas
            off = (pi % 3 - 1) * 14

            if fc == tc:
                # Flecha reflexiva (recirculación)
                rx, ry = cxf + BOX_W//2 - 10, y0f - 10
                c.create_arc(rx-18, ry-18, rx+18, ry+18,
                             start=0, extent=300,
                             style="arc", outline=col, width=1.5)
                c.create_text(rx, ry - 22, text=f"P{pi+1}",
                              font=("Segoe UI", 7), fill=col)
            else:
                # Flecha entre dos compartimentos
                if cxf < cxt:
                    ax1, ax2 = x1f, x0t
                else:
                    ax1, ax2 = x0f, x1t
                ay = y_comp + BOX_H//2 + off

                c.create_line(ax1, ay, ax2, ay,
                              fill=col, width=1.5, arrow="last",
                              arrowshape=(8, 10, 4))
                mx = (ax1 + ax2) // 2
                c.create_text(mx, ay - 9,
                              text=f"P{pi+1} {PATH_NAMES.get(pt,'')}",
                              font=("Segoe UI", 7), fill=col)

        # ── Dose locations ────────────────────────────────────────────────────
        DL_Y = H - 44
        for di, dd in enumerate(doses):
            name = dd.get("name", f"DL{di+1}")
            comp_n = dd.get("comp_number", 1)
            label = name if len(name) <= 18 else name[:16] + "…"

            # Triángulo (offsite) o círculo (sala control) o cuadrado
            dx = MARGIN + di * 160
            if dx + 120 > W: break

            c.create_oval(dx, DL_Y - 14, dx + 28, DL_Y + 14,
                          fill=DOT, outline="#5B2C6F", width=1)
            c.create_text(dx + 14, DL_Y, text=f"DL{di+1}",
                          font=("Segoe UI", 7), fill="white")
            c.create_text(dx + 36, DL_Y - 6,
                          text=label,
                          font=("Segoe UI", 8), fill=TXT, anchor="w")
            c.create_text(dx + 36, DL_Y + 7,
                          text=f"→ C{comp_n}",
                          font=("Segoe UI", 7), fill=DOT, anchor="w")

        # ── Leyenda de tipos ──────────────────────────────────────────────────
        leg_x = W - 160
        leg_y = 10
        type_labels = [("C1=CR", "#2E86C1"), ("C2=Env", "#1E8449"),
                       ("C3=Other", "#B7950B")]
        for j, (lbl, col) in enumerate(type_labels):
            c.create_rectangle(leg_x, leg_y + j*16,
                                leg_x + 10, leg_y + j*16 + 10,
                                fill=list(COL.values())[j],
                                outline=col, width=1)
            c.create_text(leg_x + 14, leg_y + j*16 + 5,
                          text=lbl, font=("Segoe UI", 8),
                          fill=col, anchor="w")

        path_leg = [(1,"Piping","#884EA0"),(2,"Filter","#E67E22"),
                    (3,"Sup.Pool","#1ABC9C"),(4,"Air Leak","#2E86C1")]
        pl_x = W - 160
        pl_y = leg_y + 60
        for j, (_, lbl, col) in enumerate(path_leg):
            c.create_line(pl_x, pl_y + j*14 + 5,
                          pl_x + 14, pl_y + j*14 + 5,
                          fill=col, width=2, arrow="last", arrowshape=(6,8,3))
            c.create_text(pl_x + 18, pl_y + j*14 + 5,
                          text=lbl, font=("Segoe UI", 8),
                          fill=col, anchor="w")

    def _save_psf_from_preview(self):
        """Genera y guarda el PSF directamente desde la vista previa."""
        if not GENERATOR_OK:
            messagebox.showerror("Error", "RADTRAD_ENGINE no disponible.")
            return
        try:
            model = self._build_model()
        except Exception as e:
            messagebox.showerror("Error al construir modelo", str(e))
            return
        errors = model.validate()
        if errors:
            messagebox.showerror("Errores de validación",
                                 "\n".join(f"• {e}" for e in errors))
            return
        default_name = self.global_tab._fields["output_filename"].get()
        if not default_name.endswith(".psf"):
            default_name = Path(default_name).stem + ".psf"
        path = filedialog.asksaveasfilename(
            defaultextension=".psf",
            filetypes=[("PSF files", "*.psf"), ("All", "*.*")],
            initialfile=default_name)
        if not path:
            return
        try:
            model.write(path)
            messagebox.showinfo("PSF guardado",
                                f"Archivo guardado correctamente:\n{path}")
        except Exception as e:
            messagebox.showerror("Error al guardar PSF", str(e))

    def _export_diagram(self):
        """Exporta el diagrama del canvas a PNG o EPS."""
        c = self._diagram_canvas
        if c.winfo_width() < 10:
            messagebox.showwarning("Diagrama vacío",
                                   "Pulsa Actualizar primero para generar el diagrama.")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("EPS (vectorial)", "*.eps"),
                       ("All", "*.*")],
            initialfile="esquema_planta.png")
        if not path:
            return

        ext = Path(path).suffix.lower()

        if ext == ".eps":
            # EPS nativo de tkinter — sin dependencias externas
            try:
                c.postscript(file=path, colormode="color")
                messagebox.showinfo("Diagrama exportado",
                                    f"EPS guardado:\n{path}")
            except Exception as e:
                messagebox.showerror("Error al exportar EPS", str(e))

        else:
            # PNG — requiere Pillow
            try:
                from PIL import ImageGrab, Image
                # Obtener coordenadas absolutas del canvas en pantalla
                x = c.winfo_rootx()
                y = c.winfo_rooty()
                w = c.winfo_width()
                h = c.winfo_height()
                img = ImageGrab.grab(bbox=(x, y, x + w, y + h))
                img.save(path)
                messagebox.showinfo("Diagrama exportado",
                                    f"PNG guardado:\n{path}")
            except ImportError:
                # Pillow no disponible — guardar como EPS en su lugar
                eps_path = Path(path).with_suffix(".eps")
                try:
                    c.postscript(file=str(eps_path), colormode="color")
                    messagebox.showwarning(
                        "Pillow no instalado",
                        f"Para exportar PNG instala Pillow:\n"
                        f"  pip install Pillow\n\n"
                        f"Se ha guardado como EPS vectorial en su lugar:\n"
                        f"{eps_path}")
                except Exception as e:
                    messagebox.showerror("Error al exportar", str(e))
            except Exception as e:
                messagebox.showerror("Error al exportar PNG", str(e))

    # ── Guardar / cargar config ───────────────────────────────────────────────

    def _save_config(self):
        try:
            gd = self.global_tab.get_data()
            comps = [p.get_data() for p in self._comp_panels]
            paths = [p.get_data() for p in self._path_panels]
            doses = [p.get_data() for p in self._dose_panels]
            data  = {"global": gd, "compartments": comps,
                     "pathways": paths, "dose_locations": doses}
        except Exception as e:
            messagebox.showerror("Error", str(e)); return

        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json"), ("All", "*.*")],
            initialfile="psf_config.json")
        if path:
            Path(path).write_text(
                json.dumps(data, indent=2, default=str), encoding="utf-8")
            messagebox.showinfo("Guardado", f"Configuración guardada:\n{path}")

    def _load_config(self):
        path = filedialog.askopenfilename(
            filetypes=[("JSON", "*.json"), ("All", "*.*")])
        if not path:
            return
        try:
            self._apply_config(json.loads(Path(path).read_text(encoding="utf-8")))
        except Exception as e:
            messagebox.showerror("Error al cargar", f"{path}\n{e}")

    def _apply_config(self, data: dict):
        """Fill every tab from a configuration (the dict written by «Guardar config» or a preset)."""
        for lst in (self._dose_panels, self._path_panels, self._comp_panels):
            for p in lst: p.destroy()
            lst.clear()
        self.global_tab.set_data(data.get("global", {}))
        for cd in data.get("compartments", []) or [{}]:
            self._add_comp().set_data(cd)
        self._update_path_comp_names(); self._update_dose_comp_names()
        for pd_ in data.get("pathways", []) or [{}]:
            self._add_path().set_data(pd_)
        for dd in data.get("dose_locations", []) or [{}]:
            self._add_dose().set_data(dd)
        self._refresh_preview()

    def _load_preset(self):
        key = PSF_PRESET_KEYS.get(self._preset_var.get())
        if key is None:
            return
        if not messagebox.askyesno("Preajuste", "Se sustituirá todo el contenido del generador por el preajuste "
                                               f"«{self._preset_var.get()}».\n\n¿Continuar?"):
            return
        self._apply_config(psf_preset(key))

    def _check_for_pipeline(self, model):
        """Problems that would stop the chain from using this .psf as its template (PIPELINE.check_template)."""
        try:
            import PIPELINE as _P
        except Exception:
            return []           # numpy / pandas not installed: the chain checks it again when it runs
        return _P.check_template(model.to_string().encode("cp1252", "replace").splitlines(keepends=True))

    def _use_in_pipeline(self):
        """Write the .psf to INPUT/PSF/generated.psf and select it as the template of the calculation tab."""
        if not GENERATOR_OK:
            messagebox.showerror("Error", "RADTRAD_ENGINE no disponible."); return
        try:
            model = self._build_model()
            errors = model.validate()
        except Exception as e:
            messagebox.showerror("Error al construir modelo", str(e)); return
        errors += self._check_for_pipeline(model) if not errors else []
        if errors:
            messagebox.showerror("El PSF no se puede usar en el cálculo", "\n".join(f"• {e}" for e in errors))
            return
        path = DIR_PSF / "generated.psf"
        try:
            model.write(path)
        except Exception as e:
            messagebox.showerror("Error al guardar PSF", str(e)); return
        if callable(getattr(self, "on_use", None)):
            self.on_use(path)
        messagebox.showinfo("PSF listo", f"Guardado en:\n{path}\n\nLa pestaña de cálculo lo usará como plantilla. "
                            "La cadena sustituye en cada caso el inventario, los ficheros .inp y .rft, la potencia, "
                            "las fracciones del yodo y el X/Q de las dose locations 1 y 2.")




# =============================================================================
# WRAPPERS + APLICACIÓN UNIFICADA
# =============================================================================

class PipelineContent(PipelineGUI):
    def __init__(self, parent):
        super().__init__(parent)


class PSFContent(PSFApp):
    def __init__(self, parent):
        super().__init__(parent)


class RADTRADApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("RADTRAD Tool  —  Pipeline + Generador PSF + Mapa de zonas")
        self.configure(bg=BG_APP)
        self.geometry("1150x900")
        self.minsize(960, 680)
        if not GENERATOR_OK:
            try:
                err = _ENGINE_IMPORT_TRACEBACK
            except NameError:
                err = "RADTRAD_ENGINE.py no encontrado"
            # Si el error es por numpy/pandas/openpyxl, dar instrucción concreta
            if "numpy" in err or "pandas" in err or "openpyxl" in err:
                messagebox.showwarning(
                    "Dependencias del pipeline no instaladas",
                    "Faltan librerías del pipeline:\n\n"
                    f"{err.splitlines()[-1]}\n\n"
                    "Para instalarlas ejecuta en tu entorno:\n"
                    "  pip install numpy pandas openpyxl\n\n"
                    "El Generador PSF funcionará igualmente.\n"
                    "El Pipeline requiere esas librerías para ejecutarse.")
            else:
                messagebox.showerror(
                    "Error al cargar RADTRAD_ENGINE",
                    f"No se pudo importar RADTRAD_ENGINE.py:\n\n{err}\n\n"
                    "Asegúrate de que RADTRAD_ENGINE.py está en la misma carpeta.")
        self._build_titlebar()
        self._build_notebook()

    def _build_titlebar(self):
        bar = tk.Frame(self, bg=BG_CARD, height=54)
        bar.pack(fill="x"); bar.pack_propagate(False)
        tk.Label(bar, text="⚛", bg=BG_CARD, fg=BLUE,
                 font=("Segoe UI", 22)).pack(side="left", padx=(14, 6), pady=4)
        tf = tk.Frame(bar, bg=BG_CARD); tf.pack(side="left", pady=4)
        tk.Label(tf, text="RADTRAD Tool",
                 bg=BG_CARD, fg=TEXT,
                 font=("Segoe UI Semibold", 14)).pack(anchor="w")
        tk.Label(tf,
                 text="ARCON96 + RADTRAD Pipeline  ·  Generador PSF  ·  Mapa de zonas  ·  IDOM 2025",
                 bg=BG_CARD, fg=MUTED, font=("Segoe UI", 8)).pack(anchor="w")
        tk.Button(bar, text="?  Ayuda", bg=BG_INPUT, fg=BLUE,
                  activebackground=BLUE, activeforeground=WHITE,
                  relief="flat", font=("Segoe UI Semibold", 9), bd=0,
                  padx=12, pady=8, cursor="hand2",
                  command=lambda: ReadmeWindow(self)).pack(side="right", padx=8, pady=8)

    def _build_notebook(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("App.TNotebook",
                        background=BG_APP, borderwidth=0, tabmargins=[0, 0, 0, 0])
        style.configure("App.TNotebook.Tab",
                        background=BG_INPUT, foreground=MUTED,
                        padding=[22, 8], font=("Segoe UI Semibold", 10))
        style.map("App.TNotebook.Tab",
                  background=[("selected", BLUE)],
                  foreground=[("selected", WHITE)])
        nb = ttk.Notebook(self, style="App.TNotebook")
        nb.pack(fill="both", expand=True)

        tab1 = tk.Frame(nb, bg=BG_APP)
        nb.add(tab1, text="  Pipeline ARCON96 + RADTRAD  ")
        self._pipeline_content = PipelineContent(tab1)
        self._pipeline_content.pack(fill="both", expand=True)

        tab2 = tk.Frame(nb, bg=BG_APP)
        nb.add(tab2, text="  Generador PSF  ")
        self._psf_content = PSFContent(tab2)
        self._psf_content.pack(fill="both", expand=True)
        self._psf_content.on_use = lambda path: (self._pipeline_content.psf_widget.use_generated(path),
                                                 nb.select(tab1))

        # Emergency zone map: native view to scale + full map in the browser (mapa_tab.py)
        tab3 = tk.Frame(nb, bg=BG_APP)
        nb.add(tab3, text="  Mapa de zonas  ")
        try:
            from mapa_tab import MapaZonasTab
            self.mapa_tab = MapaZonasTab(tab3, SCRIPT_DIR)
            self.mapa_tab.pack(fill="both", expand=True)
            self.mapa_tab.instalacion_por_defecto = lambda: self._pipeline_content.inst_widget.get()
            self._pipeline_content.on_run_finished = (
                lambda ok: (self.mapa_tab.refrescar(seleccionar_ultimo=True), ok and nb.select(tab3)))
        except Exception as e:
            tk.Label(tab3, text=f"No se pudo cargar el mapa de zonas (mapa_tab.py):\n{e}",
                     bg=BG_APP, fg=RED, font=FONT_UI, justify="left").pack(padx=20, pady=20, anchor="w")

        # Conectar el botón "Abrir Generador PSF" del PsfWidget con el notebook
        try:
            self._pipeline_content.psf_widget.set_notebook(nb)
        except Exception:
            pass


# =============================================================================
# ENTRY POINT
# =============================================================================

def main():
    app = RADTRADApp()
    app.mainloop()


if __name__ == "__main__":
    try:
        main()
    except Exception as _err:
        import traceback as _tb
        _msg = f"{type(_err).__name__}: {_err}\n\n{_tb.format_exc()}"
        try:
            # Intentar mostrar en ventana tkinter
            import tkinter as _tk
            from tkinter import messagebox as _mb
            _r = _tk.Tk(); _r.withdraw()
            _mb.showerror("Error al iniciar RADTRAD Tool", _msg)
            _r.destroy()
        except Exception:
            pass
        raise
