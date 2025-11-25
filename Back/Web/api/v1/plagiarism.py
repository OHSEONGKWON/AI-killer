"""
표절 검사 라우터 (Gemini AI 기반).

주요 기능:
- Gemini AI를 활용한 지능형 표절 탐지
- 원본 출처 자동 추적
- 표절 의심 구간 하이라이팅
- 유사도 점수 및 상세 분석 제공
"""

import asyncio
import logging
from fastapi import APIRouter, Depends, HTTPException

from ... import models
from ...gemini_plagiarism import detect_plagiarism, format_highlight_text
from ...dependencies import get_current_user

router = APIRouter()



@router.post("/plagiarism/check", response_model=models.PlagiarismResponse, summary="AI 표절 검사")
async def check_plagiarism(
    request: models.PlagiarismRequest
):
    """Gemini AI를 활용하여 입력 텍스트의 표절 여부를 검사합니다.
    
    처리 순서:
    1) Gemini AI가 텍스트를 분석하여 원본 출처 추적
    2) 유사도 점수 계산 (0~100)
    3) 표절 의심 구간 하이라이팅
    4) 상세 분석 결과 반환
    
    Args:
        content: 검사할 텍스트 (10~10000자)
    
    Returns:
        suspected_source: 추정 원본 출처
        original_found: 원본 발견 여부
        overall_similarity_score: 유사도 점수 (0~100)
        highlight_segments: 표절 의심 구간 목록
        highlighted_html: HTML 형식의 하이라이트된 텍스트
    """
    try:
        # Gemini AI 표절 탐지 (비동기 처리)
        result = await asyncio.to_thread(detect_plagiarism, request.content)
        
        # 오류 처리
        if "error" in result:
            raise HTTPException(status_code=500, detail=result.get("error", "표절 검사 중 오류 발생"))
        
        # 하이라이트 구간을 HighlightSegment 모델로 변환
        highlight_segments = [
            models.HighlightSegment(**seg)
            for seg in result.get("highlight_segments", [])
        ]
        
        # HTML 형식 하이라이트 생성
        highlighted_html = format_highlight_text(
            request.content,
            result.get("highlight_segments", [])
        )
        
        return models.PlagiarismResponse(
            suspected_source=result.get("suspected_source", "출처 불명"),
            source_url=result.get("source_url"),
            original_found=result.get("original_found", False),
            overall_similarity_score=result.get("overall_similarity_score", 0),
            highlight_segments=highlight_segments,
            highlighted_html=highlighted_html
        )
        
    except ValueError as e:
        logging.error(f"표절 검사 입력 오류: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging.error(f"표절 검사 중 예상치 못한 오류: {e}")
        raise HTTPException(status_code=500, detail="표절 검사 중 오류가 발생했습니다.")


