import pandas as pd


def parse_visit_schedule(filepath: str):
    """엑셀 파일에서 방문별 일지 수를 파싱하는 함수

    Args:
        filepath (str): 엑셀 파일 경로

    Returns:
        tuple: (v2, v3, v4) 각 방문별 일지 수를 담은 dict
    """
    # 엑셀 불러오기
    excel_file = pd.ExcelFile(filepath)
    df = pd.read_excel(excel_file, sheet_name="방문")

    # 헤더 및 불필요한 행 제거
    df_cleaned = df.iloc[0:].reset_index(drop=True)
    df_cleaned.columns = df_cleaned.iloc[0]
    df_cleaned = df_cleaned.drop(0).reset_index(drop=True)

    # 인덱스를 기준으로 파싱
    v2, v3, v4 = {}, {}, {}
    for _, row in df_cleaned.iterrows():
        try:
            # 방문2
            subject_id_v2 = row.iloc[1]
            diary_count_v2 = row.iloc[8]
            if pd.notna(subject_id_v2) and pd.notna(diary_count_v2):
                v2[subject_id_v2] = int(diary_count_v2)

            # 방문3
            subject_id_v3 = row.iloc[10]
            diary_count_v3 = row.iloc[17]
            if pd.notna(subject_id_v3) and pd.notna(diary_count_v3):
                v3[subject_id_v3] = int(diary_count_v3)

            # 방문4
            subject_id_v4 = row.iloc[19]
            diary_count_v4 = row.iloc[26]
            if pd.notna(subject_id_v4) and pd.notna(diary_count_v4):
                v4[subject_id_v4] = int(diary_count_v4)
        except Exception as e:
            print(f"Row parsing error: {e}")

    return v2, v3, v4


if __name__ == "__main__":
    v2, v3, v4 = parse_visit_schedule("visit_schedule.xlsx")
    # print(v2)
    print(v3)
    # print(v4)
    print(v2['01-S002'])
