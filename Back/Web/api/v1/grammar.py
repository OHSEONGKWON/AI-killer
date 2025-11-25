"""
Gemini API 기반 문법 검사 라우터.

주요 기능:
- Gemini API를 이용한 한국어 맞춤법/문법 교정
- 윤문 (문체 개선)
- 수정 내역 상세 설명
- 문법 점수 및 자연스러움 평가
- 어휘 추천
"""

import asyncio
from fastapi import APIRouter, HTTPException

from ... import models
from ...gemini_grammar import check_grammar

router = APIRouter()


@router.post("/grammar/check", response_model=models.GrammarCheckResponse, summary="문법 검사")
async def check_grammar_endpoint(request: models.GrammarCheckRequest):
    """입력 텍스트의 문법을 Gemini API로 검사하고 교정합니다.
    
    처리 내용:
    1) 맞춤법/오타 교정 (corrected_text)
    2) 문체 개선 및 윤문 (refined_text)
    3) 수정 내역 상세 설명 (diff_explanation)
    4) 문법 점수 및 자연스러움 평가 (score)
    5) 어휘 추천 (vocabulary_suggestions)
    
    Args:
        content: 검사할 텍스트
    
    Returns:
        original_text: 원문
        corrected_text: 맞춤법 교정된 텍스트
        refined_text: 윤문된 최종 텍스트
        diff_explanation: 수정 내역 리스트
        nuance_feedback: 뉘앙스 분석
        vocabulary_suggestions: 어휘 추천 리스트
        score: 문법/자연스러움 점수
    """
    try:
        # Gemini API는 blocking이므로 asyncio.to_thread로 비동기 처리
        result = await asyncio.to_thread(check_grammar, request.content)
        
        # Gemini 응답을 Pydantic 모델로 변환
        return models.GrammarCheckResponse(
            original_text=result.get("original_text", request.content),
            corrected_text=result.get("corrected_text", ""),
            refined_text=result.get("refined_text", ""),
            diff_explanation=[
                models.DiffExplanation(**diff) 
                for diff in result.get("diff_explanation", [])
            ],
            nuance_feedback=result.get("nuance_feedback", ""),
            vocabulary_suggestions=[
                models.VocabularySuggestion(**vocab) 
                for vocab in result.get("vocabulary_suggestions", [])
            ],
            score=models.GrammarScore(**result.get("score", {"grammar": 0, "naturalness": 0}))
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=500,
            detail=f"응답 파싱 오류: {str(e)}"
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=500,
            detail=f"문법 검사 중 오류 발생: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"예상치 못한 오류 발생: {str(e)}"
        )
