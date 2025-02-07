import csv
import re
from youtube_transcript_api import YouTubeTranscriptApi


from g4f.client import Client

summary = '''
지금부터 너는 경로원에서 어르신께 친절하게 설명하는 봉사원이야. 주어진 영상들은 만성질환관리(고혈압, 당뇨병) 환자분들께 전달될 일상생활습관 개선, 운동, 식습관 관련 영상들의 자막 텍스트야. 아래의 조건에 맞게 내용을 요약해줘. 

조건: 
- 핵심 정보만 남기기: 건강 주제와 관련이 없는 내용은 모두 제외해줘. 
- 오탈자 및 띄어쓰기 수정: 문법적 오류나 오탈자는 모두 올바르게 수정하고, 자연스럽고 매끄러운 문장으로 고쳐줘. 
- 단락 구분 및 제목 작성: 건강과 관련된 주제로 3~5개의 단락으로 나누어줘. 
각 단락을 대표할 수 있는 큰 제목을 붙여줘. 
- 어르신에게 친절하게 설명: 어르신이 쉽게 이해하실 수 있도록 문장은 최대한 3문장 이내로, 공손하고 친절한 어조로 작성해줘. 
- 쉬운 표현 사용: 어려운 용어나 기술적인 표현은 피하고, 어르신들이 쉽게 이해하실 수 있는 일상적인 말로  바꿔줘. 
- 핵심 강조: 중요한 정보를 놓치지 않도록, 각 단락의 핵심 포인트를 명확히 전달해줘.

텍스트:

'''


def get_summary(full_transcript):
    # Connect to the ChatGPT API
    try:
        client = Client()
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": f"{
                summary}: {full_transcript}"}],
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def extract_video_id(url):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})(?=\?|&|$)", url)
    if match:
        return match.group(1)
    return None


def get_full_transcript(video_id):
    try:
        # Fetching the transcript
        transcript_list = YouTubeTranscriptApi.get_transcript(
            video_id, languages=['ko'])
        full_transcript = " ".join([t['text'] for t in transcript_list])
        return full_transcript
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


if __name__ == "__main__":
    input_file_name = 'youtube_links.csv'
    output_file_name = f'{input_file_name.split(".")[0]}_output.csv'

    try:
        # 파일 읽기 및 수정
        with open(input_file_name, mode='r', encoding='utf-8') as input_file, \
                open(output_file_name, mode='w', encoding='utf-8', newline='') as output_file:
            reader = csv.reader(input_file)
            writer = csv.writer(output_file)

            for row in reader:
                # A열 값 추출
                value = row[0]
                # row 길이 확장
                while len(row) < 4:
                    row.append("")

                # 빈 문자열인지 확인
                if value == "":
                    continue

                # 비디오 ID 추출
                video_id = extract_video_id(value)

                print(f"Video Id: {video_id}")

                if video_id is None:
                    writer.writerow(row)
                    continue

                row[1] = video_id

                # 비디오 ID로 전체 트랜스크립트 가져오기
                full_transcript = get_full_transcript(video_id)

                if full_transcript is None:
                    writer.writerow(row)
                    continue

                print("Full Transcript: " + full_transcript)
                row[2] = full_transcript

                writer.writerow(row)

    except Exception as e:
        print(f"An error occurred: {e}")
