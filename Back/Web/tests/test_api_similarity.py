"""
유사도 검사 API 테스트.

pytest -v tests/test_api_similarity.py
"""

import pytest
from httpx import AsyncClient
from fastapi import status

from Back.Web.main import app


@pytest.mark.asyncio
async def test_similarity_check_success():
    """정상적인 유사도 검사 요청."""
    async with AsyncClient(app=app, base_url="http://test", timeout=60.0) as client:
        response = await client.post(
            "/api/v1/similarity/check",
            json={
                "topic": "인공지능의 미래",
                "text": "인공지능 기술은 빠르게 발전하고 있으며, 우리의 일상생활에 많은 영향을 미치고 있습니다.",
                "num_sentences": 5
            }
        )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    # 응답 구조 검증
    assert "top3_summary" in data
    assert "all_scores" in data
    assert "perplexity" in data
    assert "final_probability" in data
    
    # 배열 길이 검증
    assert len(data["all_scores"]) == 5
    
    # 점수 범위 검증
    assert 0 <= data["final_probability"] <= 1
    assert data["perplexity"] >= 0


@pytest.mark.asyncio
async def test_similarity_check_missing_topic():
    """주제 누락 시 검증 오류."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/similarity/check",
            json={
                "text": "테스트 텍스트입니다.",
                "num_sentences": 5
            }
        )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_similarity_check_invalid_num_sentences():
    """문장 수 범위 초과."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/similarity/check",
            json={
                "topic": "테스트",
                "text": "테스트 텍스트입니다.",
                "num_sentences": 100  # 최대 50
            }
        )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_similarity_check_default_num_sentences():
    """num_sentences 기본값(20) 테스트."""
    async with AsyncClient(app=app, base_url="http://test", timeout=60.0) as client:
        response = await client.post(
            "/api/v1/similarity/check",
            json={
                "topic": "과학 기술",
                "text": "과학 기술은 인류의 발전을 이끌어왔습니다."
            }
        )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["all_scores"]) == 20  # 기본값


@pytest.mark.asyncio
async def test_similarity_check_min_sentences():
    """최소 문장 수(1) 테스트."""
    async with AsyncClient(app=app, base_url="http://test", timeout=30.0) as client:
        response = await client.post(
            "/api/v1/similarity/check",
            json={
                "topic": "날씨",
                "text": "오늘 날씨가 좋습니다.",
                "num_sentences": 1
            }
        )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["all_scores"]) == 1
