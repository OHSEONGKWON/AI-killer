"""
데이터 액세스 레이어(CRUD).

주의:
- 비즈니스 로직은 라우터 또는 서비스 계층에서 처리하고,
  이 모듈은 DB 읽기/쓰기 책임만 가집니다.
"""

from typing import List
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, delete

from . import models, security

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