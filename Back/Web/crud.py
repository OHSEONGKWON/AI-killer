from typing import List
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, delete

from . import models, security

# --- User CRUD ---
async def get_user(db: AsyncSession, user_id: int):
    """ID로 단일 사용자를 가져옵니다."""
    user = await db.get(models.User, user_id)
    return user

async def get_user_by_username(db: AsyncSession, username: str):
    statement = select(models.User).where(models.User.username == username)
    result = await db.exec(statement)
    return result.first()
    
async def get_user_by_kakao_id(db: AsyncSession, kakao_id: int):
    statement = select(models.User).where(models.User.kakao_id == kakao_id)
    result = await db.exec(statement)
    return result.first()

async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[models.User]:
    """전체 사용자 목록을 페이지네이션하여 가져옵니다."""
    statement = select(models.User).offset(skip).limit(limit)
    result = await db.exec(statement)
    return result.all()

async def create_kakao_user(db: AsyncSession, user_info: dict) -> models.User:
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
    """사용자를 삭제합니다."""
    user_to_delete = await db.get(models.User, user_id)
    if user_to_delete:
        await db.delete(user_to_delete)
        await db.commit()
        return True
    return False