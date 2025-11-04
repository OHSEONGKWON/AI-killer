"""
Perplexity 분석 모듈.

역할:
- 텍스트의 Perplexity(혼란도) 계산
- 낮은 Perplexity = AI가 작성한 글일 가능성 높음 (예측 가능)
- 높은 Perplexity = 사람이 작성한 글일 가능성 높음 (예측 불가능)

TODO: 팀원이 실제 언어 모델로 구현 예정
현재는 임시 placeholder 함수
"""

import time
import random


def calculate_perplexity(text: str) -> float:
    """
    [임시 함수] 텍스트의 Perplexity를 계산합니다.
    
    실제 구현 시:
    1. GPT-2 또는 KoGPT 같은 언어 모델 로드
    2. 텍스트에 대한 log-likelihood 계산
    3. Perplexity = exp(- log-likelihood / token_count)
    4. 정규화하여 0~1 범위로 변환 (낮을수록 AI-like)
    
    Args:
        text: 분석할 텍스트
    
    Returns:
        Perplexity 기반 AI 확률 (0.0 ~ 1.0)
        높을수록 AI가 작성한 글일 가능성 높음
    """
    print("(Perplexity 모듈) 혼란도 분석 시작...")
    time.sleep(0.7)  # 실제 모델 처리 시간 시뮬레이션
    
    # 임시: 랜덤 점수 반환
    # 실제로는 낮은 perplexity → 높은 AI 확률로 변환
    score = random.uniform(0.2, 0.8)
    print(f"(Perplexity 모듈) 분석 완료: {score:.3f}")
    
    return score
