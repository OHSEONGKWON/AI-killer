"""
AI-like 문장 하이라이팅 라우터.

주요 기능:
- 입력 텍스트에서 AI가 작성한 것처럼 보이는 문장/구간 탐지
- 각 구간에 AI-like 점수와 이유를 부여
- 전체 텍스트의 AI-like 비율 계산

참고:
- 현재는 패턴 기반 휴리스틱으로 구현 (실제로는 ML 모델 사용 권장)
- 탐지 패턴: 반복적 표현, 지나치게 완벽한 문법, 일반적인 문구 등
"""

import re
from typing import List
from fastapi import APIRouter

from ... import models

router = APIRouter()


def detect_ai_like_patterns(text: str) -> List[models.HighlightSegment]:
    """텍스트에서 AI-like 패턴을 찾아 하이라이팅할 구간 목록 반환.
    
    탐지 패턴:
    - 과도하게 형식적인 문구 (예: "중요한 점은...", "결론적으로...")
    - 반복적인 전환 표현
    - 지나치게 일반적인 문장
    - 리스트/나열 형태의 구조적 글
    """
    segments = []
    
    # AI가 자주 사용하는 문구 패턴 (한국어)
    ai_patterns = [
        (r"중요한 점은[^.!?]*[.!?]", "형식적인 강조 표현", 0.7),
        (r"결론적으로[^.!?]*[.!?]", "형식적인 전환 표현", 0.75),
        (r"먼저[,\s]+[^.!?]*[.!?].*둘째[,\s]+[^.!?]*[.!?]", "구조적 나열 패턴", 0.8),
        (r"~할 수 있습니다[.!?]", "과도한 정중 표현", 0.65),
        (r"~하는 것이 중요합니다[.!?]", "일반적인 조언 패턴", 0.7),
        (r"다양한[^.!?]*있습니다", "모호한 일반화", 0.6),
        (r"~에 대해 살펴보[^.!?]*[.!?]", "형식적인 안내 표현", 0.7),
        (r"이러한[^.!?]*통해", "형식적 연결어", 0.65),
    ]
    
    for pattern, reason, score in ai_patterns:
        for match in re.finditer(pattern, text):
            segments.append(models.HighlightSegment(
                text=match.group(),
                start_index=match.start(),
                end_index=match.end(),
                ai_score=score,
                reason=reason
            ))
    
    # 중복 제거 및 정렬
    segments = sorted(segments, key=lambda x: x.start_index)
    
    return segments


def calculate_ai_ratio(text: str, segments: List[models.HighlightSegment]) -> float:
    """전체 텍스트 중 AI-like 구간의 비율 계산."""
    if not text or not segments:
        return 0.0
    
    # 하이라이팅된 문자 수 총합
    highlighted_chars = sum(seg.end_index - seg.start_index for seg in segments)
    total_chars = len(text)
    
    if total_chars == 0:
        return 0.0
    
    return round(highlighted_chars / total_chars, 3)


@router.post("/highlighting/analyze", response_model=models.HighlightResponse, summary="AI-like 문장 하이라이팅")
async def analyze_highlighting(request: models.HighlightRequest):
    """입력 텍스트에서 AI가 작성한 것처럼 보이는 문장들을 찾아 하이라이팅합니다.
    
    처리 순서:
    1) 텍스트를 분석하여 AI-like 패턴 탐지
    2) 각 패턴에 점수와 이유 부여
    3) 전체 AI-like 비율 계산
    
    반환값:
    - segments: 하이라이팅할 구간 목록 (위치, 점수, 이유 포함)
    - overall_ai_ratio: 전체 텍스트 중 AI-like 비율
    """
    # AI-like 패턴 탐지
    segments = detect_ai_like_patterns(request.content)
    
    # 전체 AI 비율 계산
    ai_ratio = calculate_ai_ratio(request.content, segments)
    
    return models.HighlightResponse(
        segments=segments,
        overall_ai_ratio=ai_ratio
    )
