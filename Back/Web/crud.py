"""
데이터 액세스 레이어(CRUD).

주의:
- 비즈니스 로직은 라우터 또는 서비스 계층에서 처리하고,
  이 모듈은 DB 읽기/쓰기 책임만 가집니다.
"""

from typing import List, Optional
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, delete

from . import models, security
from .analysis_models import AnalysisRecord

# --- User CRUD ---
async def get_user(db: AsyncSession, user_id: int):
    """ID로 단일 사용자를 가져옵니다.

    존재하지 않으면 None을 반환합니다.
    """
    user = await db.get(models.User, user_id)
    return user

async def get_user_by_username(db: AsyncSession, username: str):
    """username 인덱스를 활용해 사용자 한 명을 조회합니다."""
    statement = select(models.User).where(models.User.username == username)
    result = await db.exec(statement)
    return result.first()
    
async def get_user_by_kakao_id(db: AsyncSession, kakao_id: int):
    """카카오 ID로 사용자 조회."""
    statement = select(models.User).where(models.User.kakao_id == kakao_id)
    result = await db.exec(statement)
    return result.first()

async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[models.User]:
    """전체 사용자 목록을 페이지네이션하여 가져옵니다."""
    statement = select(models.User).offset(skip).limit(limit)
    result = await db.exec(statement)
    return result.all()

async def create_kakao_user(db: AsyncSession, user_info: dict) -> models.User:
    """카카오에서 받은 간단한 user_info로 사용자 생성.

    실제 서비스에서는 이메일 검증/중복 처리 등 추가 로직이 필요합니다.
    """
    db_user = models.User(
        username=user_info.get('nickname'),
        email=user_info.get('email'),
        kakao_id=user_info.get('id')
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def delete_user(db: AsyncSession, user_id: int):
    """사용자를 삭제합니다. 성공 시 True, 없으면 False 반환."""
    user_to_delete = await db.get(models.User, user_id)
    if user_to_delete:
        await db.delete(user_to_delete)
        await db.commit()
        return True
    return False

# --- AnalysisRecord CRUD ---
async def create_analysis_record(
    db: AsyncSession, 
    *, 
    title: str, 
    content: str, 
    ai_probability: float, 
    kobert_score: float, 
    similarity_score: float, 
    created_at: str = None
) -> AnalysisRecord:
    """분석 결과를 데이터베이스에 저장합니다."""
    record = AnalysisRecord(
        title=title,
        content=content,
        ai_probability=ai_probability,
        kobert_score=kobert_score,
        similarity_score=similarity_score,
        created_at=created_at,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


# --- AnalysisConfig CRUD ---
async def get_analysis_config(db: AsyncSession, text_type: str) -> Optional[models.AnalysisConfig]:
    """텍스트 유형으로 분석 설정을 조회합니다."""
    statement = select(models.AnalysisConfig).where(
        models.AnalysisConfig.text_type == text_type,
        models.AnalysisConfig.is_active == True
    )
    result = await db.exec(statement)
    return result.first()


async def get_default_analysis_config(db: AsyncSession) -> Optional[models.AnalysisConfig]:
    """기본 분석 설정을 조회합니다."""
    statement = select(models.AnalysisConfig).where(
        models.AnalysisConfig.is_default == True,
        models.AnalysisConfig.is_active == True
    )
    result = await db.exec(statement)
    return result.first()


async def get_all_analysis_configs(db: AsyncSession) -> List[models.AnalysisConfig]:
    """모든 분석 설정을 조회합니다."""
    statement = select(models.AnalysisConfig)
    result = await db.exec(statement)
    return result.all()


async def create_analysis_config(
    db: AsyncSession, 
    config: models.AnalysisConfigCreate
) -> models.AnalysisConfig:
    """새로운 분석 설정을 생성합니다."""
    db_config = models.AnalysisConfig.model_validate(config)
    db.add(db_config)
    await db.commit()
    await db.refresh(db_config)
    return db_config


async def update_analysis_config(
    db: AsyncSession,
    text_type: str,
    config_update: models.AnalysisConfigUpdate
) -> Optional[models.AnalysisConfig]:
    """분석 설정을 수정합니다."""
    statement = select(models.AnalysisConfig).where(models.AnalysisConfig.text_type == text_type)
    result = await db.exec(statement)
    db_config = result.first()
    
    if not db_config:
        return None
    
    # 수정된 필드만 업데이트
    update_data = config_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_config, key, value)
    
    await db.commit()
    await db.refresh(db_config)
    return db_config


async def delete_analysis_config(db: AsyncSession, text_type: str) -> bool:
    """분석 설정을 삭제합니다."""
    statement = select(models.AnalysisConfig).where(models.AnalysisConfig.text_type == text_type)
    result = await db.exec(statement)
    config = result.first()
    
    if config:
        await db.delete(config)
        await db.commit()
        return True
    return False
