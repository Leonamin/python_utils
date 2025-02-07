import os
from dotenv import load_dotenv
import requests


def extract_address_parts(address: str) -> tuple[str, str]:
    # 첫 번째 콤마 기준으로 도로명 주소와 상세 주소 분리
    split_address = address.split(',', 1)
    road_address = split_address[0].strip()
    detail_address = split_address[1].strip()
    return road_address, detail_address


def find_zip_code(road_address: str) -> str:
    """
    도로명 주소(road_address)를 이용해 Kakao Local API에서 우편번호(zone_no)를 가져옵니다.
    """
    # .env 혹은 시스템 환경 변수에서 REST API 키를 가져옵니다.
    api_key = os.environ.get("REST_API_KEY")
    if not api_key:
        raise ValueError("REST_API_KEY 환경변수가 설정되어 있지 않습니다.")

    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {
        "Authorization": f"KakaoAK {api_key}"
    }
    # analyze_type을 exact로 지정하면 입력 주소와 정확히 일치하는 결과를 우선 반환하도록 할 수 있습니다.
    params = {
        "query": road_address,
        "analyze_type": "exact"
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        raise Exception(f"Kakao API 요청 실패: {
                        response.status_code}, {response.text}")

    data = response.json()
    documents = data.get("documents", [])

    # 응답된 각 문서에서 road_address의 address_name이 입력한 도로명 주소와 일치하는지 확인합니다.
    for doc in documents:
        road_addr_info = doc.get("road_address")
        if road_addr_info and road_addr_info.get("address_name") == road_address:
            return road_addr_info.get("zone_no")

    # 만약 정확한 일치가 없으면 첫 번째 결과의 우편번호를 반환하도록 할 수 있습니다.
    if documents:
        road_addr_info = documents[0].get("road_address")
        if road_addr_info:
            return road_addr_info.get("zone_no")

    print(f"해당 도로명 주소에 대한 우편번호를 찾지 못했습니다. : {road_address}")
    return ''


if __name__ == "__main__":
    load_dotenv()
    # 예시 주소
    address = "서울특별시 강남구 테헤란로 513, (삼성동, B1일부,4,9,10층,테헤란로81길10,B1일부,삼성로92길29,3,4)"

    # 도로명 주소와 상세 주소 분리
    road_address, detail_address = extract_address_parts(address)
    print("도로명 주소:", road_address)
    print("상세 주소:", detail_address)

    try:
        # 도로명 주소로 우편번호 조회
        zip_code = find_zip_code(road_address)
        print("우편번호:", zip_code)
    except Exception as e:
        print("우편번호 조회 중 오류 발생:", e)
