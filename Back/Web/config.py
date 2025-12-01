"""
환경 설정 로더.

역할:
- pydantic-settings로 .env 값을 읽어 Settings 객체를 구성합니다.
"""

from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import field_validator, ValidationError
import sys


class Settings(BaseSettings):
    """프로젝트에서 사용하는 환경 변수 정의.

    - .env 파일 또는 OS 환경변수에서 값을 읽습니다.
    """
    # 필수 환경변수
    JWT_SECRET_KEY: str
    GEMINI_API_KEY: str
    
    # 선택적 환경변수
    KAKAO_REST_API_KEY: str | None = None
    KAKAO_REDIRECT_URI: str | None = None
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    FRONTEND_URL: str = "http://localhost:8080"
    
    # OpenAI API 설정 (선택사항)
    OPENAI_API_KEY: str | None = None
    
    # 웹 검색 API (선택사항 - 실시간 표절 검사용)
    SERPER_API_KEY: str | None = None
    GOOGLE_SEARCH_API_KEY: str | None = None
    GOOGLE_SEARCH_ENGINE_ID: str | None = None
    
    PLAGIARISM_API_URL: str | None = None
    PLAGIARISM_API_KEY: str | None = None
    GRAMMAR_API_URL: str | None = None
    GRAMMAR_API_KEY: str | None = None
    
    # 로깅 설정 (선택사항)
    LOG_LEVEL: str = "INFO"
    JSON_LOGS: str = "0"
    ENVIRONMENT: str = "development"
    
    @field_validator("JWT_SECRET_KEY")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        """JWT_SECRET_KEY는 최소 32자 이상이어야 합니다."""
        if len(v) < 32:
            raise ValueError(
                "JWT_SECRET_KEY must be at least 32 characters long for security. "
                "Generate one with: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
            )
        return v
    
    @field_validator("GEMINI_API_KEY")
    @classmethod
    def validate_gemini_key(cls, v: str) -> str:
        """GEMINI_API_KEY가 유효한 형식인지 검증합니다."""
        if not v or len(v) < 10:
            raise ValueError(
                "GEMINI_API_KEY is required. Get one from: https://ai.google.dev/"
            )
        return v

    class Config:
        # .env 파일 경로를 프로젝트 루트로 지정
        env_file = Path(__file__).parent.parent.parent / ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = True


# 전역 settings 인스턴스 (import하여 사용)
try:
    settings = Settings()
except ValidationError as e:
    print("\n❌ 환경 변수 검증 실패:")
    for error in e.errors():
        field = error['loc'][0]
        msg = error['msg']
        print(f"  - {field}: {msg}")
    print("\n💡 .env 파일을 확인하거나 다음 명령으로 키를 생성하세요:")
    print("  python -c \"import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(32))\"")
    print("  GEMINI_API_KEY는 https://ai.google.dev/ 에서 발급받으세요.\n")
    sys.exit(1)


def validate_required_settings():
    """선택적 환경 변수 검증.
    
    서버 시작 시 호출하여 선택적 설정 누락을 알립니다.
    필수 환경변수(JWT_SECRET_KEY, GEMINI_API_KEY)는 Settings 초기화 시 자동 검증됩니다.
    """
    warnings = []
    
    if not settings.KAKAO_REST_API_KEY:
        warnings.append("🟡 KAKAO_REST_API_KEY가 설정되지 않았습니다. 카카오 로그인을 사용할 수 없습니다.")
    
    if not settings.OPENAI_API_KEY:
        warnings.append("🟡 OPENAI_API_KEY가 설정되지 않았습니다. (현재 사용되지 않음)")
    
    if not settings.PLAGIARISM_API_URL:
        warnings.append("ℹ️  외부 표절 API가 설정되지 않았습니다. Gemini API만 사용합니다.")
    
    return warnings