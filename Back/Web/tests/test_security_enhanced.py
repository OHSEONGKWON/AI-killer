"""
보안 및 인증 테스트 (JWT, bcrypt, OAuth)
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from jose import jwt

from Web.security import verify_password, get_password_hash, create_access_token
from Web.config import settings


class TestPasswordHashing:
    """비밀번호 해싱 및 검증 테스트"""
    
    def test_hash_password_is_secure(self):
        """해시된 비밀번호는 평문과 다르고 매번 다른 값이어야 함"""
        password = "SecurePassword123!"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        assert hash1 != password
        assert hash2 != password
        assert hash1 != hash2  # 매번 다른 salt 사용
    
    def test_verify_password_correct(self):
        """올바른 비밀번호는 검증 성공"""
        password = "MyPassword123!"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """잘못된 비밀번호는 검증 실패"""
        password = "MyPassword123!"
        wrong_password = "WrongPassword123!"
        hashed = get_password_hash(password)
        
        assert verify_password(wrong_password, hashed) is False
    
    def test_long_password_truncation(self):
        """72자 이상의 비밀번호는 정확히 처리됨 (bcrypt 72바이트 제한)"""
        # 72자를 초과하는 비밀번호
        long_password = "A" * 100
        hashed = get_password_hash(long_password)
        
        # 처음 72자만 매치되어야 함
        assert verify_password(long_password, hashed) is True
        
        # 72자보다 짧지만 다른 비밀번호는 매치되지 않음
        short_password = "A" * 71
        assert verify_password(short_password, hashed) is False


class TestJWTToken:
    """JWT 토큰 생성 및 검증 테스트"""
    
    def test_create_token(self):
        """토큰 생성 테스트"""
        data = {"sub": "user123", "email": "test@example.com"}
        token = create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
        assert token.count('.') == 2  # JWT는 3개 부분으로 구성
    
    def test_token_contains_data(self):
        """토큰 내 페이로드 검증"""
        user_id = "user123"
        email = "test@example.com"
        data = {"sub": user_id, "email": email}
        token = create_access_token(data)
        
        # 토큰 디코딩
        decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        assert decoded["sub"] == user_id
        assert decoded["email"] == email
    
    def test_token_has_expiry(self):
        """토큰에 만료 시간이 포함되어야 함"""
        data = {"sub": "user123"}
        token = create_access_token(data)
        
        decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        assert "exp" in decoded
        # 만료 시간은 향후여야 함
        exp_time = datetime.utcfromtimestamp(decoded["exp"])
        assert exp_time > datetime.utcnow()
    
    def test_token_expiry_matches_setting(self):
        """토큰 만료 시간이 설정값과 일치"""
        before = datetime.utcnow()
        data = {"sub": "user123"}
        token = create_access_token(data)
        after = datetime.utcnow()
        
        decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
        exp_time = datetime.utcfromtimestamp(decoded["exp"])
        
        # 만료 시간이 대략 ACCESS_TOKEN_EXPIRE_MINUTES 후여야 함
        expected_min = before + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES - 1)
        expected_max = after + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES + 1)
        
        assert expected_min <= exp_time <= expected_max
    
    def test_invalid_token_fails_verification(self):
        """유효하지 않은 토큰은 검증 실패"""
        invalid_token = "invalid.token.here"
        
        with pytest.raises(Exception):  # JWT 예외
            jwt.decode(invalid_token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
    
    def test_token_with_wrong_key_fails(self):
        """다른 키로 검증하면 실패"""
        data = {"sub": "user123"}
        token = create_access_token(data)
        
        with pytest.raises(Exception):
            jwt.decode(token, "wrong_secret_key", algorithms=[settings.ALGORITHM])
