# --- START OF FILE gemini_quiz.py (수정 완료) ---

import google.generativeai as genai
import os
import json
import random
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
        # API 설정 실패 시에도 게임 진행을 위해 종료하지 않음


# 로컬 퀴즈 데이터 로드
def load_local_quizzes():
    try:
        with open('quiz_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("경고: quiz_data.json 파일을 찾을 수 없습니다. 오프라인 퀴즈 기능이 비활성화됩니다.")
        return None


local_quizzes = load_local_quizzes()


def get_local_quiz(category):
    """로컬 퀴즈 데이터에서 랜덤 퀴즈를 가져옵니다."""
    if local_quizzes and category in local_quizzes and local_quizzes[category]:
        return random.choice(local_quizzes[category])
    else:
        # 해당 카테고리가 없거나 비어있을 경우 비상 퀴즈 반환
        return {
            "question": f"'{category}'에 대한 오프라인 퀴즈가 없습니다. '정답'을 입력하세요.",
            "answer": "정답"
        }


def generate_quiz(category):
    """지정된 카테고리에 대한 퀴즈를 생성합니다. API 호출 실패 시 로컬 퀴즈를 사용합니다."""
    try:
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
        response = model.generate_content(prompt)
        json_text = response.text.strip().replace('```json', '').replace('```', '').strip()
        quiz_data = json.loads(json_text)

    except Exception as e:
        print(f"퀴즈 생성 중 오류 발생 (API 호출 실패 또는 할당량 초과): {e}")
        print("로컬 퀴즈 데이터베이스를 사용합니다.")
        quiz_data = get_local_quiz(category)

    # 정답에서 공백 및 특수문자 제거하여 검사 용이하게 만듦
    quiz_data['answer_clean'] = ''.join(filter(str.isalnum, quiz_data['answer'].lower()))

    return quiz_data

# --- END OF FILE gemini_quiz.py (수정 완료) ---