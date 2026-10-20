#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PIPELINE.py  —  ARCON96 + RADTRAD unified runner
=================================================
Author : Gilberto Villescas Díaz
Company: IDOM
Date   : 2025

Pipeline:
  PHASE 1 — ARCON96 batch runs (OVERALL + SECTOR)
              → 99_5th_PERCENTILE_XQ_VALUES_Sector_BY_HOUR.xlsx
  PHASE 2 — RADTRAD PSF generation + batch execution
              → psf_batch/frac_set_XX/YYY_m/Test16_YYYm.psf + .o0
  PHASE 3 — Post-process: Sets_Worst2h.xlsx

All interactive parameters are collected in a single session at startup.

Bug fixes vs original scripts:
  - Sheet naming: H1h (was erroneously "H0h" for 1-hour averaging)
  - EXPECTED_TIMES aligned with HORAS_VALIDAS: both [1,2,4,8,12,24,96,168,360,720]
"""

from __future__ import annotations

import argparse, csv, json, logging, os, random, re, shutil, subprocess, sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill

try:
    from distutils.dir_util import copy_tree
except ImportError:
    def copy_tree(src: str, dst: str):
        shutil.copytree(src, dst, dirs_exist_ok=True)

# ===========================================================================
# GLOBAL PATHS & CONSTANTS
# ===========================================================================
SCRIPT_DIR = Path(__file__).resolve().parent
CWD        = SCRIPT_DIR / "ARCON"   # all ARCON96 runs and outputs go here

ARCON_EXE   = Path(r"C:\ARCON96\arcon96f.exe")
RADTRAD_EXE = Path(r"C:\RADTRAD\RADTRAD3.03x\Distribution0203\BatchModeVersion\radtrad.exe")
MET_BASE    = SCRIPT_DIR

# ARCON96 output files
SALIDA_LOG_OVERALL  = CWD / "Output_Log_Overall.txt"
INTERVALOS_OVERALL  = CWD / "Intervals_Overall.txt"
SALIDAS_LOG_SECTOR  = CWD / "Output_Log_Sector.txt"
INTERVALOS_SECTOR   = CWD / "Intervals_Sector.txt"
MAXIMO_SECTOR       = CWD / "Maximum_Sector.txt"
TOTAL_XQ_COLUMNAS   = CWD / "Total_XQ_Sector_Columns.txt"
PERCENTIL95_OVERALL = CWD / "95th_PERCENTILE_XQ_VALUES.txt"
FRECUENCIAS_SECTOR  = CWD / "Frequencies_Sectors.txt"

# Bridge files (ARCON96 output → RADTRAD input)
XQ_EXCEL       = CWD / "99_5th_PERCENTILE_XQ_VALUES_Sector_BY_HOUR.xlsx"
TOTAL_XQ_EXCEL = CWD / "TOTAL_XQs_BY_HOUR.xlsx"
XQ_MAX_TXT     = CWD / "XQ_Maximmun_by_hour.txt"

# Timeouts
ARCON_TIMEOUT   = 900
RADTRAD_TIMEOUT = 1800

# Averaging hours — ALIGNED between both phases (bug fix: was [0,2,4...] in IRADOA)
HORAS_VALIDAS  = [1, 2, 4, 8, 12, 24, 96, 168, 360, 720]
EXPECTED_TIMES = HORAS_VALIDAS   # same list, explicit alias for clarity

# 95th-percentile output formatting
P95_LABEL = 26
P95_WIDTH = 13
P95_FMT   = "{:>" + str(P95_WIDTH) + ".2E}"

# Dose unit conversions
FACTOR_USV = 10_000.0
REM_TO_MSV = 10.0

# Regex
NUM_PAT = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][+-]?\d+)?"
NUM_RE  = re.compile(NUM_PAT)
RE_CASE = re.compile(r"^X_(\d{3})_V_(\d+)$")

# PSF binary patterns
_PAIR_RE  = re.compile(rb"\s*(?:\[\s*)?-?\d+\.\d+E[+-]\d{2}\s+-?\d+\.\d+E[+-]\d{2}\s*(?:\]\s*)?")
_PFALLBACK= re.compile(rb"-?\d+\.\d+E[+-]\d{2}\s+-?\d+\.\d+E[+-]\d{2}")
_FRAC_RE  = re.compile(rb"\d\.\d+E[+-]\d{2}\s+\d\.\d+E[+-]\d{2}\s+\d\.\d+E[+-]\d{2}\s+1\.0000E\+00")


# ===========================================================================
# LOGGING
# ===========================================================================
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(message)s",
        datefmt="%H:%M:%S",
    )
    logging.info("Python %s  |  Script: %s", sys.version.split()[0], SCRIPT_DIR)


# ===========================================================================
# INTERACTIVE PARAMETER COLLECTION
# ===========================================================================
def _ask_int(prompt, default, lo=1, hi=99999):
    while True:
        raw = input(prompt).strip()
        if not raw:
            return default
        try:
            v = int(raw)
            if lo <= v <= hi:
                return v
        except ValueError:
            pass
        print(f"  Must be an integer between {lo} and {hi}.")


def _ask_yn(prompt, default=True):
    tag = "(ENTER=Y/n)" if default else "(y/N=ENTER)"
    while True:
        raw = input(f"{prompt} {tag}: ").strip().lower()
        if raw in ("", "y", "yes", "s", "si"):
            return True
        if raw in ("n", "no"):
            return False
        print("  Answer y or n.")


def _ask_fractions(nsets):
    print(f"\n  Iodine fractions per set  ({nsets} sets)")
    print("  Format: AER,I2,CH3I  e.g. 0.6,0.3,0.1")
    print("  ENTER = random Dirichlet sampling\n")
    sets = []
    for k in range(1, nsets + 1):
        while True:
            raw = input(f"  Set {k:02d} (ENTER=random): ").strip()
            if not raw:
                sets.append(None); break
            try:
                parts = [float(x) for x in raw.split(",") if x.strip()]
                if len(parts) != 3 or sum(parts) <= 0:
                    raise ValueError
                s = sum(parts)
                sets.append((parts[0]/s, parts[1]/s, parts[2]/s)); break
            except ValueError:
                print("  Enter three comma-separated positive numbers.")
    return sets


# ===========================================================================
# NIF GENERATION  (integrated from NIF.py)
# ===========================================================================
NIF_TEMPLATE = """ Nuclide {0}:
 {1}
  {2}
  {3}
  {4}
  {5}
 {6}     {7}
 {8}     {9}
 {10}     {11}"""

def _fmt_nif(value, is_integer=False, is_halflife=False):
    if is_integer:
        return str(int(float(value)))
    val = float(value)
    if val == 0:
        return "0.0000000000E+00" if is_halflife else "0.0000E+00"
    return f"{val:.10E}" if is_halflife else f"{val:.4E}"


def generate_nif(txt_path: Path, out_nif: Path) -> Path:
    """
    Read a Variables_NIF-style TXT (one nuclide per line, 12 tokens) and
    write a properly formatted .NIF file.  Returns the output path.

    Token layout per line:
      0  nuclide_number   (e.g. 001)
      1  element_name     (e.g. Xe-131m)
      2  release_group    (plain integer)
      3  half_life        (10-decimal scientific)
      4  mass_number      (4-decimal scientific)
      5  activity         (4-decimal scientific)
      6  daughter1_name
      7  daughter1_ratio  (4-decimal scientific)
      8  daughter2_name
      9  daughter2_ratio
      10 daughter3_name
      11 daughter3_ratio
    """
    lines = [l for l in txt_path.read_text(encoding="utf-8", errors="replace").splitlines()
             if l.strip()]
    if not lines:
        raise ValueError(f"Variables file is empty: {txt_path}")

    with out_nif.open("w", newline="\r\n", encoding="utf-8") as f:
        f.write(" Nuclide Inventory Name:\n")
        f.write(" Normalized i_SMR 530.4 MWth Core Inventory\n")
        f.write(" Power Level:\n")
        f.write("  0.1000E+01\n")
        f.write(" Nuclides:\n")
        f.write(f"  {len(lines)}\n")

        for line in lines:
            tokens = line.strip().split()
            if len(tokens) < 12:
                raise ValueError(
                    f"Line has {len(tokens)} tokens (expected 12):\n  {line.strip()}"
                )
            fv = []
            for i, tok in enumerate(tokens[:12]):
                if   i == 0:          fv.append(tok)
                elif i == 1:          fv.append(tok)
                elif i == 2:          fv.append(_fmt_nif(tok, is_integer=True))
                elif i == 3:          fv.append(_fmt_nif(tok, is_halflife=True))
                elif i in (4, 5):     fv.append(_fmt_nif(tok))
                elif i in (6, 8, 10): fv.append(tok)
                elif i in (7, 9, 11): fv.append(_fmt_nif(tok))
            f.write(NIF_TEMPLATE.format(*fv) + "\n")

    logging.info("NIF generated: %s  (%d nuclides)", out_nif.name, len(lines))
    return out_nif


def _ask_nif() -> str:
    """
    Ask how to handle the .nif file.
    Returns the filename to use inside defaults\\.
    If generation is chosen, creates the .NIF file next to the script right now.
    """
    NIF_DEFAULT = "tid_def.nif"
    VAR_DEFAULT = "Variables_NIF.txt"

    print("\n  .nif file — choose an option:")
    print("    1  Use existing .nif  (enter filename, default: tid_def.nif)")
    print("    2  Generate from a Variables_NIF.txt file")

    while True:
        choice = input("  Option 1/2 (ENTER=1): ").strip() or "1"
        if choice == "1":
            raw = input(f"  .nif filename  (ENTER={NIF_DEFAULT}): ").strip()
            return raw or NIF_DEFAULT

        elif choice == "2":
            raw_txt = input(f"  Variables TXT path  (ENTER={VAR_DEFAULT}): ").strip()
            txt_path = Path(raw_txt) if raw_txt else SCRIPT_DIR / VAR_DEFAULT

            if not txt_path.exists():
                print(f"  ✗ File not found: {txt_path}")
                print("    Make sure the TXT is in the script folder or enter the full path.")
                continue

            raw_nif = input("  Output .nif name  (ENTER=i_SMR.nif): ").strip()
            nif_name = raw_nif if raw_nif else "i_SMR.nif"
            defaults_dir = SCRIPT_DIR / "Defaults"
            defaults_dir.mkdir(exist_ok=True)
            out_nif = defaults_dir / nif_name

            try:
                generate_nif(txt_path, out_nif)
                print(f"  ✓ NIF generated → {out_nif}")
            except Exception as e:
                print(f"  ✗ NIF generation failed: {e}")
                print("    Fix the TXT file and try again, or choose option 1.")
                continue

            return nif_name

        else:
            print("  ✗ Enter 1 or 2.")


def ask_all_params():
    SEP = "─" * 62
    print(f"\n{SEP}\n  PIPELINE — unified parameter setup\n{SEP}")

    print("\n  ── ARCON96 ──────────────────────────────────────────────")
    num_met  = _ask_int("  MET files count           (ENTER=1):    ", 1,  1, 99)
    dist_min = _ask_int("  Minimum distance [m]      (ENTER=10):   ", 10, 1)
    dist_max = _ask_int("  Maximum distance [m]      (ENTER=400):  ", 400, dist_min+1)
    delta    = _ask_int("  Distance step [m]         (ENTER=10):   ", 10, 1)

    print("\n  ── RADTRAD ──────────────────────────────────────────────")
    tpl_def = SCRIPT_DIR / "template_master.psf"
    raw = input(f"  PSF template   (ENTER={tpl_def.name}): ").strip()
    template_path = Path(raw) if raw else tpl_def

    nsets      = _ask_int("  Fraction sets count       (ENTER=6):   ", 6, 1, 999)
    fixed_sets = _ask_fractions(nsets)

    print("\n  ── Support files ────────────────────────────────────────")
    DEF = ("tid_dba.rft", "fgr11&12.inp")
    rft = input(f"  .rft  (ENTER={DEF[0]}): ").strip() or DEF[0]
    nif = _ask_nif()          # Option 1: manual name  |  Option 2: generate from TXT
    inp = input(f"  .inp  (ENTER={DEF[1]}): ").strip() or DEF[1]

    raw_exe = input(f"  RADTRAD exe  (ENTER=default): ").strip()
    radtrad_exe = Path(raw_exe) if raw_exe else RADTRAD_EXE

    raw_out = input("  RADTRAD output folder  (ENTER=psf_batch): ").strip()
    out_root = Path(raw_out) if raw_out else Path("psf_batch")

    no_run = not _ask_yn("\n  Execute RADTRAD?", default=True)

    print(f"\n{SEP}\n")
    return dict(
        num_met=num_met, dist_min=dist_min, dist_max=dist_max, delta=delta,
        template_path=template_path, nsets=nsets, fixed_sets=fixed_sets,
        support_names=(rft, nif, inp),
        radtrad_exe=radtrad_exe, out_root=out_root, no_run=no_run,
    )


# ===========================================================================
# FILESYSTEM UTILITIES
# ===========================================================================
class ConfigError(Exception): ...
class ExecutionError(Exception): ...


def _unlink(p):
    try: p.unlink()
    except (FileNotFoundError, PermissionError): pass

def _safe_rm(p):
    if p.exists(): _unlink(p); logging.info("Deleted: %s", p.name)

def _rmdir(p):
    if p.exists() and p.is_dir():
        try: shutil.rmtree(p)
        except OSError as e: logging.warning("Cannot remove %s: %s", p, e)

def _ensure_writable(p):
    try:
        p.mkdir(parents=True, exist_ok=True)
        probe = p / ".probe.tmp"; probe.write_text("ok"); _unlink(probe)
    except OSError as e:
        raise ConfigError(f"Cannot write under {p}: {e}") from e

def _tail(p, n=60):
    try: return "\n".join(p.read_text(encoding="utf-8", errors="replace").splitlines()[-n:])
    except: return "<unreadable>"

def _clean_arcon_dirs():
    logging.info("Cleaning previous ARCON96 run directories...")
    for sub in CWD.iterdir():
        if sub.is_dir() and (sub.name[0].isdigit() or RE_CASE.match(sub.name)):
            _rmdir(sub)
    for f in CWD.glob("*.xlsx"):
        _unlink(f)


def _ask_delete_arcon_dirs():
    """
    After ARCON96 finishes, ask the user whether to delete the run
    sub-directories (OVERALL: NNN_NN/  and SECTOR: X_NNN_V_NNN/).
    The bridge Excel and TXT outputs are kept regardless.
    """
    # Count how many directories exist and their total size
    dirs = [
        sub for sub in CWD.iterdir()
        if sub.is_dir() and (sub.name[0].isdigit() or RE_CASE.match(sub.name))
    ]
    if not dirs:
        return   # nothing to delete

    total_mb = sum(
        sum(f.stat().st_size for f in d.rglob("*") if f.is_file())
        for d in dirs
    ) / (1024 ** 2)

    print(f"\n  ARCON96 generated {len(dirs)} run directories ({total_mb:.1f} MB).")
    print("  These contain the raw .log, .cfd and .out files.")
    print("  The bridge Excel and TXT outputs have already been saved.")

    while True:
        raw = input("  Delete ARCON96 run directories? (y/N=ENTER): ").strip().lower()
        if raw in ("", "n", "no"):
            logging.info("ARCON96 run directories kept.")
            return
        if raw in ("y", "yes", "s", "si"):
            deleted = 0
            for d in dirs:
                _rmdir(d)
                deleted += 1
            logging.info("Deleted %d ARCON96 run directories.", deleted)
            return
        print("  Answer y or n.")


# ===========================================================================
# ARCON96 — RSF
# ===========================================================================
def _validate_rsf(text):
    warn = []
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if not lines: return ["Empty RSF"]
    def is_num(t):
        try: float(t); return True
        except: return False
    def n_ints(ln):
        return sum(1 for t in ln.replace(",", " ").split() if t.lstrip("+-").isdigit())
    try:
        nm = int(lines[0])
        for i in range(1, 1+nm):
            if i >= len(lines) or not lines[i].upper().endswith(".MET"):
                warn.append(f"L{i+1}: expected *.MET")
    except: warn.append("L1: expected integer")
    if not any(l.lower().endswith(".log") for l in lines): warn.append("No *.log line")
    if not any(l.lower().endswith(".cfd") for l in lines): warn.append("No *.cfd line")
    if sum(1 for ln in lines if sum(1 for t in ln.replace(",", " ").split() if is_num(t)) == 2) < 1:
        warn.append("No 2-number line")
    if sum(1 for ln in lines if n_ints(ln) == 10) < 2:
        warn.append("< 2 lines with 10 integers")
    if lines[-1].lower() not in ("y", "n"): warn.append(f"Last line not y/n: {lines[-1]!r}")
    return warn


def _gen_rsf(num_met, value, xxx=None):
    mets = "\n".join(f"MET{i:02d}.MET" for i in range(1, num_met+1))
    direction = "  180 360" if xxx is None else f"  {xxx:3d} 45"
    return (
        f" {num_met}\n {mets}\n    10.00\n    58.00\n   1\n   1\n"
        f"     0.00\n     0.01\n     0.00\n     0.00\n     0.00\n"
        f"{direction}\n    {value:.2f}\n      0.00\n      0.00\n"
        f"ISMR.log\nISMR.cfd\n     0.2\n     0.50\n     4.30\n"
        f"   1   2   4   8  12  24  96 168 360 720\n"
        f"   1   2   4   8  11  22  87 152 324 648\n"
        f"     0.00     0.00\ny"
    )


# ===========================================================================
# ARCON96 — EXECUTION & LOG PARSING
# ===========================================================================
def _copy_mets(src, dst, n):
    copied = []
    for i in range(1, n+1):
        name = f"MET{i:02d}.MET"
        shutil.copy2(src/name, dst/name); copied.append(dst/name)
    return copied


def _run_arcon(case_dir, rsf, exe, qa):
    for w in _validate_rsf(rsf):
        logging.warning("[%s] RSF: %s", case_dir.name, w)
    (case_dir / "arconin.rsf").write_text(rsf, encoding="cp1252")
    out = case_dir / f"{case_dir.name}.out"
    try:
        with out.open("w", encoding="utf-8", errors="replace") as fo:
            rc = subprocess.run(
                [str(exe)], cwd=str(case_dir),
                input=f"arconin.rsf\r\n{qa}\r\n",
                text=True, stdout=fo, stderr=subprocess.STDOUT,
                check=False, timeout=ARCON_TIMEOUT,
            ).returncode
        return rc
    except subprocess.TimeoutExpired:
        logging.error("Timeout in %s", case_dir.name); return 124
    except FileNotFoundError as e:
        raise ExecutionError(f"Cannot launch ARCON96: {e}") from e


def _parse_log(case_dir, log_out, intervals_out, p95_path=None):
    lp = case_dir / "ISMR.log"
    if not lp.exists(): logging.warning("ISMR.log missing: %s", case_dir.name); return
    try: lines = lp.read_text(encoding="cp1252", errors="replace").splitlines()
    except Exception as e: logging.warning("Read error %s: %s", case_dir.name, e); return
    i, n = 0, len(lines)
    while i < n:
        ln = lines[i]
        if "AVER. PER." in ln:
            with log_out.open("a", encoding="utf-8") as f: f.write(f"{case_dir.name}: {ln}\n")
            i += 1; continue
        if "TOTAL X/Qs" in ln:
            with log_out.open("a", encoding="utf-8") as f:
                f.write(f"{case_dir.name}: {ln}\n")
                if i+1 < n: f.write(f"{case_dir.name}: {lines[i+1]}\n")
            i += 2; continue
        if "95th PERCENTILE X/Q VALUES" in ln:
            if i+1 < n:
                vl = lines[i+1]
                with log_out.open("a", encoding="utf-8") as f: f.write(f"{case_dir.name}: {vl}\n")
                if p95_path:
                    nums = [float(x) for x in NUM_RE.findall(vl)]
                    if len(nums) >= len(HORAS_VALIDAS):
                        _append_p95(p95_path, case_dir.name, nums)
                    else:
                        logging.warning("%s: only %d P95 values", case_dir.name, len(nums))
            i += 2; continue
        if "95% X/Q for standard averaging intervals" in ln:
            with intervals_out.open("a", encoding="utf-8") as f:
                f.write(f"{case_dir.name}:\n")
                for j in range(1, 7):
                    if i+j < n: f.write(lines[i+j] + "\n")
            i += 7; continue
        i += 1


def _run_case(dir_name, rsf, log_out, intervals_out, exe, met_base, num_met, p95_path=None):
    case_dir = CWD / dir_name
    _rmdir(case_dir); _ensure_writable(case_dir)
    mets = _copy_mets(met_base, case_dir, num_met)
    rc = _run_arcon(case_dir, rsf, exe, f"{case_dir.name}_user.qa")
    for m in mets: _unlink(m)
    if rc != 0:
        logging.error("ARCON96 rc=%d — %s", rc, dir_name)
    else:
        logging.info("ARCON96 OK — %s", dir_name)
    if not (case_dir / "ISMR.log").exists():
        logging.error("ISMR.log missing — %s", dir_name); return
    _parse_log(case_dir, log_out, intervals_out, p95_path)


# ===========================================================================
# ARCON96 — 95th PERCENTILE
# ===========================================================================
def _write_p95_header(path):
    with path.open("w", encoding="utf-8") as f:
        f.write("95th PERCENTILE X/Q VALUES\n")
        f.write("".ljust(P95_LABEL))
        for h in HORAS_VALIDAS: f.write(f"{h:>{P95_WIDTH}d}")
        f.write("\n")

def _append_p95(path, name, vals):
    prefix = f"{name}:"; pad = max(P95_LABEL - len(prefix), 1)
    with path.open("a", encoding="utf-8") as f:
        f.write(prefix + " " * pad)
        for v in vals[:len(HORAS_VALIDAS)]: f.write(P95_FMT.format(v))
        f.write("\n")

def _load_p95_by_v(path, hora):
    result = {}
    if not path.exists() or hora not in HORAS_VALIDAS: return result
    idx = HORAS_VALIDAS.index(hora)
    for ln in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if ":" not in ln: continue
        tag, tail = ln.split(":", 1); tag = tag.strip()
        if "_" in tag:
            v = tag.split("_", 1)[0]
            nums = [float(x) for x in NUM_RE.findall(tail)]
            if len(nums) >= len(HORAS_VALIDAS): result[v] = nums[idx]
    return result


# ===========================================================================
# ARCON96 — CFD / TOTAL X/Q
# ===========================================================================
def _parse_cfd(cfd_path, hora):
    IDX = {1:1, 2:2, 4:3, 8:4, 12:6, 24:7, 96:8, 168:9, 360:10, 720:11}
    k = IDX[hora]
    try: raw = cfd_path.read_text(encoding="cp1252", errors="replace").splitlines()
    except Exception as e: logging.warning("Cannot read %s: %s", cfd_path, e); return []
    out = []
    for ln in raw:
        if any(s in ln for s in ("X/Q CUMULATIVE FREQUENCY","XOQ","Abv. Lim.","Belw. Lim.")): continue
        tokens = NUM_RE.findall(ln)
        if len(tokens) >= 12:
            try: out.append((tokens[0], float(tokens[k])))
            except ValueError: pass
    return out


def _interp_xoq(pairs, target):
    if len(pairs) < 2: return None
    for xoq, ac in pairs:
        if abs(ac - target) <= 5e-6: return xoq
    for i in range(len(pairs)-1):
        x1, a1 = pairs[i]; x2, a2 = pairs[i+1]
        if (a1 >= target >= a2) or (a2 >= target >= a1):
            d = a2 - a1
            return x1 + (target - a1) / d * (x2 - x1) if abs(d) > 1e-12 else x1
    return None


def _build_total_matrix(hora):
    if hora not in HORAS_VALIDAS: raise ValueError(f"Invalid hour {hora}")
    idx = HORAS_VALIDAS.index(hora)
    re_case = re.compile(r"^(X_\d{3}_V_\d+):\s*(.*)$")
    re_tag  = re.compile(r"X_(\d{3})_V_(\d+)")
    data = {}; all_v = set(); all_xxx = set()
    if not SALIDAS_LOG_SECTOR.exists(): return [], [], data
    lines = SALIDAS_LOG_SECTOR.read_text(encoding="utf-8", errors="replace").splitlines()
    i, n = 0, len(lines)
    while i < n:
        m = re_case.match(lines[i])
        if not m or "TOTAL X/Qs" not in m.group(2): i += 1; continue
        tag, content = m.group(1), m.group(2)
        pos = content.upper().find("TOTAL X/QS")
        nums = [float(x) for x in NUM_RE.findall(content[pos+10:])]
        if len(nums) < len(HORAS_VALIDAS) and i+1 < n:
            m2 = re_case.match(lines[i+1])
            if m2 and m2.group(1) == tag:
                n2 = [float(x) for x in NUM_RE.findall(m2.group(2))]
                if len(n2) >= len(HORAS_VALIDAS): nums = n2; i += 1
        if len(nums) < len(HORAS_VALIDAS): i += 1; continue
        mm = re_tag.match(tag)
        if not mm: i += 1; continue
        xxx, v = mm.group(1), mm.group(2)
        all_v.add(v); all_xxx.add(xxx)
        data.setdefault(v, {})[xxx] = max(nums[idx], data.get(v, {}).get(xxx, float("-inf")))
        i += 1
    return sorted(all_v, key=int), sorted(all_xxx, key=int), data


def _build_percent_maps(hora, targets):
    v_sorted, _, totals = _build_total_matrix(hora)
    perc_maps = {t: defaultdict(dict) for t in targets}
    groups = defaultdict(list)
    for d in CWD.iterdir():
        if d.is_dir():
            m = RE_CASE.match(d.name)
            if m: groups[m.group(2)].append((m.group(1), d))
    for v in sorted(groups, key=int):
        for xxx, dpath in sorted(groups[v], key=lambda t: int(t[0])):
            cfd = dpath / "ISMR.cfd"
            if not cfd.exists(): continue
            rows = _parse_cfd(cfd, hora)
            total = totals.get(v, {}).get(xxx)
            if not total or total <= 0: continue
            ac_pairs = []
            for tok, freq in rows:
                try:
                    xoq = float(tok)
                    ac = max(0.0, min(1.0, (total - freq) / total))
                    ac_pairs.append((xoq, ac))
                except ValueError: pass
            if ac_pairs:
                for t in targets:
                    xq = _interp_xoq(ac_pairs, t)
                    if xq is not None: perc_maps[t][v][xxx] = xq
    return v_sorted, perc_maps


# ===========================================================================
# ARCON96 — EXCEL BUILDING
# ===========================================================================
def _add_995_sheet(wb, sheet_name, v_sorted, pmap, hora, overall):
    ws = wb.create_sheet(title=sheet_name)
    xxx_s = sorted({x for v in v_sorted for x in pmap.get(v, {})}, key=int)
    headers = ["V"] + [f"X_{int(x):03d}" for x in xxx_s] + \
              ["Maximmum Sector", "Maximmum Overall", "Maximun"]
    bold = Font(bold=True); center = Alignment(horizontal="center")
    BLUE = "0000FF"; RED = "FF0000"
    for c, h in enumerate(headers, 1):
        cell = ws.cell(2, c, h); cell.font = bold; cell.alignment = center
    ws.column_dimensions["A"].width = 6
    for j in range(2, 2+len(xxx_s)):
        ws.column_dimensions[ws.cell(2,j).column_letter].width = 14
    for j in range(2+len(xxx_s), 2+len(xxx_s)+3):
        ws.column_dimensions[ws.cell(2,j).column_letter].width = 18
    for r, v in enumerate(v_sorted, 3):
        ws.cell(r, 1, int(v)).alignment = center
        row_vals = []
        for j, xxx in enumerate(xxx_s, 2):
            val = pmap.get(v, {}).get(xxx)
            if val is None: ws.cell(r, j, "NA").alignment = center
            else: ws.cell(r, j, val); row_vals.append((j, val))
        ms = 2+len(xxx_s); mo = ms+1; mx = ms+2
        if row_vals:
            mc, mv = max(row_vals, key=lambda t: t[1])
            ws.cell(r, mc).font = Font(color=BLUE)
            ws.cell(r, ms, mv).font = Font(color=BLUE)
        else:
            ws.cell(r, ms, "NA").alignment = center; mv = None
        ov = overall.get(v)
        ws.cell(r, mo, ov if ov is not None else "NA")
        if ov is None: ws.cell(r, mo).alignment = center
        if mv is not None and ov is not None: final = max(mv, ov)
        elif mv is not None: final = mv
        elif ov is not None: final = ov
        else: final = None
        if final is None: ws.cell(r, mx, "NA").alignment = center
        else: ws.cell(r, mx, final).font = Font(color=RED)
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(headers))
    tc = ws.cell(1, 1, f"99_5th PERCENTILE X/Q per sector (Acumm_Frecuency=0.9950, averaging hour={hora} h)")
    tc.font = Font(bold=True); tc.alignment = Alignment(horizontal="center")


def _build_xq_excel(xlsx_path, target=0.995):
    """Build the bridge Excel. Sheets named H1h…H720h (no H0h bug)."""
    wb = Workbook(); wb.remove(wb.active)
    for hora in HORAS_VALIDAS:
        vs, pmaps = _build_percent_maps(hora, [target])
        overall = _load_p95_by_v(PERCENTIL95_OVERALL, hora)
        _add_995_sheet(wb, f"H{hora}h", vs, pmaps.get(target, {}), hora, overall)
    wb.save(xlsx_path)
    logging.info("Bridge Excel saved: %s", xlsx_path)


def _build_total_excel(xlsx_path):
    wb = Workbook(); wb.remove(wb.active)
    bold = Font(bold=True); center = Alignment(horizontal="center")
    for hora in HORAS_VALIDAS:
        vs, xxx_s, data = _build_total_matrix(hora)
        ws = wb.create_sheet(title=f"TOTAL_{hora}h")
        ws.cell(1, 1, f"TOTAL X/Qs for averaging {hora} h").font = bold
        ws.cell(2, 1, "V").font = bold; ws.column_dimensions["A"].width = 6
        for j, xxx in enumerate(xxx_s, 2):
            c = ws.cell(2, j, f"X_{int(xxx):03d}"); c.font = bold; c.alignment = center
            ws.column_dimensions[c.column_letter].width = 14
        for r, v in enumerate(vs, 3):
            ws.cell(r, 1, int(v)).alignment = center
            for j, xxx in enumerate(xxx_s, 2):
                val = data.get(v, {}).get(xxx)
                ws.cell(r, j, float(val) if val is not None else "NA")
    wb.save(xlsx_path)
    logging.info("TOTAL X/Qs Excel saved: %s", xlsx_path)


def _export_max_txt(xlsx_path, txt_path):
    try: wb = load_workbook(xlsx_path, data_only=True)
    except Exception as e: logging.warning("Cannot open bridge Excel for TXT: %s", e); return
    dist_set = set()
    for sh in wb.sheetnames:
        ws = wb[sh]; r = 3
        while True:
            v = ws.cell(r, 1).value
            if v is None: break
            try: dist_set.add(f"{int(v):03d}")
            except: break
            r += 1
    if not dist_set: return
    v_sorted = sorted(dist_set, key=int)
    mapping = {}
    for sh in wb.sheetnames:
        ws = wb[sh]
        hdrs = [ws.cell(2, c).value for c in range(1, ws.max_column+1)]
        col_max = next(
            (i+1 for i, h in enumerate(hdrs)
             if isinstance(h, str) and h.strip().lower() in ("maximun", "maximmum")),
            ws.max_column
        )
        rm = {}; r = 3
        while True:
            v = ws.cell(r, 1).value
            if v is None: break
            try: rm[f"{int(v):03d}"] = ws.cell(r, col_max).value
            except: break
            r += 1
        mapping[sh] = rm
    with txt_path.open("w", encoding="utf-8") as f:
        f.write("X/Q Maximmun by hour\n")
        f.write("Distance".ljust(8))
        for h in HORAS_VALIDAS: f.write(f"{h:>14d}")
        f.write("\n")
        for v in v_sorted:
            f.write(f"{int(v):>8d}")
            for h in HORAS_VALIDAS:
                val = mapping.get(f"H{h}h", {}).get(v)
                if val is None or (isinstance(val, str) and val.strip().upper() == "NA"):
                    f.write(f"{'NA':>14s}")
                else:
                    try: f.write(f"{float(val):>14.6E}")
                    except: f.write(f"{'NA':>14s}")
            f.write("\n")
    logging.info("TXT max-by-hour: %s", txt_path)


def _extract_sector_maxima(log_path, out_path):
    if not log_path.exists(): return
    re_v     = re.compile(r"X_\d{3}_V_(\d+):")
    re_total = re.compile(r"TOTAL X/Qs[:=]?\s*(" + NUM_PAT + r")", re.IGNORECASE)
    maxes = {}
    with log_path.open("r", encoding="utf-8", errors="replace") as f:
        for ln in f:
            if "TOTAL X/Qs" not in ln: continue
            mv = re_v.search(ln)
            if not mv: continue
            v = mv.group(1); mt = re_total.search(ln)
            if mt:
                try: maxes[v] = max(float(mt.group(1)), maxes.get(v, float("-inf")))
                except: pass
    with out_path.open("w", encoding="utf-8") as f:
        for v in sorted(maxes, key=int): f.write(f"{v}: {maxes[v]}\n")


# ===========================================================================
# PSF / RADTRAD — BINARY HELPERS
# ===========================================================================
def _looks_pair(b):
    return bool(_PAIR_RE.match(b) or _PFALLBACK.search(b))

def _e11(v):
    return f"{float(v):.4E}".encode().rjust(11)

def _read_template(path):
    with open(path, "rb") as f: return f.read().splitlines(keepends=True)

def _locate_frac(lines):
    for i, l in enumerate(lines):
        if _FRAC_RE.search(l): return i
    return None

def _replace_frac(lines, idx, f1, f2, f3):
    old = lines[idx]; parts = old.split()
    indent = old[:old.index(parts[0])] if parts else b""
    nl = b"\r\n" if old.endswith(b"\r\n") else b"\n"
    lines[idx] = indent + _e11(f1) + b" " + _e11(f2) + b" " + _e11(f3) + b" " + _e11(1.0) + nl

def _find_loc_start(lines, title_b):
    for i, l in enumerate(lines):
        if l.strip() == title_b: return i
    return None

def _find_first_pair(lines, start):
    for j in range(start, len(lines)):
        if _looks_pair(lines[j]): return j
        st = lines[j].strip()
        if st.startswith(b"Location ") and j > start: break
        if st in (b"Effective Volume Location:", b"Simulation Parameters:", b"Output Filename:"): break
    return None

def _fill_location(lines, title, times, xqs):
    idx_loc  = _find_loc_start(lines, title.encode())
    if idx_loc is None: logging.warning("PSF block '%s' not found", title); return
    idx_pair = _find_first_pair(lines, idx_loc)
    if idx_pair is None: return
    idx_cnt = next((k for k in range(idx_pair-1, idx_loc-1, -1) if lines[k].strip().isdigit()), None)
    end = idx_pair
    while end < len(lines) and _PAIR_RE.match(lines[end]): end += 1
    ex = lines[idx_pair]; parts = ex.split()
    indent = ex[:ex.index(parts[0])] if parts else b""
    new_pairs = [indent + _e11(t) + b" " + _e11(q) + b"\r\n" for t, q in zip(times, xqs)]
    if idx_cnt is not None:
        cl = lines[idx_cnt]; ci = cl[:len(cl)-len(cl.lstrip(b" "))]
        cn = b"\r\n" if cl.endswith(b"\r\n") else b"\n"
        lines[idx_cnt] = ci + str(len(times)).encode() + cn
    lines[idx_pair:end] = new_pairs

def _replace_out_name(lines, name):
    for i, l in enumerate(lines):
        if l.strip() == b"Output Filename:" and i+1 < len(lines):
            ln = lines[i+1]; ind = ln[:len(ln)-len(ln.lstrip(b" "))]
            nl = b"\r\n" if ln.endswith(b"\r\n") else b"\n"
            lines[i+1] = ind + name.encode() + nl; return

def _replace_next_after(lines, label, text):
    for i, l in enumerate(lines):
        if l.strip() == label and i+1 < len(lines):
            ln = lines[i+1]; ind = ln[:len(ln)-len(ln.lstrip(b" "))]
            nl = b"\r\n" if ln.endswith(b"\r\n") else b"\n"
            lines[i+1] = ind + text.encode() + nl; return True
    return False

def _replace_first_match(lines, pattern, text):
    rex = re.compile(pattern)
    for i, ln in enumerate(lines):
        if rex.search(ln):
            ind = ln[:len(ln)-len(ln.lstrip(b" "))]
            nl = b"\r\n" if ln.endswith(b"\r\n") else b"\n"
            lines[i] = ind + text.encode() + nl; return True
    return False

def _patch_support(lines, rft, nif, inp):
    _replace_next_after(lines, b"Nuclide Inventory File:", f"defaults\\{nif}")
    _replace_first_match(lines, rb"\.inp(\s*$)", f"defaults\\{inp}")
    _replace_first_match(lines, rb"\.rft(\s*$)", f"defaults\\{rft}")


# ===========================================================================
# RADTRAD — X/Q READER FROM BRIDGE EXCEL
# ===========================================================================
def read_xq_series(excel_path, distance_m, times):
    """Read 'Maximun' column from H{t}h sheets for the given distance."""
    xqs = []
    for t in times:
        sheet = f"H{int(t)}h"
        df = pd.read_excel(excel_path, sheet_name=sheet, engine="openpyxl", header=1)
        df.columns = [str(c).strip() for c in df.columns]
        if "Maximun" not in df.columns: raise KeyError(f"'Maximun' not in {sheet}")
        df["_d"] = pd.to_numeric(df["V"], errors="coerce")
        match = df[df["_d"] == float(distance_m)]
        if match.empty:
            avail = ", ".join(str(int(v)) for v in df["_d"].dropna().astype(int).unique())
            raise ValueError(f"Distance {distance_m}m not in {sheet}. Available: {avail}")
        xqs.append(float(match.iloc[0]["Maximun"]))
    return xqs


# ===========================================================================
# RADTRAD — PSF BUILDER
# ===========================================================================
def build_psf(template_lines, distance_m, fracs, excel_path, support_names):
    lines = list(template_lines)
    f1, f2, f3 = fracs
    _patch_support(lines, *support_names)
    idx = _locate_frac(lines)
    if idx is not None: _replace_frac(lines, idx, f1, f2, f3)
    xqs = read_xq_series(excel_path, float(distance_m), EXPECTED_TIMES)
    _fill_location(lines, "Location 1:", EXPECTED_TIMES, xqs)
    _fill_location(lines, "Location 2:", EXPECTED_TIMES, xqs)
    _replace_out_name(lines, f"Test16_{distance_m}m.o0")
    return b"".join(lines)


# ===========================================================================
# RADTRAD — EXECUTION
# ===========================================================================
def run_radtrad(psf_path, exe, timeout=RADTRAD_TIMEOUT):
    log = psf_path.with_suffix(".run.log")
    out = psf_path.with_suffix(".o0").name
    cmd = [str(exe), "/b", psf_path.name, out]
    flags = 0x08000000 if os.name == "nt" else 0
    with log.open("wb") as fl:
        try:
            kw = {"creationflags": flags} if os.name == "nt" else {}
            res = subprocess.run(cmd, cwd=str(psf_path.parent),
                                 stdout=fl, stderr=fl, timeout=timeout, check=False, **kw)
        except Exception as e:
            fl.write(f"[ERROR] {e}".encode("cp1252", "ignore")); return 1
    return res.returncode


# ===========================================================================
# RADTRAD — O0 PARSERS
# ===========================================================================
def _is_num(t):
    try: float(t); return True
    except: return False

def _nums(ln):
    return [float(t) for t in ln.replace(",", " ").split() if _is_num(t)]

def parse_cumulative(text):
    empty = pd.DataFrame(columns=["receptor","time_h","TEDE_rem","Thyroid_rem"])
    if not text: return empty
    idx = text.lower().find("cumulative dose summary")
    if idx == -1: return empty
    tail = text[idx:].splitlines(); end = len(tail)
    for i, ln in enumerate(tail):
        ll = ln.strip().lower()
        if ("worst" in ll and "two" in ll and "hour" in ll) or \
           ("exclusion" in ll and "boundary" in ll):
            end = i; break
    rows = []
    for ln in tail[:end]:
        s = ln.strip()
        if not s or s[0] not in "0123456789+-.": continue
        nums = _nums(s)
        if len(nums) >= 7:
            t = nums[0]; eth, ete, lth, lte, cth, cte = nums[1:7]
            rows += [{"receptor":"EAB","time_h":t,"TEDE_rem":ete,"Thyroid_rem":eth},
                     {"receptor":"LPZ","time_h":t,"TEDE_rem":lte,"Thyroid_rem":lth},
                     {"receptor":"CR", "time_h":t,"TEDE_rem":cte,"Thyroid_rem":cth}]
    if not rows: return empty
    return pd.DataFrame(rows).sort_values(["receptor","time_h"]).reset_index(drop=True)

def _w2h_block(text):
    if not text: return None
    idx = text.lower().find("worst two-hour doses")
    if idx == -1: return None
    blk = []; started = False
    for ln in text[idx:].splitlines():
        ll = ln.strip().lower()
        if not started:
            if "exclusion area boundary" in ll: started = True; blk.append(ln)
            continue
        if any(ll.startswith(s) for s in (
            "exclusion area boundary doses:","low population zone doses:",
            "control room doses:","cumulative dose summary","worst two-hour doses",
        )) or (ln.strip().startswith("#") and len(ln.strip()) > 5): break
        blk.append(ln)
    res = "\n".join(blk).strip(); return res or None

def parse_worst_two_hour(text):
    blk = _w2h_block(text)
    if not blk: return None
    nre = r"[+-]?\d+(?:\.\d+)?(?:[Ee][+-]?\d+)?"
    for ln in [l.strip() for l in blk.splitlines() if l.strip()]:
        nums = re.findall(nre, ln)
        if len(nums) >= 4:
            t, wb, th, te = (float(x) for x in nums[:4])
            return {"time_2h": t, "wb_2h_rem": wb, "thyr_2h_rem": th, "tede_2h_rem": te}
    return None

def parse_eab_2h(text):
    if not text: return None
    idx = text.lower().find("exclusion area boundary doses:")
    if idx == -1: return None
    tail = text[idx:].splitlines()
    ti = next((i for i, ln in enumerate(tail[:200000])
               if "time" in ln.lower() and "(h)" in ln.lower() and "=" in ln and "2.0000" in ln), None)
    if ti is None: return None
    nre = r"[+-]?\d+(?:\.\d+)?(?:[Ee][+-]?\d+)?"
    wd = wa = td_ = ta = thd = tha = None
    for ln in tail[ti+1:ti+25]:
        ll = ln.lower().strip(); nums = re.findall(nre, ln)
        if "delta dose" in ll and len(nums) >= 3:
            wd, thd, td_ = float(nums[0]), float(nums[1]), float(nums[2])
        elif "accumulated dose" in ll and len(nums) >= 3:
            wa, tha, ta = float(nums[0]), float(nums[1]), float(nums[2])
        if None not in (wd, wa, td_, ta): break
    if all(x is None for x in (wd, wa, td_, ta)): return None
    return dict(wb_delta_2h_rem=wd, wb_accum_2h_rem=wa,
                th_delta_2h_rem=thd, th_accum_2h_rem=tha,
                te_delta_2h_rem=td_, te_accum_2h_rem=ta)


# ===========================================================================
# RADTRAD — SETS_WORST2H.XLSX
# ===========================================================================
def _safe_xlsx_path(path: Path) -> Path:
    """
    If the target .xlsx is locked (open in Excel), return an auto-renamed
    path like Sets_Worst2h_01.xlsx, _02.xlsx, etc. instead of crashing.
    """
    if not path.exists():
        return path
    try:
        # Quick write-access probe
        path.open("r+b").close()
        return path
    except PermissionError:
        stem = path.stem; suffix = path.suffix; parent = path.parent
        i = 1
        while True:
            candidate = parent / f"{stem}_{i:02d}{suffix}"
            if not candidate.exists():
                logging.warning(
                    "%s is open in another program — saving as %s instead.",
                    path.name, candidate.name
                )
                return candidate
            try:
                candidate.open("r+b").close()
                logging.warning(
                    "%s is open in another program — saving as %s instead.",
                    path.name, candidate.name
                )
                return candidate
            except PermissionError:
                i += 1


def write_sets_worst2h(out_xlsx, runs_index):
    out_xlsx.parent.mkdir(parents=True, exist_ok=True)
    out_xlsx = _safe_xlsx_path(out_xlsx)   # auto-rename if locked
    per_set = {}
    for r in runs_index:
        o0 = Path(r.get("o0_path", ""))
        if not o0.exists(): continue
        text = o0.read_text(encoding="cp1252", errors="ignore")
        w2h = parse_worst_two_hour(text); e2h = parse_eab_2h(text)
        if w2h is None and e2h is None: continue
        per_set.setdefault(r["set_id"], []).append({
            "distance_m":       int(r["distance_m"]),
            "Time_2h_h":        float(w2h["time_2h"]) if w2h else 2.0,
            "WB_Worst2h_mSv":   w2h["wb_2h_rem"]   * REM_TO_MSV if w2h and w2h.get("wb_2h_rem")   is not None else None,
            "TEDE_Worst2h_mSv": w2h["tede_2h_rem"] * REM_TO_MSV if w2h and w2h.get("tede_2h_rem") is not None else None,
            "WB_Delta_2h_mSv":  e2h["wb_delta_2h_rem"] * REM_TO_MSV if e2h and e2h.get("wb_delta_2h_rem") is not None else None,
            "WB_Accum_2h_mSv":  e2h["wb_accum_2h_rem"] * REM_TO_MSV if e2h and e2h.get("wb_accum_2h_rem") is not None else None,
        })
    if not per_set: logging.warning("Sets_Worst2h: no data"); return

    with pd.ExcelWriter(out_xlsx, engine="openpyxl") as w:
        # Summary
        sumrows = []
        for sid, rows in per_set.items():
            meta = out_xlsx.parent.parent / f"frac_set_{int(sid):02d}" / "set_meta.json"
            fI2 = fC = fA = None
            if meta.exists():
                try:
                    m = json.loads(meta.read_text(encoding="utf-8"))
                    fI2 = m.get("frac_I2"); fC = m.get("frac_CH3I"); fA = m.get("frac_AER")
                except: pass
            tv = [r["TEDE_Worst2h_mSv"] for r in rows if r.get("TEDE_Worst2h_mSv") is not None]
            mt = max(tv) if tv else None
            md = next((r["distance_m"] for r in rows if r.get("TEDE_Worst2h_mSv") == mt), None)
            sumrows.append({"Set": f"Set{int(sid):02d}",
                            "frac_AER":fA,"frac_I2":fI2,"frac_CH3I":fC,
                            "Max_TEDE_Worst2h_mSv":mt,"At_distance_m":md})
        if sumrows:
            pd.DataFrame(sumrows).sort_values("Set").to_excel(w, sheet_name="Summary", index=False)
        # Per-set
        COLS = ["distance_m","Time_2h_h","WB_Worst2h_mSv","TEDE_Worst2h_mSv",
                "WB_Delta_2h_mSv","WB_Accum_2h_mSv"]
        for sid, rows in per_set.items():
            df = pd.DataFrame(rows).sort_values("distance_m")
            for c in COLS:
                if c not in df.columns: df[c] = None
            df[COLS].to_excel(w, sheet_name=f"Set{int(sid):02d}", index=False)
        # EAB sheets
        per_eab = defaultdict(list)
        for r in runs_index: per_eab[r["set_id"]].append(r)
        for sid, runs in per_eab.items():
            erows = []
            for r in runs:
                o0 = Path(r["o0_path"])
                if not o0.exists(): continue
                e = parse_eab_2h(o0.read_text(encoding="cp1252", errors="ignore"))
                if not e: continue
                erows.append({"distance_m": int(r["distance_m"]),
                    "WB_Delta_2h_mSv":   e["wb_delta_2h_rem"] * REM_TO_MSV if e.get("wb_delta_2h_rem") is not None else None,
                    "WB_Accum_2h_mSv":   e["wb_accum_2h_rem"] * REM_TO_MSV if e.get("wb_accum_2h_rem") is not None else None,
                    "TEDE_Delta_2h_mSv": e["te_delta_2h_rem"] * REM_TO_MSV if e.get("te_delta_2h_rem") is not None else None,
                    "TEDE_Accum_2h_mSv": e["te_accum_2h_rem"] * REM_TO_MSV if e.get("te_accum_2h_rem") is not None else None,
                })
            if erows:
                pd.DataFrame(erows).sort_values("distance_m").to_excel(
                    w, sheet_name=f"EAB_2h_Set{int(sid):02d}", index=False)

    # Highlight max TEDE
    try:
        wb2 = load_workbook(out_xlsx)
        if "Summary" in wb2.sheetnames:
            order = ["Summary"] + [s for s in wb2.sheetnames if s != "Summary"]
            for i, name in enumerate(order): wb2.move_sheet(name, offset=i - wb2.sheetnames.index(name))
        YELLOW_FILL = PatternFill(start_color="FFF7D14D", end_color="FFF7D14D", fill_type="solid")
        for ws in wb2.worksheets:
            hdr = {cell.value: i+1 for i, cell in enumerate(ws[1])}
            col_name = "Max_TEDE_Worst2h_mSv" if ws.title == "Summary" else "TEDE_Worst2h_mSv"
            if col_name not in hdr: continue
            col = hdr[col_name]
            vals = [(r, ws.cell(r, col).value) for r in range(2, ws.max_row+1)
                    if isinstance(ws.cell(r, col).value, (int, float))]
            if not vals: continue
            mr = max(vals, key=lambda x: x[1])[0]
            ws.cell(mr, col).fill = YELLOW_FILL
            ws.cell(mr, col).font = Font(bold=True)
        try:
            wb2.save(out_xlsx)
        except PermissionError:
            alt = _safe_xlsx_path(out_xlsx)
            wb2.save(alt)
            logging.warning("Saved highlighted version as %s (original locked)", alt.name)
            out_xlsx = alt
    except Exception as e:
        logging.warning("Could not highlight Worst2h maxima: %s", e)

    logging.info("Sets_Worst2h.xlsx written: %s", out_xlsx)


# ===========================================================================
# RADTRAD — OUTPUT ROOT MANAGEMENT & DEFAULTS COPY
# ===========================================================================
def _manage_out_root(path):
    if not path.exists(): return
    print(f"\n  Output folder already exists: {path}")
    print("  1=DELETE  2=RENAME  3=KEEP")
    c = input("  Choose (ENTER=3): ").strip() or "3"
    if c == "1": shutil.rmtree(path, ignore_errors=True)
    elif c == "2":
        i = 1; new = Path(f"{path}_old_{i:02d}")
        while new.exists(): i += 1; new = Path(f"{path}_old_{i:02d}")
        path.rename(new); print(f"  Renamed → {new}")

def _copy_defaults(target_dir):
    src = SCRIPT_DIR / "Defaults"
    if src.exists() and src.is_dir(): copy_tree(str(src), str(target_dir / "Defaults"))
    else: logging.warning("Defaults folder not found: %s", src)


# ===========================================================================
# MAIN
# ===========================================================================
BANNER = """
╔══════════════════════════════════════════════════════════╗
║      ARCON96 + RADTRAD  —  UNIFIED PIPELINE              ║
║      Author : Gilberto Villescas Díaz  (IDOM)  2025      ║
╠══════════════════════════════════════════════════════════╣
║  PHASE 1  ARCON96   batch runs  →  Bridge Excel          ║
║  PHASE 2  RADTRAD   PSF + run   →  .o0 outputs           ║
║  PHASE 3  Post-proc             →  Sets_Worst2h.xlsx     ║
╚══════════════════════════════════════════════════════════╝
"""

def main():
    print(BANNER)
    setup_logging()

    # ── ALL PARAMETERS UP FRONT ─────────────────────────────
    p = ask_all_params()
    num_met       = p["num_met"]
    dist_min      = p["dist_min"]
    dist_max      = p["dist_max"]
    delta         = p["delta"]
    template_path = p["template_path"]
    nsets         = p["nsets"]
    fixed_sets    = p["fixed_sets"]
    support_names = p["support_names"]
    radtrad_exe   = p["radtrad_exe"]
    out_root      = p["out_root"]
    no_run        = p["no_run"]
    distances     = list(range(dist_min, dist_max + 1, delta))

    # ── PRE-FLIGHT ───────────────────────────────────────────
    logging.info("Pre-flight checks...")
    errors = []
    if not ARCON_EXE.exists():
        errors.append(f"ARCON96 executable not found: {ARCON_EXE}")
    missing_mets = [f"MET{i:02d}.MET" for i in range(1, num_met+1)
                    if not (MET_BASE / f"MET{i:02d}.MET").exists()]
    if missing_mets:
        errors.append(f"Missing MET files: {', '.join(missing_mets)}")
    if not template_path.exists():
        errors.append(f"PSF template not found: {template_path}")
    if not no_run and not radtrad_exe.exists():
        errors.append(f"RADTRAD executable not found: {radtrad_exe}")
    if errors:
        for e in errors: logging.error("  %s", e)
        return 2

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # PHASE 1 — ARCON96
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    logging.info("=" * 62)
    logging.info("PHASE 1  —  ARCON96  (%d distances, 17 cases each)", len(distances))
    logging.info("=" * 62)

    # Ensure ARCON output directory exists
    CWD.mkdir(exist_ok=True)
    logging.info("ARCON96 directory: %s", CWD)

    _clean_arcon_dirs()
    for f in [SALIDA_LOG_OVERALL, INTERVALOS_OVERALL, SALIDAS_LOG_SECTOR,
              INTERVALOS_SECTOR, MAXIMO_SECTOR, TOTAL_XQ_COLUMNAS,
              PERCENTIL95_OVERALL, FRECUENCIAS_SECTOR]:
        _safe_rm(f)

    # 1a — OVERALL
    logging.info("  1a) OVERALL runs")
    _write_p95_header(PERCENTIL95_OVERALL)
    for v in distances:
        _run_case(f"{v:03d}_{v:02d}", _gen_rsf(num_met, v),
                  SALIDA_LOG_OVERALL, INTERVALOS_OVERALL,
                  ARCON_EXE, MET_BASE, num_met, p95_path=PERCENTIL95_OVERALL)

    # 1b — SECTOR
    logging.info("  1b) SECTOR runs  (16 sectors × %d distances)", len(distances))
    xxx_values = np.round(np.linspace(22.5, 360, 16)).astype(int)
    for xxx in xxx_values:
        for v in distances:
            _run_case(f"X_{xxx:03d}_V_{v:03d}", _gen_rsf(num_met, v, xxx),
                      SALIDAS_LOG_SECTOR, INTERVALOS_SECTOR,
                      ARCON_EXE, MET_BASE, num_met, p95_path=None)

    # 1c — Build bridge Excel and auxiliary outputs
    logging.info("  1c) Building bridge Excel and auxiliary outputs")
    _extract_sector_maxima(SALIDAS_LOG_SECTOR, MAXIMO_SECTOR)
    _build_xq_excel(XQ_EXCEL)           # ← Bridge: used directly by Phase 2
    _build_total_excel(TOTAL_XQ_EXCEL)
    _export_max_txt(XQ_EXCEL, XQ_MAX_TXT)
    logging.info("  Bridge Excel ready: %s", XQ_EXCEL.name)

    # Ask user whether to delete ARCON96 run directories
    _ask_delete_arcon_dirs()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # PHASE 2 — RADTRAD
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    logging.info("=" * 62)
    logging.info("PHASE 2  —  RADTRAD  (%d sets × %d distances)", nsets, len(distances))
    logging.info("=" * 62)

    _manage_out_root(out_root)
    out_root.mkdir(parents=True, exist_ok=True)
    template_lines = _read_template(template_path)
    acc_csv = out_root / "postprocess" / "post_timeseries_accum.csv"
    runs_index: List[Dict] = []

    random.seed(None); np.random.seed(None)

    for k in range(1, nsets + 1):
        if fixed_sets[k-1] is not None:
            f1, f2, f3 = fixed_sets[k-1]; src_lbl = "fixed"
        else:
            f1, f2, f3 = np.random.dirichlet([1, 1, 1]); src_lbl = "random"
        logging.info("  [SET %02d] %s  AER=%.4f  I2=%.4f  CH3I=%.4f", k, src_lbl, f1, f2, f3)

        set_dir = out_root / f"frac_set_{k:02d}"; set_dir.mkdir(parents=True, exist_ok=True)
        (set_dir / "set_meta.json").write_text(json.dumps({
            "set_id":k, "frac_AER":f1, "frac_I2":f2, "frac_CH3I":f3, "source":src_lbl,
            "frac_AER (Aerosoles)":f1, "frac_I2 (Elemental)":f2, "frac_CH3I (Organico)":f3,
        }, indent=2), encoding="utf-8")

        for d in distances:
            dist_dir = set_dir / f"{d}_m"; dist_dir.mkdir(exist_ok=True)
            _copy_defaults(dist_dir)
            try:
                psf_bytes = build_psf(template_lines, d, (f1, f2, f3), XQ_EXCEL, support_names)
            except Exception as e:
                logging.error("  PSF build failed set=%d d=%d: %s", k, d, e); continue

            psf_path = dist_dir / f"Test16_{d}m.psf"
            psf_path.write_bytes(psf_bytes)
            logging.info("    PSF: %s", psf_path.name)

            rc = None
            if not no_run:
                rc = run_radtrad(psf_path, radtrad_exe)
                if rc == 0: logging.info("    RADTRAD OK  → %s", psf_path.stem)
                else:       logging.error("    RADTRAD rc=%d → %s", rc, psf_path.stem)

            if rc == 0 or no_run:
                o0 = psf_path.with_suffix(".o0")
                if o0.exists():
                    text = o0.read_text(encoding="cp1252", errors="ignore")
                    df_case = parse_cumulative(text)
                    if not df_case.empty:
                        df_case["distance_m"] = d; df_case["set_id"] = k
                        df_case["TEDE_uSv"]    = df_case["TEDE_rem"]    * FACTOR_USV
                        df_case["Thyroid_uSv"] = df_case["Thyroid_rem"] * FACTOR_USV
                        acc_csv.parent.mkdir(parents=True, exist_ok=True)
                        hdr = not acc_csv.exists()
                        with acc_csv.open("a", newline="", encoding="utf-8") as ff:
                            writer = csv.writer(ff)
                            if hdr: writer.writerow(df_case.columns)
                            for _, row in df_case.iterrows():
                                writer.writerow([row[c] for c in df_case.columns])

            runs_index.append({
                "distance_m": d, "set_id": k,
                "psf_path": str(psf_path),
                "o0_path":  str(psf_path.with_suffix(".o0")),
                "rc": rc if rc is not None else (-1 if no_run else None),
            })

    logging.info("PHASE 2 complete%s.", " (PSFs only)" if no_run else "")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # PHASE 3 — POST-PROCESS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    logging.info("=" * 62)
    logging.info("PHASE 3  —  Post-processing → Sets_Worst2h.xlsx")
    logging.info("=" * 62)

    worst2h_out = out_root / "postprocess" / "Sets_Worst2h.xlsx"
    write_sets_worst2h(worst2h_out, runs_index)

    logging.info("=" * 62)
    logging.info("PIPELINE COMPLETE")
    logging.info("  Bridge Excel  : %s", XQ_EXCEL.name)
    logging.info("  RADTRAD root  : %s", out_root.resolve())
    logging.info("  Sets_Worst2h  : %s", worst2h_out.name)
    logging.info("=" * 62)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
