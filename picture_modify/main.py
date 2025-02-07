from PIL import Image
import os

def resize_image_by_ratio(input_path, output_path, ratio):
    """
    이미지를 지정한 비율로 크기 조정합니다.
    - input_path: 원본 이미지 경로
    - output_path: 출력 이미지 경로
    - ratio: 크기 조정 비율 (0 ~ 1)
    """
    with Image.open(input_path) as img:
        # 원본 크기 가져오기
        original_width, original_height = img.size

        # 비율에 따른 새로운 크기 계산
        new_width = int(original_width * ratio)
        new_height = int(original_height * ratio)

        # 이미지 리사이즈 (LANCZOS 필터 사용)
        resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # 결과 저장 (PNG로 저장)
        resized_img.save(output_path, format="PNG")
        print(f"Resized: {input_path} -> {output_path} ({new_width}x{new_height})")

def process_folder_by_ratio(input_folder, output_folder, ratio):
    """
    폴더 내 모든 이미지를 지정한 비율로 리사이즈합니다.
    - input_folder: 입력 폴더 경로
    - output_folder: 출력 폴더 경로
    - ratio: 크기 조정 비율 (0 ~ 1)
    """
    os.makedirs(output_folder, exist_ok=True)
    for root, _, files in os.walk(input_folder):
        for file in files:
            if file.lower().endswith('.png'):
                input_path = os.path.join(root, file)
                relative_path = os.path.relpath(input_path, input_folder)
                output_path = os.path.join(output_folder, relative_path)
                os.makedirs(os.path.dirname(output_path), exist_ok=True)

                # 이미지 크기 조정
                resize_image_by_ratio(input_path, output_path, ratio)

# 설정
input_folder = "input_images"  # 원본 이미지 폴더 경로
output_folder = "output_images"  # 결과 저장 폴더 경로
resize_ratio = 0.34  # 크기 조정 비율 (0 ~ 1, 예: 0.5는 50%)

# 실행
process_folder_by_ratio(input_folder, output_folder, resize_ratio)
