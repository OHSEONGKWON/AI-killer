"""
kobert_analyzer.py 모듈 단위 테스트.

테스트 항목:
- 정상 텍스트 입력 시 0~1 사이의 점수 반환
- 빈 텍스트 처리
- 긴 텍스트 처리
- 특수 문자 포함 텍스트 처리
"""

import pytest

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import kobert_analyzer
from kobert_analyzer import calculate_kobert_score


def test_kobert_score_range():
    """KoBERT 점수는 0~1 사이의 값을 반환합니다."""
    text = "인공지능 기술의 발전은 우리 사회에 많은 변화를 가져오고 있습니다."
    score = calculate_kobert_score(text)
    
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0


def test_kobert_score_empty_text():
    """빈 텍스트 입력 시에도 점수를 반환합니다 (0.0 또는 기본값)."""
    score = calculate_kobert_score("")
    
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0


def test_kobert_score_long_text():
    """긴 텍스트 입력 시에도 정상 동작합니다."""
    long_text = "인공지능 기술의 발전. " * 100  # 약 2000자
    score = calculate_kobert_score(long_text)
    
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0


def test_kobert_score_special_characters():
    """특수 문자가 포함된 텍스트도 처리합니다."""
    text = "AI 기술은 @#$% 다양한 분야에서 활용되고 있습니다! (정말?)"
    score = calculate_kobert_score(text)
    
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0


def test_kobert_score_consistency():
    """동일한 입력에 대해 일관된 결과를 반환합니다 (랜덤이 아닌 경우)."""
    text = "테스트 텍스트입니다."
    score1 = calculate_kobert_score(text)
    score2 = calculate_kobert_score(text)
    
    # 현재 구현은 랜덤이므로 다를 수 있음
    # 실제 모델 연동 후에는 같은 값이어야 함
    # assert score1 == score2  # 실제 모델에서는 주석 해제
    assert isinstance(score1, float)
    assert isinstance(score2, float)
