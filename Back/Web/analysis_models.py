from typing import Optional
from sqlmodel import SQLModel, Field

class AnalysisRecord(SQLModel, table=True):
    """사용자가 제출한 텍스트와 분석 결과를 저장하는 테이블 모델."""
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: str
    ai_probability: float
    kobert_score: float
    similarity_score: float
    perplexity_score: Optional[float] = 0.0
    burstiness_score: Optional[float] = 0.0
    created_at: Optional[str] = None
