"""
analysis.py 라우터 단위 테스트.

테스트 항목:
- 정상 분석 요청/응답
- 빈 콘텐츠 처리
- KoBERT 모듈 오류 처리
- DB 저장 실패 시에도 응답 반환 (무시하고 계속)
"""

import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock
from fastapi import status

# Back/Web 디렉터리를 패키지로 인식할 수 있도록 경로 조정
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 이제 직접 import 가능
import main
from main import app
import models


@pytest.mark.asyncio
async def test_analyze_success():
    """정상 분석 요청 시 AI 확률과 세부 점수를 반환합니다."""
    # KoBERT 모듈을 모킹하여 고정된 점수 반환
    with patch('kobert_analyzer.calculate_kobert_score', return_value=0.85):
        # DB 저장 함수도 모킹 (실제 DB 없이 테스트)
        with patch('crud.create_analysis_record', new_callable=AsyncMock):
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/analyze",
                    json={
                        "title": "인공지능의 미래",
                        "content": "인공지능 기술은 빠르게 발전하고 있습니다."
                    }
                )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert "ai_probability" in data
    assert "analysis_details" in data
    assert data["ai_probability"] == 0.85
    assert data["analysis_details"]["kobert_score"] == 0.85
    assert data["analysis_details"]["similarity_score"] == 0.0


@pytest.mark.asyncio
async def test_analyze_empty_content():
    """빈 콘텐츠 요청 시 422 Unprocessable Entity를 반환합니다."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/analyze",
            json={
                "title": "제목만 있음",
                "content": ""
            }
        )
    
    # Pydantic 검증 실패로 422 반환 (min_length 제약)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_analyze_kobert_error():
    """KoBERT 모듈 오류 시 500 Internal Server Error를 반환합니다."""
    # KoBERT 모듈에서 예외 발생 시뮬레이션
    with patch('kobert_analyzer.calculate_kobert_score', side_effect=RuntimeError("모델 로드 실패")):
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/analyze",
                json={
                    "title": "테스트",
                    "content": "충분히 긴 콘텐츠입니다. 최소 20자 이상이어야 합니다."
                }
            )
    
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "내부 분석 모듈" in response.json()["detail"]


@pytest.mark.asyncio
async def test_analyze_db_save_failure():
    """DB 저장 실패 시에도 분석 결과는 반환합니다 (무시하고 계속)."""
    with patch('kobert_analyzer.calculate_kobert_score', return_value=0.75):
        # DB 저장 시 예외 발생
        with patch('crud.create_analysis_record', side_effect=Exception("DB 연결 실패")):
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/analyze",
                    json={
                        "title": "제목",
                        "content": "본문 내용입니다. 충분히 길게 작성했습니다."
                    }
                )
    
    # DB 저장 실패는 무시하고 200 반환
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["ai_probability"] == 0.75


@pytest.mark.asyncio
async def test_analyze_minimum_valid_input():
    """최소 유효 입력(title 5자, content 20자)으로 정상 동작합니다."""
    with patch('kobert_analyzer.calculate_kobert_score', return_value=0.5):
        with patch('crud.create_analysis_record', new_callable=AsyncMock):
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/analyze",
                    json={
                        "title": "최소제목",  # 5자
                        "content": "최소 20자 이상의 본문 내용"  # 20자 이상
                    }
                )
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["ai_probability"] == 0.5
