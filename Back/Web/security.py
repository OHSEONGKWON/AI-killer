"""
보안 유틸리티(security).

역할:
- 비밀번호 해시/검증
- JWT 액세스 토큰 발급
"""

from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from .config import settings

# bcrypt 기반 해시 컨텍스트
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    """평문 비밀번호와 해시를 비교 검증합니다."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """비밀번호 해시를 생성합니다."""
    return pwd_context.hash(password)


def create_access_token(data: dict):
    """JWT 액세스 토큰을 생성합니다.

    - data: 토큰 페이로드(sub 등)를 담은 dict
    - 만료 시간(exp)은 설정값 기준 분 단위로 추가됩니다.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt