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
    """분석 요청 바디: 제목, 본문 텍스트, 텍스트 유형."""
    title: str = Field(max_length=200, description="제목")
    content: str = Field(min_length=10, max_length=10000, description="분석할 텍스트 (10~10000자)")
    text_type: Optional[str] = Field(default="paper", description="텍스트 유형 (paper, essay, blog, article, news 등)")

class AnalysisDetails(SQLModel):
    """세부 점수: 4가지 AI 검출 지표."""
    kobert_score: float  # KoBERT AI 분류 확률 (0.0~1.0)
    similarity_score: float  # SBERT 코사인 유사도 (0.0~1.0)
    perplexity_score: Optional[float] = 0.0  # Perplexity 점수 (0.0~1.0)
    burstiness_score: Optional[float] = 0.0  # Burstiness 점수 (0.0~1.0)

class AnalysisResponse(SQLModel):
    """분석 응답: 최종 확률과 세부 점수."""
    ai_probability: float  # 가중치 적용된 최종 AI 확률
    analysis_details: AnalysisDetails

# --- 인증/유저 API 모델 ---
class UserBase(SQLModel):
    """유저 공통 필드: username/email은 유니크 인덱스."""
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True)

class UserCreate(SQLModel):
    """회원가입 시 사용하는 바디 모델(패스워드 포함)."""
    email: str = Field(description="이메일 주소")
    password: str = Field(min_length=6, max_length=72, description="비밀번호 (6~72자)")

class UserUpdate(SQLModel):
    """내 정보 수정 요청."""
    username: Optional[str] = Field(default=None, description="사용자명(닉네임)")

class PasswordChange(SQLModel):
    """비밀번호 변경 요청."""
    current_password: str = Field(description="현재 비밀번호")
    new_password: str = Field(min_length=6, max_length=72, description="새 비밀번호 (6~72자)")

class UserResponse(UserBase):
    """클라이언트에 반환할 유저 정보 스키마."""
    id: int
    is_admin: bool
    active: bool

class User(UserBase, table=True):
    """DB 테이블 모델. 실제 저장되는 필드들을 포함."""
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: Optional[str] = Field(default=None)
    kakao_id: Optional[int] = Field(default=None, unique=True, index=True)
    is_admin: bool = Field(default=False)
    active: bool = Field(default=True, index=True)

class UserAdminUpdate(SQLModel):
    """관리자에 의한 사용자 정보 수정 요청."""
    username: Optional[str] = None
    email: Optional[str] = None
    is_admin: Optional[bool] = None
    active: Optional[bool] = None

class UserStatusUpdate(SQLModel):
    """사용자 활성/비활성 상태 변경 요청. 값이 없으면 토글로 처리."""
    active: Optional[bool] = None

class KakaoCode(SQLModel):
    """카카오 인증 콜백에서 전달되는 code 값."""
    code: str

class Token(SQLModel):
    """JWT 액세스 토큰 응답."""
    access_token: str
    token_type: str

# --- 표절 검사 API 모델 ---
class MatchedSource(SQLModel):
    """유사한 소스 정보."""
    source_url: Optional[str] = None
    source_title: Optional[str] = None
    similarity_score: float
    matched_text: str

class HighlightSegment(SQLModel):
    """표절 하이라이트 구간."""
    target_text: str
    type: str  # "EXACT" | "SUSPICIOUS"
    reason: str

class PlagiarismRequest(SQLModel):
    """표절 검사 요청."""
    content: str = Field(min_length=10, max_length=10000, description="검사할 텍스트")

class PlagiarismResponse(SQLModel):
    """표절 검사 응답."""
    suspected_source: str  # 추정 출처
    source_url: Optional[str] = None  # 출처 URL
    original_found: bool  # 원본 발견 여부
    overall_similarity_score: int  # 유사도 점수 (0~100)
    highlight_segments: List[HighlightSegment]  # 하이라이트 구간
    highlighted_html: Optional[str] = None  # HTML 포맷 하이라이트
    matched_sources: List[MatchedSource] = []  # 기본값 빈 리스트
    is_plagiarized: bool = False  # 기본값 False

# --- 문법 검사 API 모델 ---
class DiffExplanation(SQLModel):
    """수정 내역 상세."""
    original: str  # 원본 텍스트
    changed: str  # 수정된 텍스트
    reason: str  # 수정 이유

class VocabularySuggestion(SQLModel):
    """어휘 추천 정보."""
    word: str  # 원문 단어
    suggestion: str  # 추천 단어
    reason: str  # 추천 이유

class GrammarScore(SQLModel):
    """문법 점수."""
    grammar: int  # 문법 점수 (0~100)
    naturalness: int  # 자연스러움 점수 (0~100)

class GrammarCheckRequest(SQLModel):
    """문법검사 요청."""
    content: str = Field(min_length=1, max_length=10000, description="검사할 텍스트")

class GrammarCheckResponse(SQLModel):
    """문법검사 응답 (Gemini 기반)."""
    original_text: str  # 원문
    corrected_text: str  # 맞춤법 교정된 텍스트
    refined_text: str  # 윤문된 최종 텍스트
    diff_explanation: List[DiffExplanation]  # 수정 내역
    nuance_feedback: str  # 뉘앙스 분석
    vocabulary_suggestions: List[VocabularySuggestion]  # 어휘 추천
    score: GrammarScore  # 점수

# --- 분석 설정 모델 (Admin) ---
class AnalysisConfigBase(SQLModel):
    """분석 설정 공통 필드."""
    text_type: str = Field(index=True, unique=True, description="텍스트 유형 (paper, essay, blog, etc.)")
    description: Optional[str] = Field(default=None, description="설정 설명")
    
    # 4가지 분석 지표 가중치 (합이 1.0이 되도록 권장)
    sbert_weight: float = Field(default=0.25, ge=0.0, le=1.0, description="SBERT 코사인 유사도 가중치")
    kobert_weight: float = Field(default=0.35, ge=0.0, le=1.0, description="KoBERT AI 분류 확률 가중치")
    perplexity_weight: float = Field(default=0.20, ge=0.0, le=1.0, description="Perplexity 가중치")
    burstiness_weight: float = Field(default=0.20, ge=0.0, le=1.0, description="Burstiness 가중치")
    
    # 메타 정보
    is_active: bool = Field(default=True, description="활성화 여부")
    is_default: bool = Field(default=False, description="기본 설정 여부")


class AnalysisConfig(AnalysisConfigBase, table=True):
    """분석 설정 DB 테이블."""
    __tablename__ = "analysis_config"
    
    id: Optional[int] = Field(default=None, primary_key=True)


class AnalysisConfigCreate(AnalysisConfigBase):
    """분석 설정 생성 요청."""
    pass


class AnalysisConfigUpdate(SQLModel):
    """분석 설정 수정 요청 (모든 필드 선택적)."""
    description: Optional[str] = None
    sbert_weight: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    kobert_weight: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    perplexity_weight: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    burstiness_weight: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None


class AnalysisConfigResponse(AnalysisConfigBase):
    """분석 설정 응답."""
    id: int