"""
일반 사용자(users) 관련 라우터.

- /users/me: 현재 인증된 사용자의 계정을 삭제(탈퇴)합니다.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from ...dependencies import get_db, get_current_user
from ... import models, crud, security

router = APIRouter()


@router.get("/users/me", response_model=models.UserResponse, summary="내 정보 조회")
async def get_me(current_user: models.User = Depends(get_current_user)):
    """현재 로그인된 사용자의 정보를 반환합니다.
    
    - 인증은 get_current_user 의존성으로 확인됩니다.
    - JWT 토큰이 유효하면 사용자 정보를 반환합니다.
    """
    return current_user


@router.delete("/users/me", summary="내 계정 삭제")
async def delete_me(db=Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """현재 로그인된 사용자 계정을 삭제합니다.

    - 인증은 get_current_user 의존성으로 확인됩니다.
    - 삭제 성공 시 간단한 메시지를 반환하고, 실패 시 404를 반환합니다.
    """
    success = await crud.delete_user(db, user_id=current_user.id)
    if success:
        return {"message": "회원 탈퇴가 완료되었습니다."}
    raise HTTPException(status_code=404, detail="User not found")


@router.patch("/users/me", response_model=models.UserResponse, summary="내 정보 수정")
async def update_me(update: models.UserUpdate, db=Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """현재 로그인된 사용자의 프로필 정보를 수정합니다 (username)."""
    changed = False
    if update.username and update.username != current_user.username:
        # username 중복 확인
        exists = await crud.get_user_by_username(db, username=update.username)
        if exists and exists.id != current_user.id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 사용 중인 사용자명입니다.")
        current_user.username = update.username
        changed = True

    if not changed:
        return current_user

    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.put("/users/me/password", summary="비밀번호 변경")
async def change_password(body: models.PasswordChange, db=Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """현재 비밀번호 검증 후 새 비밀번호로 변경합니다."""
    if not current_user.hashed_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="소셜 로그인 계정은 비밀번호가 없습니다.")

    if not security.verify_password(body.current_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="현재 비밀번호가 올바르지 않습니다.")

    current_user.hashed_password = security.get_password_hash(body.new_password)
    await db.commit()
    return {"message": "비밀번호가 변경되었습니다."}
