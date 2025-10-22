"""
KoBERT 분석 모듈(임시 구현).

주의:
- 현재는 실제 모델 대신 시간 지연 후 랜덤 값을 반환하여 흐름만 검증합니다.
- 특정 문자열("에러 테스트")을 포함하면 의도적으로 에러를 발생시켜 예외 처리 경로를 테스트합니다.
"""

# (팀원 1 담당)
import time
import random


def calculate_kobert_score(text: str) -> float:
    """텍스트를 받아 KoBERT AI 작성 확률(0~1)을 임시로 반환합니다."""
    print("(KoBERT 모듈) 분석 시작...")
    time.sleep(random.uniform(1, 2))  # 실제 모델의 처리 시간 흉내
    score = random.random()
    print(f"(KoBERT 모듈) 분석 완료: {score:.2f}")
    
    # 안정성 테스트: 특정 키워드가 있으면 예외를 발생
    if "에러 테스트" in text:
        raise ValueError("의도적으로 발생시킨 KoBERT 분석 에러")
        
    return score