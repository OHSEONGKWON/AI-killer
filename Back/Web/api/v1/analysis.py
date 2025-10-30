"""
분석(analysis) 관련 라우터.

주요 기능:
- 블로그/에세이 본문을 KoBERT 분석으로 평가
- AI 작성 확률을 반환하고 결과를 DB에 저장

참고:
- CPU 바운드/블로킹 작업은 asyncio.to_thread로 이벤트 루프를 막지 않도록 처리합니다.
"""

from typing import List
import asyncio
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException

from ...dependencies import get_db
from ... import models
from ...kobert_analyzer import calculate_kobert_score
from ...crud import create_analysis_record

router = APIRouter()


@router.post("/analyze", response_model=models.AnalysisResponse, summary="블로그/에세이 AI 작성 검증")
async def analyze(request: models.AnalysisRequest, db=Depends(get_db)):
    """블로그/에세이를 분석하여 AI 작성 확률을 반환합니다.

    처리 순서:
    1) KoBERT 점수 계산 (CPU 바운드 작업을 별도 스레드에서 실행)
    2) 결과를 DB에 저장
    3) AI 작성 확률 반환
    """
    try:
        # CPU 바운드 작업은 to_thread로 분리하여 이벤트 루프 유지
        kobert_score = await asyncio.to_thread(calculate_kobert_score, request.content)
    except Exception as e:
        print(f"분석 오류 발생: {e}")
        raise HTTPException(status_code=500, detail="내부 분석 모듈 호출 중 오류가 발생했습니다.")

    # KoBERT 점수를 최종 AI 확률로 사용
    final_probability = kobert_score

    # 분석 결과를 DB에 저장 (similarity_score는 0.0으로 저장)
    try:
        await create_analysis_record(
            db,
            title=request.title,
            content=request.content,
            ai_probability=final_probability,
            kobert_score=kobert_score,
            similarity_score=0.0,  # 더 이상 사용하지 않음
            created_at=datetime.utcnow().isoformat(),
        )
    except Exception as e:
        print(f"DB 저장 오류(무시하고 계속 진행): {e}")

    return models.AnalysisResponse(
        ai_probability=final_probability,
        analysis_details=models.AnalysisDetails(
            kobert_score=kobert_score,
            similarity_score=0.0,  # 더 이상 사용하지 않음
        ),
    )
