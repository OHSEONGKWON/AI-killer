from typing import Optional, List
from sqlmodel import Field, SQLModel

# --- 분석 API 모델 ---
class AnalysisRequest(SQLModel):
    title: str
    abstract: str

class AnalysisDetails(SQLModel):
    kobert_score: float
    similarity_score: float

class AnalysisResponse(SQLModel):
    ai_probability: float
    analysis_details: AnalysisDetails

# --- 인증/유저 API 모델 ---
class UserBase(SQLModel):
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True)

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_admin: bool

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: Optional[str] = Field(default=None)
    kakao_id: Optional[int] = Field(default=None, unique=True, index=True)
    is_admin: bool = Field(default=False)

class KakaoCode(SQLModel):
    code: str

class Token(SQLModel):
    access_token: str
    token_type: str