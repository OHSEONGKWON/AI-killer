"""
관리자(admin) 관련 라우터.

- 관리자 전용 엔드포인트로, get_current_admin_user 의존성을 통해 권한 체크를 수행합니다.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from ...dependencies import get_db, get_current_admin_user
from ... import models, crud

router = APIRouter()


@router.get("/admin/users", response_model=List[models.UserResponse], summary="전체 사용자 조회")
async def read_users(
    skip: int = 0,
    limit: int = 100,
    q: Optional[str] = Query(default=None, description="username 또는 email 부분검색"),
    is_admin: Optional[bool] = Query(default=None),
    active: Optional[bool] = Query(default=None),
    db=Depends(get_db),
    admin_user: models.User = Depends(get_current_admin_user),
):
    """필터/검색 포함 전체 사용자 목록을 페이지네이션하여 반환합니다."""
    users = await crud.search_users(db, q=q, is_admin=is_admin, active=active, skip=skip, limit=limit)
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


@router.patch("/admin/users/{user_id}", response_model=models.UserResponse, summary="사용자 정보 수정")
async def update_user_admin(
    user_id: int,
    payload: models.UserAdminUpdate,
    db=Depends(get_db),
    admin_user: models.User = Depends(get_current_admin_user),
):
    try:
        updated = await crud.update_user_admin(db, user_id=user_id, update=payload)
    except ValueError as e:
        code = str(e)
        if code == 'USERNAME_TAKEN':
            raise HTTPException(status_code=409, detail="이미 사용 중인 사용자명입니다.")
        if code == 'EMAIL_TAKEN':
            raise HTTPException(status_code=409, detail="이미 사용 중인 이메일입니다.")
        raise
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return updated


@router.post("/admin/users/{user_id}/reset-password", summary="임시 비밀번호 발급")
async def reset_password(
    user_id: int,
    db=Depends(get_db),
    admin_user: models.User = Depends(get_current_admin_user),
):
    import secrets, string
    alphabet = string.ascii_letters + string.digits
    temp = ''.join(secrets.choice(alphabet) for _ in range(12))
    user = await crud.set_user_password(db, user_id=user_id, plain_password=temp)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"temporary_password": temp}


@router.patch("/admin/users/{user_id}/status", response_model=models.UserResponse, summary="활성/비활성 전환")
async def change_status(
    user_id: int,
    body: models.UserStatusUpdate = None,
    db=Depends(get_db),
    admin_user: models.User = Depends(get_current_admin_user),
):
    target_active = None if body is None else body.active
    user = await crud.toggle_user_active(db, user_id=user_id, active=target_active)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
