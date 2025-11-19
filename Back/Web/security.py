"""
보안 유틸리티(security).

역할:
- 비밀번호 해시/검증
- JWT 액세스 토큰 발급
"""

from datetime import datetime, timedelta
from jose import JWTError, jwt
import bcrypt
from .config import settings


def _truncate_to_72_bytes(password: str | bytes) -> bytes:
    """bcrypt 입력은 72바이트까지만 유효하므로 바이트 기준으로 잘라 반환합니다."""
    if isinstance(password, str):
        raw = password.encode("utf-8")
    else:
        raw = password
    return raw[:72]


def verify_password(plain_password, hashed_password):
    """평문 비밀번호와 해시를 비교 검증합니다."""
    plain_b = _truncate_to_72_bytes(plain_password)
    hashed_b = hashed_password.encode("utf-8") if isinstance(hashed_password, str) else hashed_password
    return bcrypt.checkpw(plain_b, hashed_b)


def get_password_hash(password):
    """비밀번호 해시를 생성합니다."""
    pw_b = _truncate_to_72_bytes(password)
    # 기본 라운드 사용; 필요 시 환경설정으로 분리 가능
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pw_b, salt)
    return hashed.decode("utf-8")


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