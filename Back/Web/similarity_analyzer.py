"""
유사도 분석 모듈(임시 구현).

주의:
- 실제 유사도 모델 대신 지연 후 랜덤 점수를 반환합니다.
"""

# (팀원 2 담당)
from typing import List
import time
import random


def calculate_similarity_score(original_text: str, generated_texts: List[str]) -> float:
    """원본 텍스트와 생성 텍스트들 간 유사도 점수(0~1)를 임시로 반환합니다."""
    print("(유사도 모듈) 분석 시작...")
    time.sleep(0.5)
    score = random.random()
    print(f"(유사도 모듈) 분석 완료: {score:.2f}")
    return score