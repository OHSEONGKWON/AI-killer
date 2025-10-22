"""
관리자(admin) 관련 라우터.

- 관리자 전용 엔드포인트로, get_current_admin_user 의존성을 통해 권한 체크를 수행합니다.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException

from ...dependencies import get_db, get_current_admin_user
from ... import models, crud

router = APIRouter()


@router.get("/admin/users", response_model=List[models.UserResponse], summary="전체 사용자 조회")
async def read_users(
    skip: int = 0,
    limit: int = 100,
    db=Depends(get_db),
    admin_user: models.User = Depends(get_current_admin_user),
):
    """전체 사용자 목록을 페이지네이션하여 반환합니다."""
    users = await crud.get_users(db, skip=skip, limit=limit)
    return users


@router.get("/admin/users/{user_id}", response_model=models.UserResponse, summary="특정 사용자 조회")
async def read_user(
    user_id: int,
    db=Depends(get_db),
    admin_user: models.User = Depends(get_current_admin_user),
):
    """특정 사용자 ID로 사용자 정보를 조회합니다."""
    db_user = await crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
