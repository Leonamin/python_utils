"""edc_generator.py  v0.2
===========================
Convert CARESQUARE sleep‑diary Excel file → cubeCDMS external‑data text file.

Changes (0.2)
-------------
* **Time string support** – cells like ``00:00`` are now split into hour/minute so
  Q1/Q2/Q6… 항목 처리 시 `ValueError` 발생하지 않음.
* **Robust formatter** – `format_result()` accepts ``'-'``/NaN/empty, numeric,
  and ``HH:MM``. Returns (value, missing_flag).
* **Mapping dict re‑organised** – each question code holds
  `{col, codes, kind, part}` where ``part`` is ``'hh'`` / ``'mm'`` / ``None``.
* **CLI** –   ``--visit V2`` & ``--split`` 그대로.

Usage
-----
```bash
pip install pandas openpyxl
python edc_generator.py workbook.xlsx --visit V2            # 한 파일 출력
python edc_generator.py workbook.xlsx --visit V2 --split    # 피험자별 분리
```

"""

import argparse
import pathlib
import datetime as dt
import re
from typing import List
import pandas as pd

# ------------------------------ helpers ------------------------------------ #

# V2, V3, V4 타입에 따라 데이터 갯수 제한 데이터가 50개라 하더라도 데이터 행 개수 제한에 따라 설정
row_limit = {
    'V2': 17,
    'V3': 35,
    'V4': 35,
}


DATE_PAT = re.compile(r"(\d{4})\D+(\d{1,2})\D+(\d{1,2})")


def parse_kr_date(text: str) -> dt.date:
    # 투약규칙 형식 파싱: "2023년 10월 5일 (목)" → date(2023, 10, 5).
    parsed = DATE_PAT.search(str(text))
    if not parsed:
        raise ValueError(f"Unrecognised date format: {text}")
    y, m, d = map(int, parsed.groups())
    return dt.date(y, m, d)


def pad(num: int, width: int) -> str:
    # Zeropad *positive* integer to given width.
    return f"{num:0{width}d}"


def format_result(val, kind: str, part: str | None) -> tuple[str, bool]:
    """Return (포맷팅된 값, 빈칸 여부).``kind`` is N1/N2/N3/C10/C255."""
    if pd.isna(val) or val == "" or val == "-":
        return "", True

    s = str(val).strip()

    # TIME "HH:MM" → split
    if ":" in s:
        hh, mm = [x.zfill(2) for x in s.split(":", 1)]
        s = hh if part == "hh" else mm

    if kind.startswith("N"):
        width = int(kind[1])  # N1, N2, N3
        return pad(int(float(s)), width), False
    elif kind.startswith("C"):
        return s[: int(kind[1:])], False
    else:
        raise ValueError(f"Unsupported kind: {kind}")


def visit_day(reg_date: dt.date, rule: int) -> str:
    """YYYYMMDD for reg_date + rule(days)."""
    d = reg_date + dt.timedelta(days=int(rule))
    return d.strftime("%Y%m%d")

# --------------------------- mapping table --------------------------------- #


# QUESTION COL → list[ dict(col,qcode,kind,part) ]
BASE_MAP_V2 = {
    1: [  # Q1 HH:MM
        {"code": "RE", "kind": "N2", "part": "hh"},
        {"code": "REMI", "kind": "N2", "part": "mm"},
    ],
    2: [
        {"code": "RE", "kind": "N2", "part": "hh"},
        {"code": "REMI", "kind": "N2", "part": "mm"},
    ],
    3: [{"code": "RE", "kind": "N3", "part": None}],
    4: [{"code": "RE", "kind": "N1", "part": None}],
    5: [{"code": "RE", "kind": "N3", "part": None}],
    6: [
        {"code": "RE", "kind": "N2", "part": "hh"},
        {"code": "REMI", "kind": "N2", "part": "mm"},
    ],
    7: [
        {"code": "RE", "kind": "N2", "part": "hh"},
        {"code": "REMI", "kind": "N2", "part": "mm"},
    ],
    8: [{"code": "RE", "kind": "N1", "part": None}],
    9: [
        {"code": "RE", "kind": "N1", "part": None},
    ],
    10: [{"code": "RE", "kind": "N3", "part": None}],
    11: [{"code": "RE", "kind": "N1", "part": None}],
    12: [{"code": "REMI", "kind": "N3", "part": None}],
    13: [{"code": "RE", "kind": "C255", "part": None}],
    14: [{"code": "RE", "kind": "N1", "part": None}],
    15: [{"code": "RE", "kind": "N3", "part": None}],
}

