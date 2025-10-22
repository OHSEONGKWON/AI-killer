"""
분석(analysis) 관련 라우터.

주요 기능:
- 블로그/에세이 본문을 KoBERT와 간이 유사도 분석으로 평가
- 두 점수를 가중 평균하여 최종 AI 작성 확률을 반환

참고:
- generate_ai_content는 실제 OpenAI 연동 전 임시 구현입니다.
- CPU 바운드/블로킹 작업은 asyncio.to_thread로 이벤트 루프를 막지 않도록 처리합니다.
"""

from typing import List
import asyncio
from fastapi import APIRouter, Depends, HTTPException

from ...dependencies import get_db
from ... import models
from ...similarity_analyzer import calculate_similarity_score
from ...kobert_analyzer import calculate_kobert_score

router = APIRouter()


def combine_scores_placeholder(kobert_score: float, similarity_score: float) -> float:
    """임시 최종 확률 계산 로직 (가중 평균). 실제 모델 결합 전 기본 로직.

    - kobert_score: KoBERT가 산출한 AI 작성 확률(0~1)
    - similarity_score: 원본과 생성문 사이 유사도 점수(0~1)
    """
    print("💡 주의: 임시 최종 확률 계산 로직을 사용 중입니다.")
    return (kobert_score * 0.7) + (similarity_score * 0.3)


@router.post("/analyze", response_model=models.AnalysisResponse, summary="블로그/에세이 AI 작성 검증")
async def analyze(request: models.AnalysisRequest, db=Depends(get_db)):
    """블로그/에세이를 분석하여 AI 작성 확률을 반환합니다.

    처리 순서:
    1) KoBERT 점수 계산과 샘플 생성 글 생성(비동기 병렬)
    2) 생성 글과 원문 간 유사도 점수 계산(스레드로 실행)
    3) 두 점수를 가중 평균으로 결합해 최종 확률 산출
    """
    try:
        # CPU 바운드/블로킹 작업은 to_thread로 분리하여 이벤트 루프 유지
        kobert_score, generated_contents = await asyncio.gather(
            asyncio.to_thread(calculate_kobert_score, request.content),
            generate_ai_content(request.title),
        )
    except Exception as e:
        print(f"분석 초기 단계 오류 발생: {e}")
        raise HTTPException(status_code=500, detail="내부 분석 모듈 또는 외부 API 호출 중 오류가 발생했습니다.")

    # similarity 모듈이 동기 블로킹을 포함할 수 있으므로 별도 스레드에서 실행
    similarity_score = await asyncio.to_thread(
        calculate_similarity_score,
        request.content,
        generated_contents,
    )

    final_probability = combine_scores_placeholder(
        kobert_score=kobert_score,
        similarity_score=similarity_score,
    )

    return models.AnalysisResponse(
        ai_probability=final_probability,
        analysis_details=models.AnalysisDetails(
            kobert_score=kobert_score,
            similarity_score=similarity_score,
        ),
    )


async def generate_ai_content(title: str) -> List[str]:
    """샘플 AI 블로그/에세이를 생성하는 임시 함수(실제 OpenAI 연동 전)."""
    print("(OpenAI 모듈) 샘플 글 생성 시작...")
    await asyncio.sleep(1.5)
    print("(OpenAI 모듈) 샘플 글 생성 완료")
    return [
        f"{title}에 대한 첫 번째 AI 생성 블로그 글입니다.",
        f"{title}에 대한 두 번째 AI 생성 에세이입니다.",
    ]
