"""
실시간 웹 검색 기반 표절 검사 API 엔드포인트
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
import logging

from ...web_search_plagiarism import (
    hybrid_plagiarism_check, 
    detect_plagiarism_with_web_search
)
from ...dependencies import get_current_user_optional
from ...models import User

router = APIRouter(tags=["표절 검사 (실시간 검색)"])
logger = logging.getLogger(__name__)


class WebPlagiarismRequest(BaseModel):
    """웹 검색 기반 표절 검사 요청"""
    content: str = Field(..., min_length=20, max_length=10000, description="검사할 텍스트")
    threshold: float = Field(0.7, ge=0.0, le=1.0, description="표절 판단 임계값 (0.0~1.0)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": "인공지능은 컴퓨터 과학의 한 분야로, 기계가 인간의 지능을 모방하도록 하는 기술입니다.",
                "threshold": 0.7
            }
        }


@router.post(
    "/plagiarism/check-web",
    summary="실시간 웹 검색 기반 표절 검사",
    description="""
    실제 웹 검색 API(Serper)를 사용하여 표절을 탐지합니다.
    
    **기능:**
    - 🌐 실시간 구글 검색으로 유사 콘텐츠 탐지
    - 📊 문장 단위 유사도 계산
    - 🔗 실제 출처 URL 및 제목 제공
    - 🎯 사용자 정의 가능한 임계값
    
    **필요 설정:**
    - .env 파일에 SERPER_API_KEY 설정 필요
    - Serper API: https://serper.dev/ (무료: 2,500쿼리/월)
    
    **비용:**
    - 텍스트당 2-4회의 검색 쿼리 사용
    """,
    responses={
        200: {"description": "검사 성공"},
        422: {"description": "입력 검증 오류"},
        503: {"description": "검색 API 오류"}
    }
)
async def check_plagiarism_web(
    request: WebPlagiarismRequest,
    current_user: User = Depends(get_current_user_optional)
):
    """실시간 웹 검색으로 표절을 검사합니다."""
    try:
        result = detect_plagiarism_with_web_search(
            text=request.content,
            threshold=request.threshold
        )
        
        # 검색이 수행되지 않은 경우 (API 키 없음 등)
        if not result.get("searched"):
            return {
                "success": False,
                "message": result.get("message", "웹 검색을 수행할 수 없습니다."),
                "result": result
            }
        
        return {
            "success": True,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"웹 검색 표절 검사 오류: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"표절 검사 중 오류가 발생했습니다: {str(e)}"
        )


@router.post(
    "/plagiarism/check-hybrid",
    summary="하이브리드 표절 검사 (AI + 웹 검색)",
    description="""
    Gemini AI 분석과 실시간 웹 검색을 결합한 가장 정확한 표절 검사입니다.
    
    **2단계 검증:**
    1. 🤖 Gemini AI가 학습 데이터에서 유사 콘텐츠 탐지
    2. 🌐 실시간 웹 검색으로 실제 출처 확인
    
    **장점:**
    - AI의 넓은 지식 + 실시간 검색의 정확성
    - 가장 높은 정확도
    - 출처 URL 제공
    
    **단점:**
    - 검색 API 할당량 소비 (텍스트당 2-4회)
    """,
    responses={
        200: {"description": "검사 성공"},
        422: {"description": "입력 검증 오류"}
    }
)
async def check_plagiarism_hybrid(
    request: WebPlagiarismRequest,
    current_user: User = Depends(get_current_user_optional)
):
    """AI 분석과 웹 검색을 결합하여 표절을 검사합니다."""
    try:
        result = hybrid_plagiarism_check(request.content)
        
        return {
            "success": True,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"하이브리드 표절 검사 오류: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"표절 검사 중 오류가 발생했습니다: {str(e)}"
        )
