"""
Pydantic/SQLModel 스키마 정의.

역할:
- 요청/응답 바디 모델(Analysis*, Token 등)
- DB 테이블 모델(User) 및 공통 베이스(UserBase)
"""

from typing import Optional, List
from sqlmodel import Field, SQLModel

# --- 분석 API 모델 ---
class AnalysisRequest(SQLModel):
    """분석 요청 바디: 제목과 본문 텍스트."""
    title: str
    content: str  # 블로그/에세이 본문

class AnalysisDetails(SQLModel):
    """세부 점수: 모듈별 점수 구성."""
    kobert_score: float
    similarity_score: float

class AnalysisResponse(SQLModel):
    """분석 응답: 최종 확률과 세부 점수."""
    ai_probability: float
    analysis_details: AnalysisDetails

# --- 인증/유저 API 모델 ---
class UserBase(SQLModel):
    """유저 공통 필드: username/email은 유니크 인덱스."""
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True)

class UserCreate(UserBase):
    """회원가입 시 사용하는 바디 모델(패스워드 포함)."""
    password: str

class UserResponse(UserBase):
    """클라이언트에 반환할 유저 정보 스키마."""
    id: int
    is_admin: bool

class User(UserBase, table=True):
    """DB 테이블 모델. 실제 저장되는 필드들을 포함."""
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: Optional[str] = Field(default=None)
    kakao_id: Optional[int] = Field(default=None, unique=True, index=True)
    is_admin: bool = Field(default=False)

class KakaoCode(SQLModel):
    """카카오 인증 콜백에서 전달되는 code 값."""
    code: str

class Token(SQLModel):
    """JWT 액세스 토큰 응답."""
    access_token: str
    token_type: str

# --- 하이라이팅 API 모델 ---
class HighlightSegment(SQLModel):
    """하이라이팅할 텍스트 구간 정보."""
    text: str
    start_index: int
    end_index: int
    ai_score: float  # 해당 구간의 AI-like 점수 (0~1)
    reason: str  # 왜 AI-like인지 설명

class HighlightRequest(SQLModel):
    """하이라이팅 요청 바디."""
    content: str

class HighlightResponse(SQLModel):
    """하이라이팅 응답: AI-like 구간 목록."""
    segments: List[HighlightSegment]
    overall_ai_ratio: float  # 전체 중 AI-like 비율

# --- 어시스턴트 API 모델 ---
class ImprovementSuggestion(SQLModel):
    """개선 제안 항목."""
    original_text: str
    improved_text: str
    improvement_type: str  # "creativity", "tone", "clarity" 등
    explanation: str

class AssistantRequest(SQLModel):
    """글쓰기 어시스턴트 요청."""
    content: str
    improvement_focus: Optional[str] = "all"  # "creativity", "tone", "clarity", "all"

class AssistantResponse(SQLModel):
    """글쓰기 어시스턴트 응답."""
    suggestions: List[ImprovementSuggestion]
    overall_score: float  # 현재 글의 창의성/인간성 점수

# --- 표절 검사 API 모델 ---
class MatchedSource(SQLModel):
    """유사한 소스 정보."""
    source_url: Optional[str] = None
    source_title: Optional[str] = None
    similarity_score: float
    matched_text: str

class PlagiarismRequest(SQLModel):
    """표절 검사 요청."""
    content: str
    check_web: bool = True  # 웹 검색 여부
    check_internal: bool = False  # 내부 저장소 검사 여부

class PlagiarismResponse(SQLModel):
    """표절 검사 응답."""
    overall_similarity: float  # 전체 유사도 점수
    matched_sources: List[MatchedSource]
    is_plagiarized: bool  # 임계치 기준 표절 여부