"""
EDC External Data upload text file generator
===========================================
Converts the customised *subject‑wide* Excel layout used by CARESQUARE for
protocol **NVP‑1704‑2** into the pipe‑delimited text format accepted by
cubeCDMS “external data uploader”.

✔ One Excel → one or many .txt outputs (global or subject‑split)
✔ Header rows (1‑5) are parsed for metadata (subject ID, visit group, dates…) 
✔ Data rows (Q1‑Q14) are expanded to 3 records per CRF as required by the
  *External Data Specification* (see `PARAMETER_DEFINITION` below).
✔ Functions are kept small & testable so you can adapt the rules easily.

Usage (command line)
--------------------
```
python edc_generator.py NVP-1704-2-R_surveys.xlsx               # single file
python edc_generator.py NVP-1704-2-R_surveys.xlsx --split  # one .txt per subject
```
The script needs **pandas** and **openpyxl** (both widely available).

ENVIRONMENTS  • Python ≥3.8  • Windows / macOS / Linux
"""
from __future__ import annotations
import argparse
import pathlib
from datetime import datetime, timedelta
from typing import List, Dict

import pandas as pd

# ---------------------------------------------------------------------------
# Constants & mapping tables
# ---------------------------------------------------------------------------
PROJECT  = "NVP-1704-2"
LAB      = "CARESQUARE"
VISIT_ID = "V2"      # for V3 / V4 change here or pass --visit

# Map questionnaire column index (relative to the 15‑wide subject slice)
# to (parameter No., code stem, result formatter function)
# The PDF “Parameter Definition” (turn0file0) was used as the source.  citeturn0file0

PARAMETER_DEFINITION: Dict[str, Dict[str, str]] = {
    # Q‑index : {"no": CRF No., "stem": code stem, "type": data‑type}
    1: {"no": "3-1",  "stem": "01RE",     "type": "h2"},
    2: {"no": "3-2",  "stem": "01REMI",  "type": "m2"},
    3: {"no": "4-1",  "stem": "02RE",     "type": "h2"},
    4: {"no": "4-2",  "stem": "02REMI",  "type": "m2"},
    5: {"no": "5",    "stem": "03RE",     "type": "m3"},
    6: {"no": "6",    "stem": "05RE",     "type": "h2"},
    7: {"no": "7",    "stem": "06RE",     "type": "m3"},
    8: {"no": "8-1",  "stem": "07RE",     "type": "h2"},
    9: {"no": "8-2",  "stem": "07REMI",  "type": "m2"},
    10:{"no": "9-1",  "stem": "08RE",     "type": "h2"},
    11:{"no": "9-2",  "stem": "08REMI",  "type": "m2"},
    12:{"no": "10",   "stem": "10RE",     "type": "d1"},
    13:{"no": "11-1", "stem": "11RE",     "type": "d1"},
    14:{"no": "11-2", "stem": "11REMI",  "type": "m3"},
    15:{"no": "12",   "stem": "12RE",     "type": "str"},
    16:{"no": "13",   "stem": "17RE",     "type": "d1"},
    17:{"no": "14",   "stem": "18RE",     "type": "m3"},
    18:{"no": "15-1", "stem": "19RE",     "type": "d1"},
    19:{"no": "15-2", "stem": "20RE",     "type": "m3"},
}

DATA_START_ROW = 7          # 0‑based index (row 8 in Excel)
COLS_PER_SUBJ  = 15

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def parse_header(subj_df: pd.DataFrame) -> dict:
    """Extract subject metadata from rows 1‑5 (indices 0‑4)."""
    sid          = str(subj_df.iat[0, 2]).strip()
    dose_rule    = int(str(subj_df.iat[1, 10]).rstrip("번"))
    reg_date_raw = str(subj_df.iat[2, 2]).split("(")[0].strip()
    reg_date     = datetime.strptime(reg_date_raw, "%Y년 %m월 %d일")
    return {
        "subject_id": sid,
        "dose_rule":  dose_rule,
        "reg_date":   reg_date,
    }


def pad(value: int, width: int) -> str:
    return str(value).zfill(width)


