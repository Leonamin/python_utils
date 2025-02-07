import os
import pyperclip

def format_file_names(folder_path):
    try:
        # 폴더 내 모든 파일 이름 가져오기
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        files.sort()  # 파일 이름 정렬

        formatted_names = []
        for file in files:
            # 확장자를 제거
            name_without_extension = os.path.splitext(file)[0]

            # 마지막 '_' 기준으로 분리
            if '_' in name_without_extension:
                formatted_name = name_without_extension.split('_')[-1]
                formatted_names.append(formatted_name)
            else:
                # '_'가 없으면 전체 파일 이름을 사용
                formatted_names.append(name_without_extension)

        # 줄바꿈으로 연결하여 클립보드에 복사
        formatted_output = "\n".join(formatted_names)
        pyperclip.copy(formatted_output)

        print("파일 이름이 포맷팅되어 클립보드에 복사되었습니다. 스프레드시트에 붙여넣으세요.")
    except Exception as e:
        print(f"오류 발생: {e}")

# 실행 부분
if __name__ == "__main__":
    folder_path = input("파일 이름을 읽을 폴더 경로를 입력하세요: ").strip()
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        format_file_names(folder_path)
    else:
        print("유효한 폴더 경로를 입력하세요.")
