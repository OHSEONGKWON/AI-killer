# (팀원 1 담당)
import time
import random

def calculate_kobert_score(text: str) -> float:
    """
    [임시 함수] 텍스트를 받아 KoBERT AI 작성 확률을 반환합니다.
    실제 모델 대신 1~2초간 대기 후 0.0 ~ 1.0 사이의 랜덤 값을 반환합니다.
    """
    print("(KoBERT 모듈) 분석 시작...")
    time.sleep(random.uniform(1, 2))  # 실제 모델의 처리 시간 흉내
    score = random.random()
    print(f"(KoBERT 모듈) 분석 완료: {score:.2f}")
    
    # 일부러 에러를 발생시키는 테스트 케이스 (안정성 테스트용)
    if "에러 테스트" in text:
        raise ValueError("의도적으로 발생시킨 KoBERT 분석 에러")
        
    return score