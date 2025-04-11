import os
import shutil
from collections import defaultdict

# 경로 설정
base_dirs = ['cohort A', 'cohort B', 'cohort C']
output_dir = 'output'

# 중복 확인용 dict
folder_map = defaultdict(list)

# 1. 모든 하위 폴더 수집
for base in base_dirs:
    if not os.path.exists(base):
        continue
    for item in os.listdir(base):
        full_path = os.path.join(base, item)
        if os.path.isdir(full_path):
            folder_map[item].append((base, full_path))

# 2. 중복 출력 및 이동 처리
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

for folder_name, locations in folder_map.items():
    if len(locations) > 1:
        print(f"중복 발견: {folder_name}")
        for base, _ in locations:
            print(f" - {base} 에 존재")
    # 첫 번째 폴더만 이동
    base, path = locations[0]
    dst = os.path.join(output_dir, folder_name)
    if not os.path.exists(dst):
        shutil.copytree(path, dst)
