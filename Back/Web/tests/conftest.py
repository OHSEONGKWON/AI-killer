"""
테스트 설정 파일 (conftest.py).

pytest가 자동으로 로드하는 공통 설정 및 fixture 정의.
"""

import pytest
import sys
import os

# 테스트 시 상위 디렉터리의 모듈을 import할 수 있도록 경로 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture
def sample_analysis_request():
    """분석 요청 테스트용 샘플 데이터."""
    return {
        "title": "인공지능의 미래",
        "content": "인공지능 기술은 우리 사회의 많은 분야에서 혁신을 가져오고 있습니다. "
                   "특히 자연어 처리, 컴퓨터 비전, 음성 인식 등의 분야에서 놀라운 발전을 보이고 있습니다."
    }


@pytest.fixture
def sample_user_data():
    """사용자 테스트용 샘플 데이터."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "secure_password_123"
    }
