from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    KAKAO_REST_API_KEY: str
    KAKAO_REDIRECT_URI: str
    JWT_SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    class Config:
        env_file = ".env" # .env 파일에서 환경변수를 읽어옴

settings = Settings()