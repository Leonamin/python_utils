from PyPDF2 import PdfMerger
from PyPDF2 import PdfReader
from PyPDF2 import PdfWriter


def unlock_pdf(input_pdf_path, output_pdf_path, password):
    # PDF 파일 열기
    with open(input_pdf_path, 'rb') as input_pdf:
        reader = PdfReader(input_pdf)

        # 비밀번호 확인 및 해제
        if reader.is_encrypted:
            reader.decrypt(password)

            writer = PdfWriter()
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                writer.add_page(page)

            # 새로운 PDF 파일 저장
            with open(output_pdf_path, 'wb') as output_pdf:
                writer.write(output_pdf)
            print(f"PDF 파일의 비밀번호가 해제되어 '{output_pdf_path}'에 저장되었어요. 냐옹~")
        else:
            print("PDF 파일에 비밀번호가 설정되어 있지 않아요. 냐옹~")


# 사용 예제
# input_pdf_path = input("PDF 파일 경로를 입력해주세요:")
input_pdf_path = '동원훈련소집통지서.pdf'
output_pdf_path = input_pdf_path + '_unlocked.pdf'
password = '20010810'

# password = input("비밀번호를 입력해주세요: ")

unlock_pdf(input_pdf_path, output_pdf_path, password)
