# (팀원 2 담당)
from typing import List
import time
import random

def calculate_similarity_score(original_text: str, generated_texts: List[str]) -> float:
    """
    [임시 함수] 원본과 생성된 텍스트 리스트를 받아 유사도 점수를 반환합니다.
    실제 모델 대신 0.5초간 대기 후 0.0 ~ 1.0 사이의 랜덤 값을 반환합니다.
    """
    print("(유사도 모듈) 분석 시작...")
    time.sleep(0.5)
    score = random.random()
    print(f"(유사도 모듈) 분석 완료: {score:.2f}")
    return score