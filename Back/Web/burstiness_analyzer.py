"""
Burstiness 분석 모듈.

역할:
- 텍스트의 Burstiness(폭발성) 계산
- 문장 길이, 단어 다양성의 변동성 측정
- AI 글: 일정한 패턴 (낮은 Burstiness)
- 사람 글: 불규칙한 패턴 (높은 Burstiness)

TODO: 팀원이 실제 통계적 측정으로 구현 예정
현재는 임시 placeholder 함수
"""

import time
import random


def calculate_burstiness(text: str) -> float:
    """
    [임시 함수] 텍스트의 Burstiness를 계산합니다.
    
    실제 구현 시:
    1. 문장 단위로 분리
    2. 각 문장의 길이, 단어 개수, 복잡도 측정
    3. 분산(variance) 또는 표준편차 계산
    4. 정규화하여 0~1 범위로 변환 (낮을수록 AI-like)
    
    측정 지표:
    - 문장 길이 편차
    - 어휘 다양성(TTR: Type-Token Ratio) 변동
    - 구두점 사용 패턴
    
    Args:
        text: 분석할 텍스트
    
    Returns:
        Burstiness 기반 AI 확률 (0.0 ~ 1.0)
        낮을수록 AI가 작성한 글일 가능성 높음 (일정한 패턴)
    """
    print("(Burstiness 모듈) 폭발성 분석 시작...")
    time.sleep(0.6)  # 실제 계산 시간 시뮬레이션
    
    # 임시: 랜덤 점수 반환
    # 실제로는 낮은 burstiness → 높은 AI 확률로 변환
    score = random.uniform(0.3, 0.85)
    print(f"(Burstiness 모듈) 분석 완료: {score:.3f}")
    
    return score
