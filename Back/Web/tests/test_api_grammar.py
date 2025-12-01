"""
문법 검사 API 테스트.

pytest -v tests/test_api_grammar.py
pytest tests/test_api_grammar.py::test_grammar_check_success -v
"""

import pytest
from httpx import AsyncClient
from fastapi import status

from Back.Web.main import app


@pytest.mark.asyncio
async def test_grammar_check_success():
    """정상적인 문법 검사 요청."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/grammar/check",
            json={
                "content": "안녕하세요. 이것은 테스트 문장입니다. 문법 검사를 진행합니다."
            }
        )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    # 응답 구조 검증
    assert "original_text" in data
    assert "corrected_text" in data
    assert "refined_text" in data
    assert "diff_explanation" in data
    assert "score" in data
    assert "grammar" in data["score"]
    assert "naturalness" in data["score"]
    
    # 점수 범위 검증
    assert 0 <= data["score"]["grammar"] <= 100
    assert 0 <= data["score"]["naturalness"] <= 100


@pytest.mark.asyncio
async def test_grammar_check_empty_content():
    """빈 텍스트 입력 시 검증 오류."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/grammar/check",
            json={"content": ""}
        )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_grammar_check_too_long():
    """10000자 초과 입력 시 검증 오류."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/grammar/check",
            json={"content": "a" * 10001}
        )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_grammar_check_korean_text():
    """한국어 문장 검사."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/grammar/check",
            json={
                "content": "저는 학교에 갔어요. 친구를 만났습니다."
            }
        )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["original_text"]) > 0


@pytest.mark.asyncio
async def test_grammar_check_with_errors():
    """문법 오류가 있는 텍스트 검사."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/grammar/check",
            json={
                "content": "나는 밥을 먹엇다. 그리고 집에 갔다."
            }
        )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    # 수정 내역이 있을 것으로 예상
    assert "diff_explanation" in data
