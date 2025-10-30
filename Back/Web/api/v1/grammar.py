"""
문법 검사 라우터.

주요 기능:
- 외부 문법검사 API(예: Grammarly API, LanguageTool API 등)를 이용하여 텍스트의 문법 오류 검사
- 오류 구간 하이라이팅 정보 제공 (시작/끝 인덱스, 오류 유형, 교정 제안)
- 시각적 표시와 교정 제안까지 포함

처리 순서:
1) 사용자 텍스트를 외부 API로 전송
2) 응답에서 문법 오류 목록 파싱
3) 각 오류 구간(start_index, end_index)과 교정 제안을 반환

주의:
- 실제 외부 API 키를 config.py에 등록하고, .env 파일로 관리
- 현재는 임시 모의 응답을 반환 (실제 API 연동 전)
"""

from typing import List
from fastapi import APIRouter, HTTPException
import httpx

from ... import models
from ...config import settings

router = APIRouter()


class GrammarError(models.SQLModel):
    """문법 오류 정보."""
    message: str  # 오류 설명
    start_index: int
    end_index: int
    error_type: str  # "spelling", "grammar", "punctuation" 등
    suggestions: List[str]  # 교정 제안 리스트


class GrammarCheckRequest(models.SQLModel):
    """문법검사 요청."""
    content: str


class GrammarCheckResponse(models.SQLModel):
    """문법검사 응답."""
    errors: List[GrammarError]
    total_errors: int
    corrected_text: str | None = None  # (옵션) 자동 교정된 텍스트


async def call_grammar_api(text: str) -> List[GrammarError]:
    """외부 문법검사 API를 호출하여 오류 목록을 반환합니다.
    
    실제 구현 예시:
    - LanguageTool API: https://languagetool.org/http-api/swagger-ui/
    - Grammarly API (비공식): https://github.com/grammarly
    - 네이버 맞춤법 검사기 크롤링 (비추천: 불안정, robots.txt 확인 필요)
    
    현재는 임시 모의 응답.
    """
    # TODO: 실제 외부 API 호출
    # if settings.GRAMMAR_API_URL and settings.GRAMMAR_API_KEY:
    #     async with httpx.AsyncClient() as client:
    #         response = await client.post(
    #             settings.GRAMMAR_API_URL,
    #             json={"text": text},
    #             headers={"Authorization": f"Bearer {settings.GRAMMAR_API_KEY}"}
    #         )
    #         response.raise_for_status()
    #         data = response.json()
    #         # API 응답 파싱...
    
    # 임시 모의 응답
    simulated_errors = [
        GrammarError(
            message="맞춤법 오류: '있다'를 '있다'로 수정",
            start_index=10,
            end_index=12,
            error_type="spelling",
            suggestions=["있다", "이따"]
        ),
        GrammarError(
            message="문법 오류: 주어-동사 불일치",
            start_index=25,
            end_index=30,
            error_type="grammar",
            suggestions=["입니다", "이다"]
        )
    ]
    
    return simulated_errors


@router.post("/grammar/check", response_model=GrammarCheckResponse, summary="문법 검사")
async def check_grammar(request: GrammarCheckRequest):
    """입력 텍스트의 문법 오류를 외부 API로 검사합니다.
    
    처리 순서:
    1) 외부 문법검사 API 호출
    2) 오류 목록 파싱
    3) 각 오류의 위치와 교정 제안 반환
    
    Args:
        content: 검사할 텍스트
    
    Returns:
        errors: 문법 오류 목록
        total_errors: 총 오류 개수
        corrected_text: 자동 교정된 텍스트 (옵션)
    """
    try:
        errors = await call_grammar_api(request.content)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"문법검사 API 호출 중 오류 발생: {str(e)}"
        )
    
    # (옵션) 자동 교정 텍스트 생성
    # corrected_text = request.content
    # for error in sorted(errors, key=lambda e: e.start_index, reverse=True):
    #     if error.suggestions:
    #         corrected_text = (
    #             corrected_text[:error.start_index] +
    #             error.suggestions[0] +
    #             corrected_text[error.end_index:]
    #         )
    
    return GrammarCheckResponse(
        errors=errors,
        total_errors=len(errors),
        corrected_text=None  # 자동 교정 기능 추가 시 활성화
    )
