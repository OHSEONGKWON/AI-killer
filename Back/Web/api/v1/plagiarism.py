"""
표절/유사도 검사 라우터.

주요 기능:
- 웹 검색 기반으로 입력 텍스트와 유사한 콘텐츠 탐지
- 내부 저장소 대비 중복도 검사
- 표절 의심 소스 목록과 유사도 점수 제공

검사 방식:
- 웹 검색: 핵심 문구로 검색 엔진 쿼리 후 결과 비교 (현재는 시뮬레이션)
- 내부 검사: DB에 저장된 이전 분석 이력과 비교
- 문장 단위 n-gram 유사도 계산

주의:
- 실제 웹 검색은 외부 API(Google Custom Search, Bing) 연동 필요
- 현재는 임시 데이터로 동작을 시뮬레이션합니다
"""

import re
import hashlib
from typing import List
from fastapi import APIRouter, Depends

from ... import models
from ...dependencies import get_db

router = APIRouter()


def extract_key_phrases(text: str, max_phrases: int = 5) -> List[str]:
    """텍스트에서 핵심 문구 추출 (검색 쿼리용).
    
    Args:
        text: 분석할 텍스트
        max_phrases: 추출할 최대 문구 수
    
    Returns:
        핵심 문구 목록
    """
    # 간단한 구현: 긴 문장들을 핵심 문구로 추출
    sentences = [s.strip() for s in re.split(r'[.!?]', text) if len(s.strip()) > 20]
    
    # 길이 순으로 정렬하여 상위 N개 추출
    phrases = sorted(sentences, key=len, reverse=True)[:max_phrases]
    
    return phrases


def calculate_text_similarity(text1: str, text2: str) -> float:
    """두 텍스트 간 유사도 계산 (0~1).
    
    간단한 n-gram 기반 유사도 계산.
    실제로는 TF-IDF, 코사인 유사도, 또는 임베딩 기반 방법 사용 권장.
    """
    # 3-gram 생성
    def get_ngrams(text: str, n: int = 3) -> set:
        words = text.lower().split()
        return set(' '.join(words[i:i+n]) for i in range(len(words)-n+1))
    
    ngrams1 = get_ngrams(text1)
    ngrams2 = get_ngrams(text2)
    
    if not ngrams1 or not ngrams2:
        return 0.0
    
    # Jaccard 유사도
    intersection = len(ngrams1 & ngrams2)
    union = len(ngrams1 | ngrams2)
    
    return round(intersection / union if union > 0 else 0.0, 3)


async def search_web_similar_content(text: str) -> List[models.MatchedSource]:
    """웹에서 유사한 콘텐츠 검색 (임시 구현).
    
    실제 구현 시에는:
    - Google Custom Search API
    - Bing Search API
    - 또는 직접 크롤링 (주의: robots.txt 준수)
    
    현재는 시뮬레이션 데이터 반환.
    """
    # 핵심 문구 추출
    key_phrases = extract_key_phrases(text, max_phrases=3)
    
    # 임시: 시뮬레이션 검색 결과
    # 실제로는 여기서 검색 API 호출
    simulated_results = [
        models.MatchedSource(
            source_url="https://example-blog.com/similar-article-1",
            source_title="비슷한 주제의 블로그 글",
            similarity_score=0.65,
            matched_text=key_phrases[0] if key_phrases else "샘플 일치 텍스트"
        ),
        models.MatchedSource(
            source_url="https://another-site.com/content-2",
            source_title="관련 에세이",
            similarity_score=0.42,
            matched_text=key_phrases[1] if len(key_phrases) > 1 else "또 다른 일치 구간"
        )
    ]
    
    # 유사도 임계치 이상만 반환 (0.4 이상)
    return [s for s in simulated_results if s.similarity_score >= 0.4]


async def check_internal_similarity(text: str, db) -> List[models.MatchedSource]:
    """내부 저장소(DB)에서 유사한 콘텐츠 검색.
    
    실제 구현 시:
    - User 테이블에 분석 이력 저장 기능 추가
    - 또는 별도 ContentHistory 테이블 생성
    - 각 저장된 콘텐츠와 유사도 비교
    
    현재는 빈 결과 반환 (DB 스키마 확장 후 구현).
    """
    # TODO: DB에서 이전 콘텐츠 조회 및 유사도 비교
    # 현재는 기능 비활성화
    return []


@router.post("/plagiarism/check", response_model=models.PlagiarismResponse, summary="표절/유사도 검사")
async def check_plagiarism(request: models.PlagiarismRequest, db=Depends(get_db)):
    """입력 텍스트의 표절 여부를 웹 검색 및 내부 DB를 통해 검사합니다.
    
    처리 순서:
    1) 텍스트에서 핵심 문구 추출
    2) 웹 검색으로 유사 콘텐츠 탐지 (옵션)
    3) 내부 저장소 대비 중복도 검사 (옵션)
    4) 전체 유사도 및 표절 여부 판정
    
    Args:
        content: 검사할 텍스트
        check_web: 웹 검색 활성화 여부
        check_internal: 내부 DB 검사 활성화 여부
    
    Returns:
        overall_similarity: 전체 유사도 점수 (0~1)
        matched_sources: 유사한 소스 목록
        is_plagiarized: 표절 여부 (임계치 0.7 기준)
    """
    matched_sources = []
    
    # 웹 검색 기반 유사도 검사
    if request.check_web:
        web_matches = await search_web_similar_content(request.content)
        matched_sources.extend(web_matches)
    
    # 내부 DB 기반 유사도 검사
    if request.check_internal:
        internal_matches = await check_internal_similarity(request.content, db)
        matched_sources.extend(internal_matches)
    
    # 전체 유사도 계산 (가장 높은 점수 기준)
    overall_similarity = max(
        [source.similarity_score for source in matched_sources],
        default=0.0
    )
    
    # 표절 판정 (임계치 0.7)
    PLAGIARISM_THRESHOLD = 0.7
    is_plagiarized = overall_similarity >= PLAGIARISM_THRESHOLD
    
    return models.PlagiarismResponse(
        overall_similarity=overall_similarity,
        matched_sources=matched_sources,
        is_plagiarized=is_plagiarized
    )


@router.get("/plagiarism/sources/{content_hash}", summary="특정 콘텐츠의 유사 소스 조회")
async def get_plagiarism_sources(content_hash: str):
    """이전에 검사한 콘텐츠의 유사 소스 목록을 다시 조회합니다.
    
    Args:
        content_hash: 콘텐츠의 해시값 (검사 시 생성)
    
    Returns:
        cached_sources: 캐시된 유사 소스 목록
    
    주의: 실제 구현 시 캐시/DB에 검사 결과 저장 필요
    """
    # TODO: Redis 또는 DB에서 캐시된 결과 조회
    return {
        "content_hash": content_hash,
        "cached_sources": [],
        "message": "캐싱 기능은 추후 구현 예정입니다"
    }
