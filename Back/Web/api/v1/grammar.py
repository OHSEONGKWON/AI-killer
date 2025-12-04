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
from fastapi import APIRouter, HTTPException, Depends, status

from ... import models
from ...gemini_grammar import check_grammar
from ...dependencies import get_current_user

router = APIRouter()


@router.post(
    "/grammar/check",
    response_model=models.GrammarCheckResponse,
    summary="한국어 문법 및 스타일 검사",
    description="""
    입력된 한국어 텍스트를 Gemini 2.0 Flash AI로 분석하여 다음을 제공합니다:
    
    **주요 기능:**
    - 📝 맞춤법/문법 오류 자동 수정
    - ✨ 문체 개선 및 윤문 (세련된 표현)
    - 🔍 수정 내역 상세 설명 (before/after)
    - 📊 문법 점수 (0-100) 및 자연스러움 평가
    - 💡 어휘 개선 제안 (더 나은 표현)
    
    **입력 제한:**
    - 최소 1자, 최대 10,000자
    
    **응답 시간:**
    - 일반적으로 2-5초 소요
    """,
    responses={
        200: {
            "description": "분석 성공",
            "content": {
                "application/json": {
                    "example": {
                        "original_text": "안녕하세요. 저는 학생입니다.",
                        "corrected_text": "안녕하세요. 저는 학생입니다.",
                        "refined_text": "안녕하십니까. 저는 학생입니다.",
                        "diff_explanation": [
                            {
                                "original": "안녕하세요",
                                "changed": "안녕하십니까",
                                "reason": "더 격식 있는 표현으로 개선"
                            }
                        ],
                        "nuance_feedback": "전체적으로 자연스러운 문장입니다.",
                        "vocabulary_suggestions": [],
                        "score": {"grammar": 95, "naturalness": 90}
                    }
                }
            }
        },
        422: {"description": "입력 검증 오류 (텍스트 길이 초과 등)"},
        503: {"description": "AI 서비스 일시적 오류"}
    },
    tags=["문법 검사"]
)
async def check_grammar_endpoint(
    request: models.GrammarCheckRequest,
    current_user = Depends(get_current_user)
):
    """입력 텍스트의 문법을 Gemini API로 검사하고 교정합니다."""
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
