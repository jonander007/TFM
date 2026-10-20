# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
RADTRAD_batch_post_integrated.py - RADTRAD Batch Automation with Integrated NIF Generation

CARACTERÍSTICAS PRINCIPALES:
- NIF INTEGRATION: Detecta automáticamente tid_def.nif; si no existe, lo genera desde Variables_NIF.txt
- Usa template_master.psf en binario (preserva bytes)
- Modifica: fracciones de iodo (I2, CH3I, Aerosol), 10 pares Location 1/2, Output Filename
- Lee X/Q de Excel (columna 19) con manejo robusto desde archivo ARCON96
- Genera estructura por distancia y set; copia soporte; copia carpeta Defaults/defaults; ejecuta RADTRAD
- POSTPROCESO INTEGRADO:
    * Tras cada ejecución OK, parsea .o0 ("Cumulative Dose Summary") y vuelca a CSV acumulativo
    * Al finalizar, crea Excel maestro (µSv y rem) con timeseries, horas clave y percentiles por distancia
    * Opcional: figuras PNG

WORKFLOW NIF:
1. Verifica si Defaults/tid_def.nif existe
2. Si NO existe: busca Variables_NIF.txt, lo parsea, ordena por número atómico, y genera tid_def.nif
3. Si existe: usa el archivo existente
4. Continúa con generación PSF y ejecución RADTRAD normal

Compatible con Python 3.7+
"""

import os
import re
import csv
import json
import math
import glob
import random
import shutil
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Tuple

import pandas as pd
import numpy as np


# ========== NIF GENERATION INTEGRATION ==========
# Integrated NIF file generation functionality
class NuclideData:
    """Clase para manejar datos de un nucleido"""
    def __init__(self, line: str, line_number: int):
        self.raw_line = line.strip()
        self.line_number = line_number
        self.variables = self._parse_line()
        
    def _parse_line(self) -> List[str]:
        """Parsea la línea y extrae variables"""
        vars = self.raw_line.split()
        
        if len(vars) < 12:
            print(f"[NIF-WARN] Línea {self.line_number}: Solo {len(vars)} variables (se esperan 12)")
            vars.extend(['0.0'] * (12 - len(vars)))
        
        return vars
    
    @property
    def nuclide_name(self) -> str:
        """Retorna el nombre del nucleido"""
        return self.variables[0] if self.variables else "Unknown"
    
    @property
    def atomic_number(self) -> int:
        """Extrae número atómico del nombre (ej: I-131 -> 53)"""
        atomic_map = {
            'H': 1, 'C': 6, 'N': 7, 'O': 8, 'Kr': 36, 'Sr': 38,
            'I': 53, 'Xe': 54, 'Cs': 55, 'Ba': 56, 'La': 57,
            'Ce': 58, 'Pu': 94, 'Am': 95, 'Cm': 96
        }
        match = re.match(r'([A-Z][a-z]?)', self.nuclide_name)
        if match:
            symbol = match.group(1)
            return atomic_map.get(symbol, 999)
        return 999
    
    @property
    def mass_number(self) -> int:
        """Extrae número másico (ej: I-131 -> 131)"""
        match = re.search(r'-(\d+)', self.nuclide_name)
        return int(match.group(1)) if match else 0
    
    def format_nif_block(self) -> str:
        """Formatea el bloque NIF con la estructura correcta"""
        v = self.variables
        template = """ Nuclide {0}:
 {1}
   {2}
  {3}
  {4}
  {5}
 {6}     {7}
 {8}     {9}
 {10}     {11}
