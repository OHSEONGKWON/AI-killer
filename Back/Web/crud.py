"""
데이터 액세스 레이어(CRUD).

주의:
- 비즈니스 로직은 라우터 또는 서비스 계층에서 처리하고,
  이 모듈은 DB 읽기/쓰기 책임만 가집니다.
"""

from typing import List, Optional
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, delete
from sqlalchemy import or_

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
    result = await db.execute(statement)
    return result.scalars().first()

async def get_user_by_email(db: AsyncSession, email: str):
    """email로 사용자 한 명을 조회합니다."""
    statement = select(models.User).where(models.User.email == email)
    result = await db.execute(statement)
    return result.scalars().first()
    
async def get_user_by_kakao_id(db: AsyncSession, kakao_id: int):
    """카카오 ID로 사용자 조회."""
    statement = select(models.User).where(models.User.kakao_id == kakao_id)
    result = await db.execute(statement)
    return result.scalars().first()

async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[models.User]:
    """전체 사용자 목록을 페이지네이션하여 가져옵니다."""
    statement = select(models.User).offset(skip).limit(limit)
    result = await db.execute(statement)
    return list(result.scalars().all())

async def search_users(
    db: AsyncSession,
    *,
    q: Optional[str] = None,
    is_admin: Optional[bool] = None,
    active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[models.User]:
    """필터/검색 조건으로 사용자 목록 조회."""
    stmt = select(models.User)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(or_(models.User.username.like(like), models.User.email.like(like)))
    if is_admin is not None:
        stmt = stmt.where(models.User.is_admin == is_admin)
    if active is not None:
        stmt = stmt.where(models.User.active == active)
    stmt = stmt.offset(skip).limit(limit)
    res = await db.execute(stmt)
    return list(res.scalars().all())

async def create_kakao_user(db: AsyncSession, user_info: dict) -> models.User:
    """카카오에서 받은 간단한 user_info로 사용자 생성.

    실제 서비스에서는 이메일 검증/중복 처리 등 추가 로직이 필요합니다.
    """
    db_user = models.User(
        username=user_info.get('nickname'),
        email=user_info.get('email'),
        kakao_id=user_info.get('id'),
        is_admin=False,
        active=True
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

async def update_user_admin(
    db: AsyncSession,
    *,
    user_id: int,
    update: models.UserAdminUpdate,
) -> Optional[models.User]:
    """관리자에 의한 사용자 정보 갱신."""
    user = await db.get(models.User, user_id)
    if not user:
        return None

    data = update.model_dump(exclude_unset=True)
    # username/email uniqueness checks
    if 'username' in data and data['username'] and data['username'] != user.username:
        exists = await get_user_by_username(db, data['username'])
        if exists and exists.id != user.id:
            raise ValueError('USERNAME_TAKEN')
        user.username = data['username']
    if 'email' in data and data['email'] and data['email'] != user.email:
        exists = await get_user_by_email(db, data['email'])
        if exists and exists.id != user.id:
            raise ValueError('EMAIL_TAKEN')
        user.email = data['email']
    if 'is_admin' in data and data['is_admin'] is not None:
        user.is_admin = bool(data['is_admin'])
    if 'active' in data and data['active'] is not None:
        user.active = bool(data['active'])

    await db.commit()
    await db.refresh(user)
    return user

async def set_user_password(db: AsyncSession, *, user_id: int, plain_password: str) -> Optional[models.User]:
    """관리자가 임시 비밀번호를 설정."""
    user = await db.get(models.User, user_id)
    if not user:
        return None
    user.hashed_password = security.get_password_hash(plain_password)
    await db.commit()
    return user

async def toggle_user_active(db: AsyncSession, *, user_id: int, active: Optional[bool] = None) -> Optional[models.User]:
    user = await db.get(models.User, user_id)
    if not user:
        return None
    if active is None:
        user.active = not bool(getattr(user, 'active', True))
    else:
        user.active = bool(active)
    await db.commit()
    await db.refresh(user)
    return user
