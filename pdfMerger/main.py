import os
from PyPDF2 import PdfMerger

def merge_pdfs(input_folder, output_file):
    # PDF 병합기 초기화
    merger = PdfMerger()
    
    # input 폴더 내의 파일들을 이름순으로 정렬
    pdf_files = sorted(
        [f for f in os.listdir(input_folder) if f.endswith('.pdf')],
        key=lambda x: x.lower()  # 대소문자 구분 없이 정렬
    )
    
    # PDF 파일 병합
    for pdf_file in pdf_files:
        pdf_path = os.path.join(input_folder, pdf_file)
        print(f"Adding {pdf_path} to the merged PDF.")
        merger.append(pdf_path)
    
    # 병합된 PDF 저장
    merger.write(output_file)
    merger.close()
    print(f"Merged PDF saved as {output_file}")

# 실행 예시
input_folder = "input"  # PDF 파일들이 있는 폴더
output_file = "merged_output.pdf"  # 병합된 PDF 저장 경로

# 함수 실행
merge_pdfs(input_folder, output_file)
