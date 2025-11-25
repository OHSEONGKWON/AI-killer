# main.py
"""
FastAPI 메인 엔트리 포인트.

역할:
- FastAPI 앱 생성 및 전역 미들웨어(CORS) 설정
- 서버 시작 시점에 SQLModel 메타데이터로 테이블 생성
- 버전별 라우터(v1)를 앱에 등록하여 엔드포인트 제공
- 로깅 시스템 초기화

주의:
- 비즈니스 로직이나 엔드포인트 구현은 api/v1/* 라우터 파일로 분리합니다.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel

from .database import engine
from .api.v1 import router as api_v1_router
from .logging_config import setup_logging, get_logger
from .config import validate_required_settings

# 로그5 초기화 (환경변수 LOG_LEVEL, JSON_LOGS, SENTRY_DSN 사용)
setup_logging()
logger = get_logger(__name__)


app = FastAPI(title="블로그/에세이 AI 작성 검증 API")

# --- 🔽 프론트엔드 연결을 위한 CORS 설정 ---
# 프론트 개발 서버 주소를 여기 배열에 추가하면 됩니다.
origins = [
    "http://localhost:8080",     # Vue 개발 서버 기본 주소
    "http://localhost:8081",     # Vue 개발 서버 대체 포트
    "http://172.16.1.219:8080",
    "http://172.20.10.2:8081"    # 네트워크 주소
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
    """애플리케이션 시작 시 초기화 작업."""
    logger.info("서버 시작 중...", extra={"app_title": app.title})
    
    # 환경 변수 검증
    warnings = validate_required_settings()
    if warnings:
        logger.warning("환경 변수 경고:")
        for warning in warnings:
            logger.warning(f"  {warning}")
    
    # 비동기 엔진 컨텍스트에서 메타데이터 기반 테이블 생성
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    logger.info("데이터베이스 테이블 생성 완료")


@app.on_event("shutdown")
async def on_shutdown():
    """애플리케이션 종료 시 정리 작업."""
    logger.info("서버 종료 중...")
    await engine.dispose()
    logger.info("데이터베이스 연결 정리 완료")


# 버전 라우터 등록 (모든 v1 엔드포인트는 /api/v1/* 경로로 노출)
app.include_router(api_v1_router)