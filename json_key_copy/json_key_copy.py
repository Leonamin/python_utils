import json

# from의 JSON 파일을 to의 JSON 파일에 덮어씌운다.


def update_json(from_file, to_file, skip_string):
    # JSON 파일에서 데이터를 읽어온다.
    with open(from_file, 'r') as f:
        from_json = json.load(f)

    with open(to_file, 'r') as f:
        to_json = json.load(f)

    # from_json의 값을 to_json에 덮어씌운다.
    for key, value in from_json.items():
        # 특정 문자열이 키에 포함된 경우 건너뛴다.
        if not (include_string in key):
            continue
        # 키가 to_json에도 있으면 덮어씌운다.
        if key in to_json:
            to_json[key] = value

    # 업데이트된 to_json을 다시 파일에 저장한다.
    with open(to_file, 'w') as f:
        json.dump(to_json, f, indent=4, ensure_ascii=False)

    print(f"Updated JSON has been written to {to_file}")


# 파일 이름 예시
# from_file = input("Enter the name of the JSON file to copy from: ")
# to_file = input("Enter the name of the JSON file to copy to: ")
from_file = "new_ar.arb"
to_file = "intl_ar.arb"

# 포함되어야할 문자열
include_string = ""

# 업데이트 함수 호출
update_json(from_file, to_file, include_string)
