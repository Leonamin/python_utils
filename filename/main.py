import os
import pyperclip

def copy_file_names_to_clipboard(folder_path):
    try:
        # 폴더 내 모든 파일 이름 가져오기
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        files.sort()  # 파일 이름 정렬

        # 파일 이름 리스트를 문자열로 변환 (줄바꿈으로 구분)
        file_names = "\n".join(files)

        # 클립보드에 복사
        pyperclip.copy(file_names)
        print("파일 이름이 클립보드에 복사되었습니다. 스프레드시트에 붙여넣으세요.")
    except Exception as e:
        print(f"오류 발생: {e}")

# 실행 부분
if __name__ == "__main__":
    folder_path = input("파일 이름을 읽을 폴더 경로를 입력하세요: ").strip()
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        copy_file_names_to_clipboard(folder_path)
    else:
        print("유효한 폴더 경로를 입력하세요.")