def format_result(val, rtype: str):
    if pd.isna(val) or val == "-":
        return "", True  # missing flag used elsewhere
    if rtype == "h2":   # hour two‑digit
        return pad(int(val), 2), False
    if rtype == "m2":   # minute two‑digit
        return pad(int(val), 2), False
    if rtype == "m3":   # minute three‑digit / generic 3‑digit
        return pad(int(val), 3), False
    if rtype == "d1":   # single digit 0‑9
        return str(int(val)), False
    if rtype == "str":  # free text
        return str(val), False
    raise ValueError(f"Unknown result type {rtype}")


def build_code(day_idx: int, stem: str, visit: str = VISIT_ID) -> str:
    return f"{visit}SD{stem}{pad(day_idx,2)}"


def make_line(study: str, lab: str, subj: str, visit: str, sample_date: str,
              code: str, result: str) -> str:
    return "|".join([study, lab, subj, visit, sample_date, code, result]) + "|"

# ---------------------------------------------------------------------------
# Core conversion logic per subject
# ---------------------------------------------------------------------------

def process_subject(subj_df: pd.DataFrame, visit: str = VISIT_ID) -> List[str]:
    meta = parse_header(subj_df)
    lines: List[str] = []

    for ridx in range(DATA_START_ROW, subj_df.shape[0]):
        row = subj_df.iloc[ridx]
        if row.isna().all():
            break  # reached blank trailing rows
        day_idx = ridx - DATA_START_ROW + 1

        # --- No₁: 미실시 flag (0 실시, 1 미실시) ---
        q1 = row[0]
        not_done = (q1 == "-")
        code_nd = build_code(day_idx, "ND")
        lines.append(make_line(PROJECT, LAB, meta["subject_id"], visit,
                               "", code_nd, "1" if not_done else "0"))
        if not_done:
            continue  # skip rest questions for this day

        # --- No₂: 검사일 (registration + dose_rule + day‑1) ---
        sample_date_dt = meta["reg_date"] + timedelta(days=day_idx)
        sample_date = sample_date_dt.strftime("%Y%m%d")
        code_date = build_code(day_idx, "DTC")
        lines.append(make_line(PROJECT, LAB, meta["subject_id"], visit,
                               sample_date, code_date, sample_date))

        # --- Remaining questionnaire answers (PARAMETER_DEFINITION) ---
        for qcol, mapping in PARAMETER_DEFINITION.items():
            # Excel: Q1 starts at col0, so qcol‑1 offset
            val = row[qcol - 1]
            result, miss = format_result(val, mapping["type"]) if qcol != 1 else format_result(q1, mapping["type"])
            if miss:
                continue  # spec: missing answers are simply skipped
            code = build_code(day_idx, mapping["stem"])
            lines.append(make_line(PROJECT, LAB, meta["subject_id"], visit,
                                   sample_date, code, result))
    return lines

# ---------------------------------------------------------------------------
# Workbook‑level orchestrator
# ---------------------------------------------------------------------------

def convert_workbook(path: pathlib.Path, visit: str = VISIT_ID,
                     split: bool = False) -> None:
    df = pd.read_excel(path, header=None, engine="openpyxl")
    out_root = path.with_suffix("")

    col = 0
    all_lines: List[str] = []
    file_counter = 0
    while col < df.shape[1]:
        if pd.isna(df.iat[0, col]):
            break  # no more subjects
        subj_df = df.iloc[:, col:col + COLS_PER_SUBJ]
        subject_lines = process_subject(subj_df, visit)
        if split:
            sid = parse_header(subj_df)["subject_id"].replace("/", "-")
            out_path = out_root.parent / f"{sid}.txt"
            out_path.write_text("\n".join(subject_lines), encoding="utf-8")
            file_counter += 1
        else:
            all_lines.extend(subject_lines)
        col += COLS_PER_SUBJ

    if not split:
        out_path = out_root.with_suffix(".txt")
        out_path.write_text("\n".join(all_lines), encoding="utf-8")
        print(f"Generated {out_path} with {len(all_lines)} lines.")
    else:
        print(f"Generated {file_counter} subject files.")

# ---------------------------------------------------------------------------
# CLI entry‑point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Generate cubeCDMS external data text file from CARESQUARE Excel export")
    parser.add_argument("excel", type=pathlib.Path, help="Input .xlsx file")
    parser.add_argument("--visit", default=VISIT_ID, help="Visit ID (V2/V3/V4)…")
    parser.add_argument("--split", action="store_true", help="Output one .txt per subject instead of single file")
    args = parser.parse_args()

    convert_workbook(args.excel, visit=args.visit, split=args.split)

if __name__ == "__main__":
    main()
