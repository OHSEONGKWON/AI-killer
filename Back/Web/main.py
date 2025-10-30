# main.py
"""
FastAPI 메인 엔트리 포인트.

역할:
- FastAPI 앱 생성 및 전역 미들웨어(CORS) 설정
- 서버 시작 시점에 SQLModel 메타데이터로 테이블 생성
- 버전별 라우터(v1)를 앱에 등록하여 엔드포인트 제공

주의:
- 비즈니스 로직이나 엔드포인트 구현은 api/v1/* 라우터 파일로 분리합니다.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel

from .database import engine
from .api.v1 import router as api_v1_router
from .analysis_models import AnalysisRecord  # DB 테이블 등록


app = FastAPI(title="블로그/에세이 AI 작성 검증 API")

# --- 🔽 프론트엔드 연결을 위한 CORS 설정 ---
# 프론트 개발 서버 주소를 여기 배열에 추가하면 됩니다.
origins = [
    "http://localhost:8080",  # Vue 개발 서버 기본 주소
    "http://127.0.0.1:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # 어떤 Origin(출처)을 허용할지
    allow_credentials=True,      # 쿠키 등 인증 정보를 허용할지
    allow_methods=["*"],         # 허용할 HTTP 메서드
    allow_headers=["*"],         # 허용할 헤더
)


# 서버 시작 시 DB 테이블 자동 생성
@app.on_event("startup")
async def on_startup():
    # 비동기 엔진 컨텍스트에서 메타데이터 기반 테이블 생성
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


# 버전 라우터 등록 (모든 v1 엔드포인트는 /api/v1/* 경로로 노출)
app.include_router(api_v1_router)