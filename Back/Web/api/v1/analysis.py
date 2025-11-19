"""
분석(analysis) 관련 라우터.

주요 기능:
- 4가지 지표로 AI 작성 확률 분석
  1. SBERT 코사인 유사도
  2. KoBERT AI 분류 확률
  3. Perplexity (혼란도)
  4. Burstiness (폭발성)
- 텍스트 유형별 가중치 적용 (관리자 설정)
- 분석 결과 DB 저장

참고:
- CPU 바운드/블로킹 작업은 asyncio.to_thread로 이벤트 루프를 막지 않도록 처리합니다.
"""

from typing import List, Optional
import asyncio
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException

from ...dependencies import get_db
from ... import models, crud
from ...kobert_analyzer import calculate_kobert_score
from ...sbert_analyzer import calculate_sbert_similarity
from ...perplexity_analyzer import calculate_perplexity
from ...burstiness_analyzer import calculate_burstiness
from ...openai_client import generate_ai_abstracts

router = APIRouter()


@router.post("/analyze", response_model=models.AnalysisResponse, summary="블로그/에세이 AI 작성 검증")
async def analyze(request: models.AnalysisRequest, db=Depends(get_db)):
    """
    텍스트를 4가지 지표로 분석하여 AI 작성 확률을 계산합니다.
    
    처리 순서:
    1) 텍스트 유형에 맞는 AnalysisConfig 로드 (없으면 default 사용)
    2) 4가지 지표를 병렬로 계산:
       - SBERT 코사인 유사도
       - KoBERT AI 분류 확률
       - Perplexity (혼란도)
       - Burstiness (폭발성)
    3) 가중치 적용하여 최종 확률 계산
    4) 결과를 DB에 저장
    """
    try:
        # 1. 텍스트 유형에 맞는 가중치 설정 로드
        text_type = getattr(request, 'text_type', 'paper')
        config = await crud.get_analysis_config(db, text_type)
        
        if not config or not config.is_active:
            # fallback to default config
            config = await crud.get_default_analysis_config(db)
            if not config:
                # 기본값이 없으면 균등 가중치 사용
                config = type('Config', (), {
                    'sbert_weight': 0.25,
                    'kobert_weight': 0.25,
                    'perplexity_weight': 0.25,
                    'burstiness_weight': 0.25,
                })()
        
        # 2. OpenAI로 AI 요약문 생성 (SBERT 비교용)
        generated_samples: List[str] = await generate_ai_abstracts(
            prompt=request.content,
            num_samples=3
        )
        
        # 3. 4가지 지표를 병렬로 계산 (CPU 바운드 작업)
        sbert_score, kobert_score, perplexity_score, burstiness_score = await asyncio.gather(
            asyncio.to_thread(calculate_sbert_similarity, request.content, generated_samples),
            asyncio.to_thread(calculate_kobert_score, request.content),
            asyncio.to_thread(calculate_perplexity, request.content),
            asyncio.to_thread(calculate_burstiness, request.content),
        )
        
        # 4. 가중치 적용하여 최종 AI 확률 계산
        final_probability = (
            sbert_score * config.sbert_weight +
            kobert_score * config.kobert_weight +
            perplexity_score * config.perplexity_weight +
            burstiness_score * config.burstiness_weight
        )
        
        # 5. 결과를 DB에 저장
        try:
            await crud.create_analysis_record(
                db,
                title=request.title,
                content=request.content,
                ai_probability=final_probability,
                kobert_score=kobert_score,
                similarity_score=sbert_score,  # SBERT score stored here
                perplexity_score=perplexity_score,
                burstiness_score=burstiness_score,
                created_at=datetime.utcnow().isoformat(),
            )
        except Exception as e:
            print(f"DB 저장 오류(무시하고 계속 진행): {e}")
        
        return models.AnalysisResponse(
            ai_probability=final_probability,
            analysis_details=models.AnalysisDetails(
                kobert_score=kobert_score,
                similarity_score=sbert_score,
                perplexity_score=perplexity_score,
                burstiness_score=burstiness_score,
            ),
        )
        
    except Exception as e:
        print(f"분석 오류 발생: {e}")
        raise HTTPException(status_code=500, detail=f"분석 중 오류가 발생했습니다: {str(e)}")
