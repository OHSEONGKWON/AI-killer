"""
환경 설정 로더.

역할:
- pydantic-settings로 .env 값을 읽어 Settings 객체를 구성합니다.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """프로젝트에서 사용하는 환경 변수 정의.

    - .env 파일 또는 OS 환경변수에서 값을 읽습니다.
    """
    KAKAO_REST_API_KEY: str | None = None
    KAKAO_REDIRECT_URI: str | None = None
    JWT_SECRET_KEY: str | None = None
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # 외부 API 설정 (선택사항)
    PLAGIARISM_API_URL: str | None = None
    PLAGIARISM_API_KEY: str | None = None
    GRAMMAR_API_URL: str | None = None
    GRAMMAR_API_KEY: str | None = None

    class Config:
        env_file = ".env"  # .env 파일에서 환경변수를 읽어옴


# 전역 settings 인스턴스 (import하여 사용)
settings = Settings()