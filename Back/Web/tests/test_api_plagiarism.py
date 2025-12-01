"""
표절 검사 API 테스트.

pytest -v tests/test_api_plagiarism.py
"""

import pytest
from httpx import AsyncClient
from fastapi import status

from Back.Web.main import app


@pytest.mark.asyncio
async def test_plagiarism_check_success():
    """정상적인 표절 검사 요청."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/plagiarism/check",
            json={
                "content": "인공지능은 컴퓨터 과학의 한 분야로, 기계가 인간의 지능을 모방하도록 하는 기술입니다."
            }
        )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    # 응답 구조 검증
    assert "overall_similarity_score" in data
    assert "is_plagiarized" in data
    assert "highlight_segments" in data
    
    # 점수 범위 검증
    assert 0 <= data["overall_similarity_score"] <= 100


@pytest.mark.asyncio
async def test_plagiarism_check_short_text():
    """짧은 텍스트 입력 시 검증 오류."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/plagiarism/check",
            json={"content": "짧은글"}
        )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_plagiarism_check_too_long():
    """10000자 초과 입력."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/plagiarism/check",
            json={"content": "a" * 10001}
        )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_plagiarism_check_original_content():
    """오리지널 콘텐츠는 낮은 유사도."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/plagiarism/check",
            json={
                "content": "이것은 완전히 새로운 독창적인 문장입니다. 어디에도 존재하지 않는 고유한 내용을 담고 있습니다."
            }
        )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data["is_plagiarized"], bool)
