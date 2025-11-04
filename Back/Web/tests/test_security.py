"""
security.py 모듈 단위 테스트.

테스트 항목:
- 비밀번호 해시 생성 및 검증
- JWT 토큰 생성 및 디코딩
- 토큰 만료 확인
"""

import pytest
from datetime import datetime, timedelta
from jose import jwt, JWTError

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import security
import config
from security import verify_password, get_password_hash, create_access_token
from config import settings


def test_password_hashing():
    """비밀번호 해시 생성 및 검증이 정상 동작합니다."""
    plain_password = "secure_password_123"
    hashed = get_password_hash(plain_password)
    
    # 해시는 원본과 달라야 함
    assert hashed != plain_password
    
    # 검증 성공
    assert verify_password(plain_password, hashed) is True
    
    # 잘못된 비밀번호는 실패
    assert verify_password("wrong_password", hashed) is False


def test_password_hash_uniqueness():
    """같은 비밀번호도 매번 다른 해시를 생성합니다 (salt 사용)."""
    password = "same_password"
    hash1 = get_password_hash(password)
    hash2 = get_password_hash(password)
    
    # bcrypt는 salt를 사용하므로 해시가 달라야 함
    assert hash1 != hash2
    
    # 하지만 둘 다 검증은 성공
    assert verify_password(password, hash1) is True
    assert verify_password(password, hash2) is True


def test_create_access_token():
    """JWT 액세스 토큰 생성이 정상 동작합니다."""
    data = {"sub": "testuser"}
    token = create_access_token(data)
    
    # 토큰은 문자열이어야 함
    assert isinstance(token, str)
    assert len(token) > 0
    
    # 토큰 디코딩 확인
    payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["sub"] == "testuser"
    assert "exp" in payload


def test_jwt_token_expiration():
    """JWT 토큰에 만료 시간이 올바르게 설정됩니다."""
    data = {"sub": "testuser"}
    token = create_access_token(data)
    
    payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
    exp_timestamp = payload["exp"]
    
    # 만료 시간은 현재 시간 + ACCESS_TOKEN_EXPIRE_MINUTES
    expected_exp = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    actual_exp = datetime.fromtimestamp(exp_timestamp)
    
    # 1분 오차 이내로 확인 (테스트 실행 시간 고려)
    assert abs((actual_exp - expected_exp).total_seconds()) < 60


def test_jwt_token_invalid_signature():
    """잘못된 시크릿 키로 디코딩 시 예외가 발생합니다."""
    data = {"sub": "testuser"}
    token = create_access_token(data)
    
    # 잘못된 시크릿 키로 디코딩 시도
    with pytest.raises(JWTError):
        jwt.decode(token, "wrong_secret_key", algorithms=[settings.ALGORITHM])


def test_jwt_token_with_additional_claims():
    """추가 클레임을 포함한 JWT 토큰 생성이 정상 동작합니다."""
    data = {
        "sub": "testuser",
        "role": "admin",
        "permissions": ["read", "write"]
    }
    token = create_access_token(data)
    
    payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["sub"] == "testuser"
    assert payload["role"] == "admin"
    assert payload["permissions"] == ["read", "write"]