"""
        return template.format(*v)

def read_nuclides_from_file(filepath: Path) -> List['NuclideData']:
    """Lee nucleidos desde archivo de texto"""
    nuclides = []
    
    if not filepath.exists():
        raise FileNotFoundError(f"[NIF-ERROR] No se encuentra el archivo: {filepath}")
    
    print(f"[NIF] Leyendo: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, start=1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            nuclide = NuclideData(line, i)
            nuclides.append(nuclide)
    
    print(f"[NIF] ✅ {len(nuclides)} nucleidos leídos")
    return nuclides

def sort_nuclides_by_atomic(nuclides: List['NuclideData']) -> List['NuclideData']:
    """Ordena nucleidos por número atómico y número másico"""
    return sorted(nuclides, key=lambda n: (n.atomic_number, n.mass_number))

def write_nif_file(nuclides: List['NuclideData'], output_path: Path) -> None:
    """Escribe el archivo .NIF"""
    print(f"[NIF] Escribiendo: {output_path}")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for nuclide in nuclides:
            f.write(nuclide.format_nif_block())
    
    print(f"[NIF] ✅ Archivo creado: {output_path}")

def generate_nif_if_needed(defaults_dir: Path, variables_nif_txt: Path = None) -> bool:
    """
    Detecta si tid_def.nif existe. Si no, busca Variables_NIF.txt y lo genera.
    
    Returns:
        True si tid_def.nif está disponible (existente o recién generado)
        False si no se pudo obtener/generar tid_def.nif
    """
    nif_path = defaults_dir / "tid_def.nif"
    
    # Caso 1: tid_def.nif ya existe
    if nif_path.exists():
        print(f"[NIF] ✅ tid_def.nif encontrado en: {nif_path}")
        return True
    
    # Caso 2: tid_def.nif no existe, buscar Variables_NIF.txt
    print(f"[NIF] tid_def.nif no encontrado en: {defaults_dir}")
    
    # Buscar Variables_NIF.txt
    if variables_nif_txt is None:
        # Buscar en el directorio actual
        variables_nif_txt = Path("Variables_NIF.txt")
    
    if not variables_nif_txt.exists():
        print(f"[NIF-ERROR] ❌ Variables_NIF.txt no encontrado en: {variables_nif_txt}")
        print(f"[NIF-ERROR] Por favor, proporcione Variables_NIF.txt o un tid_def.nif existente")
        return False
    
    # Generar tid_def.nif desde Variables_NIF.txt
    try:
        print(f"[NIF] Generando tid_def.nif desde: {variables_nif_txt}")
        nuclides = read_nuclides_from_file(variables_nif_txt)
        
        if not nuclides:
            print(f"[NIF-ERROR] ❌ No se encontraron nucleidos válidos en {variables_nif_txt}")
            return False
        
        # Ordenar por número atómico
        print(f"[NIF] Ordenando {len(nuclides)} nucleidos por número atómico...")
        nuclides = sort_nuclides_by_atomic(nuclides)
        
        # Mostrar resumen
        print(f"[NIF] Nucleidos ordenados:")
        for i, nuc in enumerate(nuclides, start=1):
            print(f"[NIF]   {i:2d}. {nuc.nuclide_name:12s} (Z={nuc.atomic_number:2d}, A={nuc.mass_number:3d})")
        
        # Escribir tid_def.nif
        defaults_dir.mkdir(parents=True, exist_ok=True)
        write_nif_file(nuclides, nif_path)
        
        return True
        
    except Exception as e:
        print(f"[NIF-ERROR] ❌ Error al generar tid_def.nif: {e}")
        import traceback
        traceback.print_exc()
        return False

# ========== END NIF GENERATION INTEGRATION ==========

# ---------- CONFIG BÁSICA ----------
TEMPLATE_FILE = "template_master.psf"
EXCEL_DEFAULT = Path("99_5th_PERCENTILE_XQ_VALUES_Sector_BY_HOUR.xlsx")
EXPECTED_TIMES = [0.0, 2.0, 4.0, 8.0, 12.0, 24.0, 96.0, 168.0, 360.0, 720.0]
RADTRAD_EXE_DEFAULT = Path(r"C:\RADTRAD\RADTRAD3.03x\Distribution0203\BatchModeVersion\radtrad.exe")

# ---------- REGEX / FORMATEO ----------
PAIR_RE = re.compile(rb"\s*[+\-]?[0-9]+\.[0-9]+E[+\-][0-9]{2}\s+[+\-]?[0-9]+\.[0-9]+E[+\-][0-9]{2}\s*")
FRAC_RE = re.compile(rb"[0-9]\.\d+E[+\-][0-9]{2}\s+[0-9]\.\d+E[+\-][0-9]{2}\s+[0-9]\.\d+E[+\-][0-9]{2}\s+1\.0000E\+00")

def fmt_e11(v: float) -> bytes:
    return f"{float(v):.4E}".encode().rjust(11)

def read_template(template_path: Path) -> List[bytes]:
    with open(template_path, "rb") as f:
        return f.read().splitlines(keepends=True)

def locate_fraction_line(lines: List[bytes]) -> Optional[int]:
    for i, l in enumerate(lines):
        if FRAC_RE.search(l):
            return i
    return None

def replace_fraction(lines: List[bytes], idx: int, f1: float, f2: float, f3: float) -> None:
    old = lines[idx]
    parts = old.split()
    indent = old[:old.index(parts[0])] if parts else b""
    newline = b"\r\n" if old.endswith(b"\r\n") else b"\n"
    sep = b" "
    lines[idx] = indent + fmt_e11(f1) + sep + fmt_e11(f2) + sep + fmt_e11(f3) + sep + fmt_e11(1.0) + newline

def _find_location_start(lines: List[bytes], title: bytes) -> Optional[int]:
    for i, l in enumerate(lines):
        if l.strip() == title:
            return i
    return None

def _find_first_pair(lines: List[bytes], start_idx: int) -> Optional[int]:
    for j in range(start_idx, len(lines)):
        if PAIR_RE.match(lines[j]):
            return j
        st = lines[j].strip()
        if st.startswith(b"Location ") and j > start_idx:
            break
        if st in (b"Effective Volume Location:", b"Simulation Parameters:", b"Output Filename:"):
            break
    return None

def _find_count_line_above(lines: List[bytes], first_pair_idx: int, limit_up: int) -> Optional[int]:
    for k in range(first_pair_idx - 1, limit_up - 1, -1):
        if lines[k].strip().isdigit():
            return k
    return None

def _block_end(lines: List[bytes], first_pair_idx: int) -> int:
    end = first_pair_idx
    while end < len(lines) and PAIR_RE.match(lines[end]):
        end += 1
    return end

def fill_location_first_block(lines: List[bytes], location_title: str, times: List[float], xqs: List[float], target_pairs: int = 10) -> None:
    title_b = location_title.encode()
    idx_loc = _find_location_start(lines, title_b)
    if idx_loc is None:
        return
    idx_first_pair = _find_first_pair(lines, idx_loc)
    if idx_first_pair is None:
        return
    idx_count = _find_count_line_above(lines, idx_first_pair, idx_loc)
    if idx_count is None:
        return
    idx_end = _block_end(lines, idx_first_pair)
    example = lines[idx_first_pair]
    example_parts = example.split()
    indent = example[:example.index(example_parts[0])] if example_parts else b""
    sep = b" "
    newline = b"\r\n"
    new_pair_lines = [indent + fmt_e11(t) + sep + fmt_e11(q) + newline for t, q in zip(times, xqs)]
    cnt_line = lines[idx_count]
    cnt_indent = cnt_line[:len(cnt_line) - len(cnt_line.lstrip(b" "))]
    cnt_newline = b"\r\n" if cnt_line.endswith(b"\r\n") else b"\n"
    lines[idx_count] = cnt_indent + str(target_pairs).encode() + cnt_newline
    lines[idx_first_pair:idx_end] = new_pair_lines

def replace_output_filename(lines: List[bytes], new_name: str) -> None:
    for i, l in enumerate(lines):
        if l.strip() == b"Output Filename:":
            if i + 1 < len(lines):
                name_ln = lines[i + 1]
                indent = name_ln[:len(name_ln) - len(name_ln.lstrip(b" "))]
                newline = b"\r\n" if name_ln.endswith(b"\r\n") else b"\n"
                lines[i + 1] = indent + new_name.encode() + newline
            break

def _parse_hour_from_sheet_name(name: str) -> Optional[float]:
    m = re.search(r"\((\d+(?:\.\d+)?)\)", str(name))
    return float(m.group(1)) if m else None

def read_xq_series_for_distance(excel_path: Path, distance_m: float, expected_times: List[float]) -> List[float]:
    xls = pd.read_excel(excel_path, sheet_name=None, engine="openpyxl")
    hour_map: Dict[float, pd.DataFrame] = {}
    for name, df in xls.items():
        h = _parse_hour_from_sheet_name(name)
        if h is not None:
            hour_map[h] = df
    if not hour_map:
        return [0.0] * len(expected_times)
    xqs: List[float] = []
    for t in expected_times:
        nearest = min(hour_map.keys(), key=lambda x: abs(x - t))
        df = hour_map[nearest]
        try:
            dist_col = df.iloc[:, 0]
            xq_col = df.iloc[:, 19]
        except Exception:
            xqs.append(0.0)
            continue
        best_idx = None
        best_diff = None
        for idx, dv in enumerate(dist_col):
            try:
                dvf = float(dv)
            except Exception:
                continue
            diff = abs(dvf - float(distance_m))
            if best_diff is None or diff < best_diff:
                best_diff = diff
                best_idx = idx
        if best_idx is None:
            xqs.append(0.0)
            continue
        try:
            xq_val = float(xq_col.iloc[best_idx])
        except Exception:
            xq_val = 0.0
        xqs.append(xq_val)
    return xqs

def collect_support_files_from_exe(radtrad_exe: Path) -> List[Path]:
    exe_dir = radtrad_exe.parent
    candidates = [
        exe_dir / "tid_dba.rft",
        exe_dir / "tid_def.nif",
        exe_dir / "tid14.inp",
    ]
    found: List[Path] = []
    for c in candidates:
        if c.exists():
            found.append(c)
        else:
            print(f"[WARN] No se encontró: {c.name} en {exe_dir}")
    return found

def copy_support_files(target_dir: Path, files: List[Path]) -> None:
    target_dir.mkdir(parents=True, exist_ok=True)
    for src in files:
        try:
            dst = target_dir / src.name
            shutil.copy2(src, dst)
            print(f"[COPY] {src} -> {dst}")
        except Exception as e:
            print(f"[COPY-ERROR] {src}: {e}")

def _copy_tree(src: Path, dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    from distutils.dir_util import copy_tree as _ct  # Py37 stdlib
    _ct(str(src), str(dst))

def copy_defaults_dir(radtrad_exe: Path, target_dir: Path) -> None:
    """
    Copia recursivamente 'Defaults' y/o 'defaults' (si existen) junto al ejecutable.
    """
    exe_dir = radtrad_exe.parent
    for name in ("Defaults", "defaults"):
        src = exe_dir / name
        if src.exists() and src.is_dir():
            dst = target_dir / name
            try:
                _copy_tree(src, dst)
                print(f"[COPY] {src} -> {dst} (recursivo)")
            except Exception as e:
                print(f"[COPY-ERROR] {name}: {e}")
        else:
            print(f"[WARN] Carpeta '{name}' no encontrada en {exe_dir}")

def run_radtrad_batch(psf_path: Path, radtrad_exe: Path, timeout: int = 1800) -> int:
    cwd = psf_path.parent
    log_path = psf_path.with_suffix(".run.log")
    out_o0 = psf_path.with_suffix('.o0').name
    if not radtrad_exe.exists():
        raise FileNotFoundError(f"No se encontró radtrad.exe en: {radtrad_exe}")
    cmd = [str(radtrad_exe), '/b', psf_path.name, out_o0]
    CREATE_NO_WINDOW = 0x08000000
    with open(log_path, "wb") as log:
        try:
            if os.name == "nt":
                res = subprocess.run(cmd, cwd=str(cwd), stdout=log, stderr=log, timeout=timeout, check=False, creationflags=CREATE_NO_WINDOW)
            else:
                res = subprocess.run(cmd, cwd=str(cwd), stdout=log, stderr=log, timeout=timeout, check=False)
        except Exception as e:
            msg = ("[RUN-ERROR] " + str(e)).encode("cp1252", errors="ignore")
            try:
                log.write(msg)
            except Exception:
                pass
            return 1
    return res.returncode

def build_psf_binary(template_lines: List[bytes], distance_m: int, frac_triplet: Tuple[float, float, float], excel_path: Path) -> bytes:
    lines = list(template_lines)
    f1, f2, f3 = frac_triplet
    idx_frac = locate_fraction_line(lines)
    if idx_frac is not None:
        replace_fraction(lines, idx_frac, f1, f2, f3)
    else:
        print("[WARN] No se encontró la línea de fracciones en el template. Se deja igual.")
    xqs = read_xq_series_for_distance(excel_path, float(distance_m), EXPECTED_TIMES)
    fill_location_first_block(lines, 'Location 1:', EXPECTED_TIMES, xqs, target_pairs=len(EXPECTED_TIMES))
    fill_location_first_block(lines, 'Location 2:', EXPECTED_TIMES, xqs, target_pairs=len(EXPECTED_TIMES))
    replace_output_filename(lines, f"Test16_{distance_m}m.o0")
    return b''.join(lines)

# ---------------- POSTPROCESO INTEGRADO ----------------
FACTOR_USV = 10000.0  # 1 rem = 10 000 µSv
CUM_RE = re.compile(r"Cumulative Dose Summary\s*(.*?)\s*Worst Two-Hour Doses", re.S)
NUM_RE = re.compile(r"^[+-]?\d+(?:\.\d+)?(?:[Ee][+-]?\d+)?$")

def parse_cumulative_block(o0_text: str) -> pd.DataFrame:
    """
    Extrae desde 'Cumulative Dose Summary' hasta 'Worst Two-Hour Doses' (excl.).
    Construye df largo con columnas: receptor, time_h, TEDE_rem, Thyroid_rem.
    """
    m = CUM_RE.search(o0_text)
    if not m:
        return pd.DataFrame(columns=["receptor","time_h","TEDE_rem","Thyroid_rem"])
    block = m.group(1)
    lines = [ln.rstrip() for ln in block.splitlines() if ln.strip()]
    # Fila de datos: empieza por número de tiempo y le siguen 6 números (EAB Th, EAB TEDE, LPZ Th, LPZ TEDE, CR Th, CR TEDE)
    rows = []
    for ln in lines:
        if not re.match(r"\s*\d", ln):
            continue
        toks = re.split(r"\s+", ln.strip())
        try:
            t = float(toks[0])
        except Exception:
            continue
        nums = []
        for tk in toks[1:]:
            if NUM_RE.match(tk):
                nums.append(float(tk))
        if len(nums) >= 6:
            # pares: (Th, TEDE) por receptor
            data = {
                "EAB":   {"Thyroid_rem": nums[0], "TEDE_rem": nums[1]},
                "LPZ":   {"Thyroid_rem": nums[2], "TEDE_rem": nums[3]},
                "CR":    {"Thyroid_rem": nums[4], "TEDE_rem": nums[5]},
            }
            for rec, dct in data.items():
                rows.append({"receptor": rec, "time_h": t, "Thyroid_rem": dct["Thyroid_rem"], "TEDE_rem": dct["TEDE_rem"]})
    if not rows:
        return pd.DataFrame(columns=["receptor","time_h","TEDE_rem","Thyroid_rem"])
    df = pd.DataFrame(rows).sort_values(["receptor","time_h"]).reset_index(drop=True)
    return df

def append_to_accumulator(acc_csv: Path, df: pd.DataFrame) -> None:
    """
    Añade filas al CSV acumulativo. Crea cabecera si no existe.
    """
    acc_csv.parent.mkdir(parents=True, exist_ok=True)
    write_header = not acc_csv.exists()
    with open(acc_csv, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(df.columns)
        for _, r in df.iterrows():
            writer.writerow([r[c] for c in df.columns])

def summarize_at_times(ts_df: pd.DataFrame, hours: List[float]) -> pd.DataFrame:
    if ts_df.empty:
        return ts_df
    out = []
    grp = ts_df.groupby(["distance_m","set_id","receptor"])
    for key, sub in grp:
        sub = sub.dropna(subset=["time_h"]).sort_values("time_h")
        xs = sub["time_h"].values
        for met in ["TEDE_rem","Thyroid_rem","TEDE_uSv","Thyroid_uSv"]:
            ys = sub[met].values
            for h in hours:
                val = float(np.interp(h, xs, ys, left=ys[0], right=ys[-1]))
                out.append({
                    "distance_m": key[0], "set_id": key[1], "receptor": key[2],
                    "metric": met.replace("_rem","").replace("_uSv",""),
                    "unit": "uSv" if met.endswith("_uSv") else "rem",
                    "time_h": h, "value": val
                })
    return pd.DataFrame(out)

def percentiles_by_distance(summary_df: pd.DataFrame, unit: str = "uSv", p: float = 95.0) -> pd.DataFrame:
    """
    Calcula P50/P95/Máx agregando sets, por distancia/receptor/métrica/tiempo.
    Solo para una unidad (µSv o rem).
    """
    if summary_df.empty:
        return summary_df
    dfu = summary_df[summary_df["unit"] == unit].copy()
    if dfu.empty:
        return dfu
    def _p(x): return np.percentile(x, p)
    agg = (dfu.groupby(["distance_m","receptor","metric","time_h"])["value"]
           .agg(["median", _p, "max"])
           .reset_index()
           .rename(columns={"median": "p50", "_p": f"p{int(p)}", "max": "p100"}))
    return agg

def write_post_excel(out_xlsx: Path, ts_df: pd.DataFrame, hours: List[float], make_percentiles: bool, make_figs: bool) -> None:
    out_xlsx.parent.mkdir(parents=True, exist_ok=True)
    # separa rem/uSv
    ts_rem = ts_df[["distance_m","set_id","receptor","time_h","TEDE_rem","Thyroid_rem"]].copy()
    ts_uSv = ts_df[["distance_m","set_id","receptor","time_h","TEDE_uSv","Thyroid_uSv"]].copy()

    # resumen a horas clave
    summary = summarize_at_times(ts_df, hours)
    # percentiles por distancia (uSv)
    agg = percentiles_by_distance(summary, unit="uSv", p=95.0) if make_percentiles else pd.DataFrame()

    with pd.ExcelWriter(out_xlsx, engine="openpyxl") as w:
        ts_rem.sort_values(["distance_m","set_id","receptor","time_h"]).to_excel(w, sheet_name="timeseries_rem", index=False)
        ts_uSv.sort_values(["distance_m","set_id","receptor","time_h"]).to_excel(w, sheet_name="timeseries_uSv", index=False)
        summary[summary["unit"]=="rem"].sort_values(["distance_m","set_id","receptor","metric","time_h"]).to_excel(w, sheet_name="key_times_rem", index=False)
        summary[summary["unit"]=="uSv"].sort_values(["distance_m","set_id","receptor","metric","time_h"]).to_excel(w, sheet_name="key_times_uSv", index=False)
        if not agg.empty:
            agg.sort_values(["distance_m","receptor","metric","time_h"]).to_excel(w, sheet_name="distance_percentiles_uSv", index=False)

    # figuras opcionales
    if make_figs and not agg.empty:
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            figs_dir = out_xlsx.parent / "figs"
            figs_dir.mkdir(exist_ok=True)
            for receptor in agg["receptor"].unique():
                for metric in ["TEDE","Thyroid"]:
                    for t in [2, 8, 24]:
                        sel = agg[(agg["receptor"]==receptor)&(agg["metric"]==metric)&(agg["time_h"]==t)]
                        if sel.empty: 
                            continue
                        sel = sel.sort_values("distance_m")
                        plt.figure(figsize=(10,5))
                        plt.plot(sel["distance_m"], sel["p50"], label="P50", lw=2)
                        plt.plot(sel["distance_m"], sel["p95"], label="P95", lw=2)
                        plt.plot(sel["distance_m"], sel["p100"], label="Máx", lw=1.5, alpha=0.8)
                        plt.xlabel("Distancia [m]"); plt.ylabel(f"{metric} [µSv] acumulada"); 
                        plt.title(f"{metric} vs distancia @ {t} h ({receptor})")
                        plt.grid(alpha=0.3); plt.legend()
                        plt.tight_layout(); 
                        plt.savefig(figs_dir / f"{metric}_vs_dist_{receptor}_{int(t)}h.png", dpi=160)
                        plt.close()
            print(f"[FIGS] Figuras en: {figs_dir}")
        except Exception as e:
            print(f"[FIGS-WARN] {e}")

def postprocess_one_o0(o0_path: Path, distance_m: int, set_id: int, meta: Dict, acc_csv: Path) -> Optional[pd.DataFrame]:
    """
    Postprocesa un .o0 inmediatamente tras su ejecución, añade datos al CSV acumulativo.
    """
    if not o0_path.exists():
        print(f"[POST-WARN] No existe {o0_path}")
        return None
    text = o0_path.read_text(encoding="cp1252", errors="ignore")
    df = parse_cumulative_block(text)
    if df.empty:
        print(f"[POST-WARN] No se pudo parsear Cumulative Dose Summary en {o0_path.name}")
        return None
    # Añadir claves
    df["distance_m"] = distance_m
    df["set_id"] = set_id
    # µSv
    df["TEDE_uSv"] = df["TEDE_rem"] * FACTOR_USV
    df["Thyroid_uSv"] = df["Thyroid_rem"] * FACTOR_USV
    # Metadatos (fracciones, etc.)
    for k in ("frac_I2","frac_CH3I","frac_AER","times_h","xq_series"):
        if k in meta:
            df[k] = json.dumps(meta[k]) if isinstance(meta[k], (list, dict)) else meta[k]
    # CSV incremental
    append_to_accumulator(acc_csv, df[["distance_m","set_id","receptor","time_h","TEDE_rem","Thyroid_rem","TEDE_uSv","Thyroid_uSv","frac_I2","frac_CH3I","frac_AER"]])
    return df

# -------------------- MAIN --------------------
def main():
    import argparse
    ap = argparse.ArgumentParser(description='Genera PSF batch (template binario), ejecuta RADTRAD /b y postprocesa .o0')
    ap.add_argument('--output-root', default='psf_batch', help='Carpeta raíz de salida')
    ap.add_argument('--seed', type=int, default=1234, help='Semilla para fracciones aleatorias')
    ap.add_argument('--nsets', type=int, default=20, help='Número de sets por distancia')
    ap.add_argument('--dist-start', type=int, default=10, help='Distancia inicial (m)')
    ap.add_argument('--dist-end', type=int, default=400, help='Distancia final (m)')
    ap.add_argument('--dist-step', type=int, default=10, help='Paso (m)')
    ap.add_argument('--fractions', nargs=3, type=float, default=None, help='Fracciones fijas I2 CH3I Aerosol (se normalizan)')
    ap.add_argument('--template', type=Path, default=Path(TEMPLATE_FILE), help='Ruta al template maestro .psf')
    ap.add_argument('--excel', type=Path, default=EXCEL_DEFAULT, help='Excel con X/Q (columna T = índice 19)')
    ap.add_argument('--radtrad-exe', type=Path, default=RADTRAD_EXE_DEFAULT, help='Ruta al ejecutable radtrad.exe')
    ap.add_argument('--timeout', type=int, default=1800, help='Tiempo máximo por ejecución (s)')
    ap.add_argument('--no-run', action='store_true', help='No ejecutar RADTRAD (solo generar PSFs)')
    # Postproc
    ap.add_argument('--no-postproc', action='store_true', help='No hacer postproceso integrado')
    ap.add_argument('--post-times', default='2,8,24,96,168,360,720', help='Horas clave CSV (ej: 2,8,24,96,168,360,720)')
    ap.add_argument('--post-out', default='RADTRAD_post.xlsx', help='Nombre del Excel final')
    ap.add_argument('--post-figs', action='store_true', help='Generar figuras PNG de percentiles')
    ap.add_argument('--no-percentiles', action='store_true', help='No calcular hoja de percentiles por distancia')

    args = ap.parse_args()
    random.seed(args.seed)

    if not args.template.exists():
        print(f"[ERROR] Template no encontrado: {args.template}")
        raise SystemExit(1)
    if not args.excel.exists():
        print(f"[ERROR] Excel no encontrado: {args.excel}")
        raise SystemExit(1)

    support_files = collect_support_files_from_exe(args.radtrad_exe)
    if support_files:
        print('[INFO] Archivos de soporte detectados:')
        for p in support_files:
            print(' -', p)
    else:
        print(f"[WARN] No se encontraron archivos de soporte en {args.radtrad_exe.parent}")

    # ========== NIF GENERATION CHECK ==========
    # Check if we need to copy/generate NIF file to working Defaults folder
    working_defaults = Path("Defaults")
    if not working_defaults.exists():
        print(f"[WARN] Carpeta Defaults no encontrada en directorio de trabajo")
        print(f"[INFO] Se copiará desde RADTRAD durante la ejecución")
    else:
        # Try to generate NIF if needed in the working Defaults folder
        nif_ok = generate_nif_if_needed(working_defaults)
        if not nif_ok:
            print(f"[ERROR] No se pudo obtener/generar tid_def.nif")
            print(f"[ERROR] Proporcione Variables_NIF.txt o asegúrese de que Defaults/tid_def.nif exista")
            raise SystemExit(1)
    # ========== END NIF CHECK ==========


    distances = list(range(int(args.dist_start), int(args.dist_end) + 1, int(args.dist_step)))
    template_lines = read_template(args.template)
    out_root = Path(args.output_root)
    out_root.mkdir(parents=True, exist_ok=True)

    # Postproc: paths
    post_dir = out_root / "postprocess"
    acc_csv = post_dir / "post_timeseries_accum.csv"
    runs_index: List[Dict] = []

    for d in distances:
        dist_dir = out_root / f"{d}_m"
        dist_dir.mkdir(parents=True, exist_ok=True)
        for k in range(1, int(args.nsets) + 1):
            set_dir = dist_dir / f"frac_set_{k:02d}"
            set_dir.mkdir(parents=True, exist_ok=True)

            if support_files:
                copy_support_files(set_dir, support_files)
            copy_defaults_dir(args.radtrad_exe, set_dir)

            if args.fractions:
                f1, f2, f3 = args.fractions
                s = (f1 + f2 + f3) or 1.0
                f1, f2, f3 = f1/s, f2/s, f3/s
            else:
                r1, r2, r3 = random.random(), random.random(), random.random()
                s = r1 + r2 + r3
                f1, f2, f3 = r1/s, r2/s, r3/s

            psf_bytes = build_psf_binary(template_lines, d, (f1, f2, f3), args.excel)
            psf_name = f"Test16_{d}m.psf"
            psf_path = set_dir / psf_name
            with open(psf_path, 'wb') as f:
                f.write(psf_bytes)
            print(f"[OK] {psf_path}")

            # Guardar metadatos del set (útil en el post)
            meta = {
                "distance_m": d,
                "set_id": k,
                "frac_I2": f1, "frac_CH3I": f2, "frac_AER": f3,
                "times_h": EXPECTED_TIMES,
                "xq_series": read_xq_series_for_distance(args.excel, float(d), EXPECTED_TIMES)
            }
            (set_dir / "run_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

            rc = None
            if not args.no_run:
                try:
                    rc = run_radtrad_batch(psf_path, args.radtrad_exe, timeout=args.timeout)
                    if rc == 0:
                        print(f"[RUN] radtrad.exe OK (rc=0): {psf_path.name}")
                    else:
                        print(f"[RUN] radtrad.exe terminó con rc={rc}: {psf_path.name}")
                except Exception as e:
                    print(f"[RUN-ERROR] {e}")
                    rc = 1

            # POSTPROCESO EN CALIENTE
            if (not args.no_postproc) and (rc == 0 or args.no_run):
                o0_path = psf_path.with_suffix(".o0")
                # Si no run, el .o0 puede no existir; no pasa nada, se hará al final si ya existieran.
                if o0_path.exists():
                    df_case = postprocess_one_o0(o0_path, d, k, meta, acc_csv)
                else:
                    df_case = None
            else:
                df_case = None

            runs_index.append({
                "distance_m": d,
                "set_id": k,
                "psf_path": str(psf_path),
                "o0_path": str(psf_path.with_suffix(".o0")),
                "rc": rc if rc is not None else (-1 if args.no_run else None)
            })

    print('[DONE] Generación', '(sin ejecución)' if args.no_run else 'y ejecución', 'completadas en', out_root.resolve())

    # ---------------- FIN DEL BUCLE: POSTPROCESO FINAL ----------------
    if not args.no_postproc:
        # 1) Si acc_csv no existe (p.ej. corriste con --no-run), intenta parsear todos los .o0 ahora
        if not acc_csv.exists():
            print("[POST] No se encontró acumulador; buscando .o0 para parseo final...")
            all_o0 = list(out_root.glob("*_m/frac_set_*/Test16_*m.o0"))
            for o0 in all_o0:
                # recuperar distance/set
                m_d = re.search(r"_(\d{1,4})m", o0.name)
                m_s = re.search(r"frac_set_(\d+)", str(o0.parent))
                d = int(m_d.group(1)) if m_d else None
                s = int(m_s.group(1)) if m_s else None
                # meta si existe
                meta_path = o0.parent / "run_meta.json"
                meta = {}
                if meta_path.exists():
                    try:
                        meta = json.loads(meta_path.read_text(encoding="utf-8"))
                    except Exception:
                        pass
                if d is None or s is None:
                    continue
                postprocess_one_o0(o0, d, s, meta, acc_csv)

        # 2) Construir Excel maestro
        if acc_csv.exists():
            ts_df = pd.read_csv(acc_csv)
            # Excel final
            hours = [float(x) for x in str(args.post_times).split(",") if x.strip()]
            post_out = (out_root / "postprocess" / args.post_out)
            write_post_excel(post_out, ts_df, hours, make_percentiles=(not args.no_percentiles), make_figs=args.post_figs)
            # Export runs_index y logs
            runs_df = pd.DataFrame(runs_index).sort_values(["distance_m","set_id"])
            logs = []
            for _, r in runs_df.iterrows():
                lp = Path(r["o0_path"]).with_suffix(".run.log")
                if lp.exists():
                    txt = lp.read_text(encoding="cp1252", errors="ignore")
                    status = "OK"
                    if re.search(r"error|failed|rc=\s*[1-9]", txt, flags=re.IGNORECASE):
                        status = "CHECK_LOG"
                    logs.append({"distance_m": r["distance_m"], "set_id": r["set_id"], "log_path": str(lp), "status": status})
            with pd.ExcelWriter(post_out, engine="openpyxl", mode="a") as w:
                runs_df.to_excel(w, sheet_name="runs_index", index=False)
                if logs:
                    pd.DataFrame(logs).to_excel(w, sheet_name="logs", index=False)
            print(f"[POST] Excel: {post_out}")
        else:
            print("[POST-WARN] No se generó Excel (no hay datos acumulados).")

if __name__ == '__main__':
    main()