# --- START OF FILE gemini_quiz.py ---

import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()


def setup_gemini():
    """Gemini API 키를 설정합니다."""
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY가 .env 파일에 설정되지 않았습니다.")
        genai.configure(api_key=api_key)
        print("Gemini API가 성공적으로 설정되었습니다.")
    except Exception as e:
        print(f"Gemini 설정 중 오류 발생: {e}")
        exit()


def generate_quiz(category):
    """지정된 카테고리에 대한 단답형 퀴즈를 생성합니다."""
    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = f"""
    '{category}' 분야에 대한 한국어 단답형 퀴즈를 1개 만들어줘. 
    정답은 명사 또는 짧은 구(phrase) 형태여야 해.
    반드시 아래와 같은 JSON 형식으로만 답변해줘. 다른 설명은 추가하지 마.

    {{
        "question": "퀴즈 질문",
        "answer": "퀴즈 정답"
    }}
    """

    try:
        response = model.generate_content(prompt)
        # 응답 텍스트에서 JSON 부분만 추출
        json_text = response.text.strip().replace('```json', '').replace('```', '').strip()
        quiz_data = json.loads(json_text)

        # 정답에서 공백 및 특수문자 제거하여 검사 용이하게 만듦
        quiz_data['answer_clean'] = ''.join(filter(str.isalnum, quiz_data['answer'].lower()))

        return quiz_data
    except Exception as e:
        print(f"퀴즈 생성 중 오류 발생: {e}")
        print(f"Gemini 응답: {response.text}")
        # 비상용 퀴즈 반환
        return {
            "question": f"'{category}' 퀴즈 생성에 실패했습니다. 정답에 '정답'이라고 입력하세요.",
            "answer": "정답",
            "answer_clean": "정답"
        }

# --- END OF FILE gemini_quiz.py ---