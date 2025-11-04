"""
SBERT 코사인 유사도 분석 모듈.

역할:
- 입력 텍스트와 AI 생성 샘플들 간의 코사인 유사도 계산
- SBERT (Sentence-BERT) 임베딩 기반

TODO: 팀원이 실제 SBERT 모델로 구현 예정
현재는 임시 placeholder 함수
"""

import time
import random
from typing import List


def calculate_sbert_similarity(original_text: str, generated_samples: List[str]) -> float:
    """
    [임시 함수] 원본 텍스트와 AI 생성 샘플들 간의 코사인 유사도를 계산합니다.
    
    실제 구현 시:
    1. SBERT 모델로 original_text 임베딩
    2. generated_samples들도 각각 임베딩
    3. 코사인 유사도 계산
    4. 평균 또는 최대값 반환
    
    Args:
        original_text: 분석할 원본 텍스트
        generated_samples: AI가 생성한 비교용 샘플 리스트
    
    Returns:
        코사인 유사도 점수 (0.0 ~ 1.0)
        높을수록 AI가 작성한 글과 유사함
    """
    print("(SBERT 모듈) 코사인 유사도 분석 시작...")
    time.sleep(0.5)  # 실제 모델 처리 시간 시뮬레이션
    
    score = random.uniform(0.3, 0.9)
    print(f"(SBERT 모듈) 분석 완료: {score:.3f}")
    
    return score
