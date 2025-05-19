"""edc_generator
설문 미실시인 경우 관련 데이터 미입력
"""

import argparse
import pathlib
import datetime as dt
import re
from typing import List, Iterable
import pandas as pd

from visit_parser import parse_visit_schedule


class LineData():
    """
    행 데이터 클래스
    """

    def __init__(self, subj_id: str, visit: str, day: str, code: str, data: str):
        self.subj_id = subj_id
        self.visit = visit
        self.day = day
        self.code = code
        self.data = data

    def make_line(self) -> str:
        return f"NVP-1704-2|CARESQUARE|{self.subj_id}|{self.visit}|{self.day}|{self.code}|{self.data}|"

# ----------------------- 전역 설정 ---------------------------------------- #


ROW_LIMIT = {"V2": 20, "V3": 40, "V4": 40}
MISSING_DEFAULT = "0"  # --missing-empty 플래그로 "" 로 변경 가능

DATE_PAT = re.compile(r"(\d{4})\D+(\d{1,2})\D+(\d{1,2})")

# V2일지의 모든 시작 일자는 빈 값이며 D1부터 수집을 하기 때문에 7번이 아닌 8번으로 진행
DATA_START_ROW = 7

NEXT_PAGE_COL = 15

VISIT3_SCHEDULE: dict[str, int] = {}
VISIT4_SCHEDULE: dict[str, int] = {}

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


'''
예외처리 용도 함수
'''


def remove_invalid_time(val: str) -> str:
    # val: 오후 11:10, 오전 6:00 등
    prefix = val[:2]
    time_str = val[3:]
    hour, minute = time_str.split(":")
    if prefix == "오후":
        hour = str(int(hour) + 12)
    time_str = f"{hour}:{minute}"
    return time_str


def is_invalid_time(val: str) -> bool:
    if len(val) > 9:
        return False
    if val.startswith("오후") or val.startswith("오전"):
        return True
    return False


def format_result(val, kind: str, part: str | None, missing_empty: bool) -> str:
    if type(val) == str and is_invalid_time(val):
        val = remove_invalid_time(val)

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


def yyyyMMddToDash(val: str) -> str:
    return val[:4] + "-" + val[4:6] + "-" + val[6:]


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


def parse_question(
    key: str,
    row: pd.Series,
    col_off: int,
    visit: str,
    subj_id: str,
    visit_date: str,
    missing_empty: bool,
    has_drink: bool,
    day: int,
) -> LineData:
    base = BASE_MAP[key]
    col_idx = int(key) if isinstance(key, float) else key
    val = row[col_off + col_idx]

    # 음주 관련 데이터 미입력
    if base["code"] in {"SD18RE", "SD20RE"} and not has_drink:
        return None

    res = format_result(
        val, base["kind"], base["part"], missing_empty)

    full_code = f"{visit}{base['code']}{pad(day, 2)}"

    return LineData(subj_id, visit, visit_date, full_code, res)


def build_subject(df: pd.DataFrame, col_off: int, missing_empty: bool) -> List[LineData]:
    # col_off: 행에서 기준이 되는 열의 Offset 대상자 마다 다름 일반적으로 대상자 순서 * 15
    subj_id = str(df.iat[0, col_off + 2]).strip()
    if subj_id in {"nan", ""}:
        return []

    reg_date = parse_kr_date(df.iat[2, col_off + 2])

    MAX_V3 = VISIT3_SCHEDULE.get(subj_id)
    if MAX_V3 is None:
        print(subj_id)
        return []

    lines: List[str] = []

    visit_type = "V3"

    for ridx, row in df.iloc[DATA_START_ROW:].iterrows():
        rule_cell = row[col_off]
        if pd.isna(rule_cell):
            break

        day = 0

        rule_i = int(rule_cell)

        visit_date = visit_day(reg_date, rule_i)

        if rule_i > MAX_V3:
            visit_type = "V4"
            day = rule_i - MAX_V3
        else:
            day = rule_i

        # 미실시 여부
        not_done = str(row[col_off + 1]).strip() == "-"
        nd_code = f"{visit_type}SDND{pad(day, 2)}"

        data_q1 = "1" if not_done else "0"

        lines.append(LineData(subj_id, visit_type,
                     visit_date, nd_code, data_q1))
        if not_done:
            continue

        # ------------------------------ 검사일 ------------------------------ #

        data_q2 = yyyyMMddToDash(visit_date)
        d_code = f"{visit_type}SDDTC{pad(day, 2)}"
        lines.append(LineData(subj_id, visit_type,
                     visit_date, d_code, data_q2))

        # ------------------------------ 데이터 파싱 ------------------------------ #

        drink_flag = str(row[col_off + 11]).strip()
        has_drink = drink_flag == "1"

        # Q1 ~ Q14 데이터 파싱

        for key in SEQ_COLS:
            line = parse_question(
                key, row, col_off, visit_type, subj_id, visit_date, missing_empty, has_drink, day)
            if line:
                lines.append(line)

    return lines

# -------------------- workbook 처리 --------------------------------------- #


def convert_workbook(path: str, split: bool, missing_empty: bool):
    wb = pd.read_excel(path, sheet_name=None, header=None, engine="openpyxl")
    all_lines: List[LineData] = []

    for _, df in wb.items():
        col = 0
        while col < df.shape[1]:
            lines = build_subject(df, col, missing_empty)
            if lines:
                all_lines.extend(lines)

            col += NEXT_PAGE_COL

    if not split and all_lines:
        make_output(all_lines, "V3", path)
        make_output(all_lines, "V4", path)


def make_output(all_lines: List[LineData], visit_type: str, path: str):
    output_path = pathlib.Path(path).with_suffix(
        "").parent / f"NVP-1704-2_{visit_type}_{dt.date.today().strftime('%Y%m%d')}.txt"
    with open(output_path, "w") as f:
        for line in all_lines:
            if line.visit == visit_type:
                f.write(line.make_line() + "\n")

# -------------------- CLI -------------------------------------------------- #


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("excel", help="input workbook (.xlsx)")
    ap.add_argument("--split", action="store_true",
                    help="피험자+Visit 별 txt 분리 저장")
    ap.add_argument("--missing-empty", action="store_true",
                    help="빈 값은 \"\" 로 기록 (기본 0)")
    args = ap.parse_args()

    global VISIT3_SCHEDULE, VISIT4_SCHEDULE

    _, VISIT3_SCHEDULE, VISIT4_SCHEDULE = parse_visit_schedule(
        'visit_schedule.xlsx')

    convert_workbook(args.excel, args.split, args.missing_empty)


if __name__ == "__main__":
    main()
