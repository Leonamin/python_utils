"""edc_generator.py  v0.6
=================================
CARESQUARE 수면일지 Excel → cubeCDMS 외부데이터 텍스트 파일

변경 내역 (0.6)
----------------
* **--visit 파라미터** 추가
  * `--visit V2` → V2만 생성
  * `--visit V3` → V3만 생성
  * `--visit V4` → V4만 생성
  * 인자를 생략하면 V2·V3·V4 **모두** 출력(이전 동작 그대로)
* 내부 루프를 `selected_visits` 리스트로 단순화.
"""

import argparse
import pathlib
import datetime as dt
import re
from typing import List, Iterable
import pandas as pd

# ----------------------- 전역 설정 ---------------------------------------- #

ROW_LIMIT = {"V2": 17, "V3": 35, "V4": 35}
MISSING_DEFAULT = "0"  # --missing-empty 플래그로 "" 로 변경 가능

DATE_PAT = re.compile(r"(\d{4})\D+(\d{1,2})\D+(\d{1,2})")

# ----------------------------- util --------------------------------------- #


def parse_kr_date(text: str) -> dt.date:
    m = DATE_PAT.search(str(text))
    if not m:
        raise ValueError(f"Unrecognised date format: {text}")
    y, mth, d = map(int, m.groups())
    return dt.date(y, mth, d)


def pad(num: int, width: int) -> str:
    return f"{num:0{width}d}"


def visit_day(reg_date: dt.date, rule: int) -> str:
    return (reg_date + dt.timedelta(days=int(rule))).strftime("%Y%m%d")


def format_result(val, kind: str, part: str | None, missing_empty: bool) -> str:
    if pd.isna(val) or val == "" or val == "-":
        return "" if missing_empty else MISSING_DEFAULT
    s = str(val).strip()
    if ":" in s:  # HH:MM
        hh, mm = [x.zfill(2) for x in s.split(":", 1)]
        s = hh if part == "hh" else mm
    if kind.startswith("N"):
        return pad(int(float(s)), int(kind[1]))
    elif kind.startswith("C"):
        return s[: int(kind[1:])]
    else:
        raise ValueError(kind)


# ------------------- 매핑 테이블 ----------------------------------------- #
# key = (column offset within 1~14, optional .1 for 분)
BASE_MAP = {
    1:   {"code": "SD01RE", "kind": "N2", "part": "hh"},
    1.1: {"code": "SD01REMI", "kind": "N2", "part": "mm"},
    2:   {"code": "SD02RE", "kind": "N2", "part": "hh"},
    2.1: {"code": "SD02REMI", "kind": "N2", "part": "mm"},
    3:   {"code": "SD03RE", "kind": "N3", "part": None},
    4:   {"code": "SD05RE", "kind": "N1", "part": None},
    5:   {"code": "SD06RE", "kind": "N3", "part": None},
    6:   {"code": "SD07RE", "kind": "N2", "part": "hh"},
    6.1: {"code": "SD07REMI", "kind": "N2", "part": "mm"},
    7:   {"code": "SD08RE", "kind": "N2", "part": "hh"},
    7.1: {"code": "SD08REMI", "kind": "N2", "part": "mm"},
    8:   {"code": "SD10RE", "kind": "N1", "part": None},
    9:   {"code": "SD11RE", "kind": "N1", "part": None},
    10:  {"code": "SD11REMI", "kind": "N3", "part": None},
    11:  {"code": "SD17RE", "kind": "N1", "part": None},
    12:  {"code": "SD18RE", "kind": "N3", "part": None},
    13:  {"code": "SD20RE", "kind": "N3", "part": None},
    14:  {"code": "SD12RE", "kind": "C255", "part": None},
}

SEQ_COLS = [
    1, 1.1, 2, 2.1, 3, 4, 5, 6, 6.1, 7, 7.1,
    8, 9, 10, 11, 12, 13, 14,
]

# --------------------- subject‑level 처리 ---------------------------------- #


def build_subject(df: pd.DataFrame, col_off: int, visit: str, missing_empty: bool) -> List[str]:
    subj_id = str(df.iat[0, col_off + 2]).strip()
    if subj_id in {"nan", ""}:
        return []
    reg_date = parse_kr_date(df.iat[2, col_off + 2])

    header_common = ["NVP-1704-2", "CARESQUARE", subj_id, visit]
    lines: List[str] = []
    max_rows = ROW_LIMIT[visit]

    for ridx, row in df.iloc[7:].iterrows():
        rule_cell = row[col_off]
        if pd.isna(rule_cell):
            break
        if ridx - 7 >= max_rows:
            break
        rule_i = int(rule_cell)
        visit_date = visit_day(reg_date, rule_i)

        # 미실시 여부
        not_done = str(row[col_off + 1]).strip() == "-"
        nd_code = f"{visit}SDND{pad(rule_i, 2)}"
        lines.append("|".join(header_common +
                     [visit_date, nd_code, "1" if not_done else "0", ""]))
        if not_done:
            continue

        # 검사일
        d_code = f"{visit}SDDTC{pad(rule_i, 2)}"
        lines.append("|".join(header_common +
                     [visit_date, d_code, visit_date, ""]))

        drink_flag = str(row[col_off + 11]).strip()

        for key in SEQ_COLS:
            base = BASE_MAP[key]
            col_idx = int(key) if isinstance(key, float) else key
            val = row[col_off + col_idx]
            if base["code"] in {"SD18RE", "SD20RE"} and drink_flag != "1":
                res = "" if missing_empty else MISSING_DEFAULT
            else:
                res = format_result(
                    val, base["kind"], base["part"], missing_empty)
            full_code = f"{visit}{base['code']}{pad(rule_i, 2)}"
            lines.append("|".join(header_common +
                         [visit_date, full_code, res, ""]))

    return lines

# -------------------- workbook 처리 --------------------------------------- #


def iter_visits(option: str | None) -> Iterable[str]:
    if option:
        return (option,)
    return ("V2", "V3", "V4")


def convert_workbook(path: str, selected_visit: str | None, split: bool, missing_empty: bool):
    wb = pd.read_excel(path, sheet_name=None, header=None, engine="openpyxl")
    all_lines: List[str] = []

    visits = tuple(iter_visits(selected_visit))

    for _, df in wb.items():
        col = 0
        while col < df.shape[1]:
            for visit in visits:
                lines = build_subject(df, col, visit, missing_empty)
                if lines:
                    all_lines.extend(lines)
                    if split:
                        subj_id = str(df.iat[0, col + 2]).strip()
                        outp = pathlib.Path(path).with_suffix(
                            "").parent / f"{subj_id}_{visit}.txt"
                        outp.write_text("\n".join(lines), encoding="utf-8")
            col += 15

    if not split and all_lines:
        outf = pathlib.Path(path).with_suffix(
            "").parent / f"NVP-1704-2_{dt.date.today().strftime('%Y%m%d')}.txt"
        outf.write_text("\n".join(all_lines), encoding="utf-8")

# -------------------- CLI -------------------------------------------------- #


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("excel", help="input workbook (.xlsx)")
    ap.add_argument(
        "--visit", choices=["V2", "V3", "V4"], help="특정 Visit 만 출력")
    ap.add_argument("--split", action="store_true",
                    help="피험자+Visit 별 txt 분리 저장")
    ap.add_argument("--missing-empty", action="store_true",
                    help="빈 값은 \"\" 로 기록 (기본 0)")
    args = ap.parse_args()
    convert_workbook(args.excel, args.visit, args.split, args.missing_empty)


if __name__ == "__main__":
    main()
