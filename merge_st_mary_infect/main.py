import os
import pandas as pd

base_path = 'st_mary_infect'
file_order = ['info', 'form_answer', 'phr_records', 'task_achieve']

# 열 이름 중복 방지용 함수


def deduplicate_columns(columns):
    seen = {}
    result = []
    for col in columns:
        if col not in seen:
            seen[col] = 1
            result.append(col)
        else:
            seen[col] += 1
            result.append(f"{col}_{seen[col]}")
    return result


# 최종 결과 리스트
final_df_list = []

# 대상 폴더 정렬
folders = sorted([f for f in os.listdir(base_path)
                 if os.path.isdir(os.path.join(base_path, f))])

for folder in folders:
    folder_path = os.path.join(base_path, folder)
    prefix = folder.split('_')[0]

    dfs = []

    for key in file_order:
        filename = f'user_{prefix}_{key}.csv'
        filepath = os.path.join(folder_path, filename)
        if os.path.exists(filepath):
            df = pd.read_csv(filepath)
            dfs.append(df)
        else:
            print(f'파일 없음: {filepath}')

    if dfs:
        # 열 방향 병합 후 중복 열 이름 처리
        combined = pd.concat(dfs, axis=1)
        combined.columns = deduplicate_columns(combined.columns)
        final_df_list.append(combined)

# 전체 폴더 데이터를 행 방향으로 병합
result_df = pd.concat(final_df_list, axis=0, ignore_index=True)

# 결과 저장
result_df.to_excel('st_mary_infect_combined.xlsx', index=False)
print("완료: st_mary_infect_combined.xlsx")
