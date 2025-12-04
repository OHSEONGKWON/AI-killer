"""
표절 검사 라우터 (실시간 웹 검색 기반).

주요 기능:
- 실시간 웹 검색을 통한 정확한 표절 탐지
- 실제 출처 URL 및 제목 제공
- 문장 단위 유사도 분석
- 유사도 점수 및 상세 분석 제공
"""

import asyncio
import logging
from fastapi import APIRouter, HTTPException, Depends, status

from ... import models
from ...web_search_plagiarism import detect_plagiarism_with_web_search
from ...dependencies import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/plagiarism/check",
    response_model=models.PlagiarismResponse,
    summary="실시간 웹 검색 표절 검사",
    description="""
    실시간 웹 검색 API를 사용하여 정확한 표절을 탐지합니다.
    
    **주요 기능:**
    - 🌐 실시간 구글 검색으로 유사 콘텐츠 탐지
    - 🔗 실제 출처 URL 및 페이지 제목 제공
    - 📊 문장 단위 유사도 점수 (0.0~1.0)
    - 🎯 자동 표절 판단 (임계값 0.7)
    - ⚡ 2-4개 문장만 검색하여 빠른 응답
    
    **필요 설정:**
    - .env 파일에 SERPER_API_KEY 설정 필요
    - Serper API: https://serper.dev/ (무료: 2,500쿼리/월)
    
    **유사도 기준:**
    - 0-30: 독창적 ✅
    - 30-40: 일부 유사 ⚠️
    - 40-50: 높은 유사도 🔶
    - 50-100: 표절 의심 ❌ (임계값)
    
    **비용:**
    - 텍스트당 15-25회의 검색 쿼리 사용 (정확도 최우선)
    """,
    responses={
        200: {
            "description": "검사 성공",
            "content": {
                "application/json": {
                    "example": {
                        "suspected_source": "위키백과 - 인공지능",
                        "source_url": "https://ko.wikipedia.org/wiki/인공지능",
                        "original_found": True,
                        "overall_similarity_score": 85,
                        "is_plagiarized": True,
                        "highlight_segments": [
                            {
                                "target_text": "인공지능은 컴퓨터 과학의 한 분야로...",
                                "type": "EXACT",
                                "reason": "출처: 위키백과 - 인공지능 (유사도 85%)"
                            }
                        ],
                        "matched_sources": [
                            {
                                "source_url": "https://ko.wikipedia.org/wiki/인공지능",
                                "source_title": "위키백과 - 인공지능",
                                "similarity_score": 0.85,
                                "matched_text": "인공지능은 컴퓨터 과학의 한 분야로..."
                            }
                        ]
                    }
                }
            }
        },
        422: {"description": "입력 검증 오류 (20-10000자)"},
        503: {"description": "검색 API 오류 (SERPER_API_KEY 확인)"}
    },
    tags=["표절 검사"]
)
async def check_plagiarism(
    request: models.PlagiarismRequest,
    current_user = Depends(get_current_user)
):
    """실시간 웹 검색을 통해 입력 텍스트의 표절 여부를 검사합니다.
    
    처리 순서:
    1) 전체 텍스트로 웹 검색 (10개 결과)
    2) 텍스트를 문장 단위로 분할하여 추가 검색 (8-5개 결과)
    3) 5가지 유사도 알고리즘 적용 (LCS, 단어, bigram, trigram, 연속문자열)
    4) 표절 판정 (임계값 0.5) 및 출처 정보 반환
    
    Args:
        content: 검사할 텍스트 (20~10000자)
    
    Returns:
        PlagiarismResponse:
            - suspected_source: 가장 유사한 출처 제목
            - source_url: 출처 URL
            - original_found: 표절 여부 (bool)
            - overall_similarity_score: 최대 유사도 (0~100)
            - is_plagiarized: 표절 여부 (bool, overall_similarity_score >= 50)
            - highlight_segments: 표절 의심 구간 목록
            - highlighted_html: HTML 하이라이트
            - matched_sources: 상위 5개 유사 출처
    """
    try:
        # 실시간 웹 검색 표절 탐지 (비동기 처리)
        result = await asyncio.to_thread(
            detect_plagiarism_with_web_search, 
            request.content,
            threshold=0.5  # 50% 이상 유사하면 표절로 판단 (정확도 향상)
        )
        
        # 검색이 수행되지 않은 경우 (API 키 없음 등)
        if not result.get("searched"):
            raise HTTPException(
                status_code=503,
                detail=result.get("message", "웹 검색 API를 사용할 수 없습니다. .env 파일에 SERPER_API_KEY를 설정하세요.")
            )
        
        # 웹 검색 결과를 PlagiarismResponse 모델 형식으로 변환
        sources = result.get("sources", [])
        top_source = sources[0] if sources else None
        
        # 유사도를 0~100 범위로 변환 (원래는 0.0~1.0)
        max_similarity_score = int(result.get("max_similarity", 0.0) * 100)
        
        # MatchedSource 리스트 생성
        matched_sources = []
        for source in sources[:5]:  # 상위 5개만
            matched_sources.append(
                models.MatchedSource(
                    source_url=source.get("url"),
                    source_title=source.get("title"),
                    similarity_score=source.get("similarity", 0.0),
                    matched_text=source.get("matched_sentence", "")[:200]  # 200자까지
                )
            )
        
        # HighlightSegment 생성 (유사도 높은 문장들)
        highlight_segments = []
        for source in sources[:3]:  # 상위 3개만 하이라이트
            if source.get("similarity", 0) >= 0.7:
                highlight_segments.append(
                    models.HighlightSegment(
                        target_text=source.get("matched_sentence", "")[:100],
                        type="EXACT" if source.get("similarity", 0) >= 0.85 else "SUSPICIOUS",
                        reason=f"출처: {source.get('title', '알 수 없음')} (유사도 {source.get('similarity', 0):.0%})"
                    )
                )
        
        # HTML 하이라이트 생성
        highlighted_html = request.content
        for seg in highlight_segments:
            if seg.type == "EXACT":
                highlighted_html = highlighted_html.replace(
                    seg.target_text, 
                    f'<mark class="exact" style="background-color: #ffcccc;">{seg.target_text}</mark>'
                )
            else:
                highlighted_html = highlighted_html.replace(
                    seg.target_text,
                    f'<mark class="suspicious" style="background-color: #ffffcc;">{seg.target_text}</mark>'
                )
        
        return models.PlagiarismResponse(
            suspected_source=top_source.get("title", "출처 불명") if top_source else "출처를 찾을 수 없음",
            source_url=top_source.get("url") if top_source else None,
            original_found=result.get("is_plagiarized", False),
            overall_similarity_score=max_similarity_score,
            highlight_segments=highlight_segments,
            highlighted_html=highlighted_html,
            matched_sources=matched_sources,
            is_plagiarized=result.get("is_plagiarized", False)
        )
        
    except HTTPException:
        # HTTPException은 그대로 전파
        raise
    except ValueError as e:
        logger.error(f"표절 검사 입력 오류: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"표절 검사 중 예상치 못한 오류: {e}")
        raise HTTPException(status_code=500, detail=f"표절 검사 중 오류가 발생했습니다: {str(e)}")


