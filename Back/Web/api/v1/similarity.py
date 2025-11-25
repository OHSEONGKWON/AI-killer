"""
텍스트 유사도 검사 API 엔드포인트
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional
import logging

from ...gemini_similarity import calculate_similarity, stream_similarity
from ...dependencies import get_current_user
from ...models import User

router = APIRouter()

class SimilarityRequest(BaseModel):
    """유사도 검사 요청"""
    topic: str = Field(..., min_length=1, max_length=500, description="주제")
    text: str = Field(..., min_length=1, max_length=5000, description="검사할 텍스트")
    num_sentences: Optional[int] = Field(20, ge=1, le=50, description="생성할 AI 문단 수 (기본 20)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "topic": "인공지능",
                "text": "인공지능은 현대 사회에서 매우 중요한 기술로 자리잡고 있으며, 다양한 분야에서 활용되고 있습니다.",
                "num_sentences": 20
            }
        }


@router.post("/check", summary="텍스트 유사도 및 Perplexity 검사")
async def check_similarity(
    request: SimilarityRequest,
    current_user: User = Depends(get_current_user)
):
    """
    사용자가 입력한 텍스트와 AI가 생성한 텍스트 간의 유사도 및 Perplexity를 검사합니다.
    
    - **topic**: 생성할 텍스트의 주제
    - **text**: 검사할 사용자 텍스트
    - **num_sentences**: 생성할 문단 수 (기본값: 20, 각 200자 내외)
    
    Returns:
        - user_text: 입력된 사용자 텍스트
        - topic: 주제
        - generated_texts: 생성된 문장들
        - scores: 각 문장별 SBERT 점수
        - top_scores: 상위 3개 문장의 점수
        - final_score: 최종 유사도 점수 (0~1, SBERT 평균)
        - final_probability: 최종 유사도 확률 (0~100, %) 
        - perplexity: 사용자 텍스트의 Perplexity 값
        - num_generated: 생성된 문장 수
    """
    try:
        result = await calculate_similarity(
            user_text=request.text,
            topic=request.topic,
            num_sentences=request.num_sentences
        )
        return result
    except ValueError as e:
        logging.error(f"유사도 검사 중 오류: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging.error(f"유사도 검사 중 예상치 못한 오류: {e}")
        raise HTTPException(status_code=500, detail="유사도 검사 중 오류가 발생했습니다.")


@router.post("/check-stream", summary="텍스트 유사도 및 Perplexity 검사 스트리밍(SSE)")
async def check_similarity_stream(
    request: SimilarityRequest,
    current_user: User = Depends(get_current_user)
):
    """유사도 및 Perplexity 계산 결과를 Server-Sent Events(SSE)로 스트리밍.

    이벤트 타입:
      - final: 최종 결과(유사도 점수/확률 + Perplexity)
      - error: 오류 발생
    """
    async def event_generator():
        async for chunk in stream_similarity(
            user_text=request.text,
            topic=request.topic,
            num_sentences=request.num_sentences,
        ):
            yield chunk
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
