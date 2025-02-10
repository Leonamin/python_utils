import openpyxl

def delete_rows_by_value(file_path, sheet_name, column_letter, target_value):
    # 엑셀 파일 열기
    wb = openpyxl.load_workbook(file_path)
    ws = wb[sheet_name]

    # 열의 인덱스를 가져오기 (A=1, B=2 ...)
    col_index = openpyxl.utils.column_index_from_string(column_letter)

    # 삭제할 행 찾기 (역순으로 처리하여 인덱스 문제 방지)
    rows_to_delete = [
        row[0].row for row in ws.iter_rows(min_col=col_index, max_col=col_index) 
        # 포함인경우
        if row[0].value and target_value in row[0].value
        # 같은경우
        # if row[0].value == target_value
        # 뒷자리가 같은경우
        # if row[0].value and str(row[0].value).strip().endswith(target_value)
    ]

    # 행 삭제 (뒤에서부터 삭제해야 인덱스 변경 문제 방지)
    for row_idx in reversed(rows_to_delete):
        ws.delete_rows(row_idx)

    # 수정된 엑셀 저장
    wb.save(file_path)
    wb.close()

if __name__ == "__main__":

    
    file_path = "input.xlsx"  # 엑셀 파일 경로
    sheet_name = input("시트 이름을 입력하세요: ")
    column_letter = input("검사할 열을 입력하세요: ")
    target_value = input("삭제할 값을 입력하세요: ")
    
    print(f"파일 경로: {file_path}")
    print(f"시트 이름: {sheet_name}")
    print(f"검사할 열: {column_letter}")
    print(f"삭제할 값: {target_value}")
    
    print("입력한 내용이 맞다면 y, 아니면 n을 입력하세요.")
    answer = input()
    if answer == "y":
        delete_rows_by_value(file_path, sheet_name, column_letter, target_value)
        print("삭제 완료")
    else:
        print("프로그램을 종료합니다.")