import time
from dotenv import load_dotenv
import pandas as pd

from extract_address_parts import find_zip_code, extract_address_parts


# ✅ 주소에서 도로명 주소, 상세 주소 추출 함수

def extract_address_parts(address):
    if pd.isna(address):  # 주소가 비어있는 경우
        return address, ""

    # 주소 분리 (첫 번째 ',' 기준)
    parts = address.split(',', 1)
    road_address = parts[0].strip()  # 도로명 주소
    detail_address = parts[1].strip() if len(parts) > 1 else ""  # 상세 주소

    return road_address, detail_address

# ✅ 주소에서 첫 번째 단어 추출 후 비교


def check_city(address):
    if pd.isna(address) or not isinstance(address, str):
        return False  # 주소가 비어있으면 False 처리
    first_word = address.split()[0]  # 공백 기준 첫 번째 단어 추출
    return first_word in target_cities  # target_cities에 포함된 경우 True 반환


if __name__ == "__main__":
    load_dotenv()
# 엑셀 파일 로드
    file_path = "input.xlsx"  # 업로드된 엑셀 파일 경로
    df = pd.read_excel(file_path)

    # ✅ 필터링할 도시 리스트 설정
    target_cities = ["부산광역시", "대구광역시"]

    # ✅ target_cities 리스트 중 하나라도 주소에 포함된 경우 필터링
    filtered_df = df[df["주소"].astype(str).apply(check_city)].copy()

    filtered_df = filtered_df.reset_index(drop=True)

    if filtered_df.empty:
        print("❗ 필터링된 데이터가 없습니다. target_cities 리스트를 확인하세요.")
        exit()
    # ✅ 변환된 데이터프레임 생성
    new_df = pd.DataFrame()

    # 의원명 출력 테스트
    print("\n=== 필터링된 의원명 목록 ===")
    # print(filtered_df["의원명"])
    for index, row in filtered_df.iterrows():
        print(f"{index} : {row['의원명']}")
    print("========================\n")

    new_df["순번"] = range(1, len(filtered_df) + 1)
    new_df["수취인"] = filtered_df["의원명"]
    new_df["주소1"], new_df["상세주소"] = zip(
        *filtered_df["주소"].apply(extract_address_parts))
    new_df["연락처"] = filtered_df["전화번호"]

    # ✅ for 문을 사용하여 우편번호 추가

    # zip_codes = []
    # for idx, road_address in enumerate(new_df["주소1"]):
    #     print(f"🔍 {idx+1}/{len(new_df)}: {road_address} - 우편번호 조회 중...")
    #     zip_code = find_zip_code(road_address)
    #     zip_codes.append(zip_code)
    #     # time.sleep(0.5)  # API 요청 간격을 두어 제한 방지

    # new_df["우편번호"] = zip_codes

    # ✅ 변환된 데이터를 엑셀 파일로 저장
    output_path = "output.xlsx"
    new_df.to_excel(output_path, index=False)
