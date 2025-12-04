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

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlmodel import SQLModel

from .database import engine
from .api.v1 import router as api_v1_router
from .logging_config import setup_logging, get_logger
from .config import validate_required_settings, settings
from .exceptions import AIServiceError, SafetyBlockError, APIKeyError, QuotaExceededError

# 로그5 초기화 (환경변수 LOG_LEVEL, JSON_LOGS, SENTRY_DSN 사용)
setup_logging()
logger = get_logger(__name__)


app = FastAPI(
    title="AI-killer API",
    description="한국어 텍스트 AI 작성 검증 서비스 - 문법, 표절, 유사도 검사",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# --- 전역 예외 핸들러 ---
@app.exception_handler(SafetyBlockError)
async def safety_block_exception_handler(request: Request, exc: SafetyBlockError):
    """Gemini SAFETY 차단 예외 처리."""
    logger.warning(f"Safety block occurred: {exc.message}", extra={"detail": exc.detail})
    return JSONResponse(
        status_code=400,
        content={"detail": exc.message, "error_type": "safety_block"}
    )

@app.exception_handler(APIKeyError)
async def api_key_exception_handler(request: Request, exc: APIKeyError):
    """API 키 오류 예외 처리."""
    logger.error(f"API key error: {exc.message}")
    return JSONResponse(
        status_code=500,
        content={"detail": exc.message, "error_type": "api_key_error"}
    )

@app.exception_handler(QuotaExceededError)
async def quota_exceeded_exception_handler(request: Request, exc: QuotaExceededError):
    """API 할당량 초과 예외 처리."""
    logger.warning(f"Quota exceeded: {exc.message}")
    return JSONResponse(
        status_code=429,
        content={"detail": exc.message, "error_type": "quota_exceeded"}
    )

@app.exception_handler(AIServiceError)
async def ai_service_exception_handler(request: Request, exc: AIServiceError):
    """AI 서비스 공통 예외 처리."""
    logger.error(f"AI service error: {exc.message}", extra={"detail": exc.detail})
    return JSONResponse(
        status_code=503,
        content={"detail": exc.message or "AI 서비스 일시적 오류", "error_type": "ai_service_error"}
    )

# --- 🔽 프론트엔드 연결을 위한 CORS 설정 ---
# 환경에 따라 동적으로 CORS origins 설정
def get_cors_origins() -> list[str]:
    """CORS 허용 origin 목록을 환경에 따라 반환합니다."""
    environment = settings.ENVIRONMENT
    frontend_url = settings.FRONTEND_URL
    
    # 기본 origin
    origins = [
        "http://localhost:8080",      # Vue 개발 서버 기본 주소
        "http://localhost:8081",      # Vue 개발 서버 대체 포트
        "http://127.0.0.1:8080",      # localhost IPv4
        frontend_url,                 # 환경 변수에서 설정한 프론트엔드 URL
    ]
    
    # 프로덕션 환경: 특정 도메인만 허용
    if environment == "production":
        origins = [frontend_url]  # 프로덕션은 설정된 URL만 허용
        logger.warning(f"프로덕션 환경: CORS origin을 {frontend_url}로만 제한합니다")
    else:
        # 개발 환경: 추가 네트워크 주소 허용 (선택사항)
        origins.extend([
            "http://172.16.1.219:8080",
            "http://172.20.10.2:8081"
        ])
        logger.info(f"개발 환경: CORS origins = {origins}")
    
    # 중복 제거
    return list(set(origins))


# 초기 CORS 설정 (고정값으로 시작)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://localhost:8081",
        "http://127.0.0.1:8080",
        settings.FRONTEND_URL or "http://localhost:8080"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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