# ---------------------- 헤더 정보 추출 ---------------------------------- #
# 피험자 아이디, 검사일


def extract_header(df: pd.DataFrame) -> tuple[str, dt.date]:
    subj_id = str(df.iat[0, 2]).strip()
    reg_date = parse_kr_date(df.iat[2, 2])
    return subj_id, reg_date

# --------------------- core per‑subject processing ------------------------- #


def process_subject(df: pd.DataFrame, visit: str) -> List[str]:
    """Return list of pipe‑delimited lines for a single subject sheet."""

    subj_id, reg_date = extract_header(df)

    header = ["NVP-1704-2", "CARESQUARE", subj_id, visit]
    lines: List[str] = []

    count = 0

    for idx, row in df.iloc[7:].iterrows():  # 8th row → 데이터
        if (count >= row_limit[visit]):
            break
        count += 1
        try:
            rule = int(row[0])  # 투약규칙
            visit_date = visit_day(reg_date, rule)

            # No1 – 미실시 여부 0: 실시 1: 미실시
            if str(row[1]).strip() == "-":
                code = f"{visit}SDND{pad(rule, 2)}"
                lines.append("|".join(header + [visit_date, code, "1", ""]))
                continue
            else:
                code = f"{visit}SDND{pad(rule, 2)}"
                lines.append("|".join(header + [visit_date, code, "0", ""]))

            # No2 - 검사일
            code = f"{visit}SDDTC{pad(rule, 2)}"
            lines.append("|".join(header + [visit_date, code, visit_date, ""]))

            # No3-1 ~ No15-2
            for qcol, mappings in BASE_MAP_V2.items():
                val = row[qcol]
                for m in mappings:
                    full_code = f"{visit}SD{pad(qcol, 2)}{m['code']}{pad(rule, 2)}"
                    res, miss = format_result(val, m["kind"], m["part"])

                    # 비어있으면 데이터 추가를 하지 않음
                    if miss:
                        continue
                    lines.append(
                        "|".join(header + [visit_date, full_code, res, ""]))
        except ValueError:
            print(row)
            continue

    return lines

# -------------------- workbook orchestrator & CLI ------------------------- #


def convert_workbook(path: str, visit: str, split: bool):
    wb = pd.read_excel(path, sheet_name=None, header=None, engine="openpyxl")
    out_root = pathlib.Path(path).with_suffix("")
    all_lines: List[str] = []

    for name, sheet in wb.items():
        # lines = process_subject(sheet, visit)
        # if split:
        #     outf = out_root.parent / f"{name}.txt"
        #     outf.write_text("\n".join(lines), encoding="utf-8")
        # all_lines.extend(lines)

        v2_lines = process_subject(sheet, 'V2')
        v3_lines = process_subject(sheet, 'V3')
        v4_lines = process_subject(sheet, 'V4')
        if split:
            outf = out_root.parent / f"{name}_V2.txt"
            outf.write_text("\n".join(v2_lines), encoding="utf-8")
            outf = out_root.parent / f"{name}_V3.txt"
            outf.write_text("\n".join(v3_lines), encoding="utf-8")
            outf = out_root.parent / f"{name}_V4.txt"
            outf.write_text("\n".join(v4_lines), encoding="utf-8")
        all_lines.extend(v2_lines)
        all_lines.extend(v3_lines)
        all_lines.extend(v4_lines)

    if not split:
        today = dt.date.today().strftime("%Y%m%d")
        (out_root.parent /
         f"NVP-1704-2_{today}.txt").write_text("\n".join(all_lines), encoding="utf-8")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("excel", help="input workbook (.xlsx)")
    p.add_argument("--visit", default="V2",
                   choices=["V2", "V3", "V4"], help="visit id")
    p.add_argument("--split", action="store_true",
                   help="output per‑subject files")
    args = p.parse_args()
    convert_workbook(args.excel, visit=args.visit, split=args.split)


if __name__ == "__main__":
    main()
