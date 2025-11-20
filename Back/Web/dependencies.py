"""
FastAPI 의존성(dependencies) 모듈.

역할:
- DB 세션 제공 의존성(get_db)
- JWT 인증을 통한 현재 사용자/관리자 확인(get_current_user, get_current_admin_user)
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from . import crud, models
from .database import async_session
from .config import settings

# Swagger 등에서 인증 스킴으로 사용됩니다. tokenUrl은 형식상 필요합니다.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_db():
    """요청 단위로 비동기 DB 세션을 제공합니다."""
    async with async_session() as session:
        yield session


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> models.User:
    """JWT를 검증하여 현재 사용자를 반환합니다.

    - Authorization: Bearer <token>
    - payload의 sub에 username이 있어야 합니다.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await crud.get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    # 비활성 사용자 접근 차단
    if hasattr(user, "active") and not user.active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive account")
    return user


async def get_current_admin_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    """현재 사용자가 관리자 권한인지 확인합니다."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user