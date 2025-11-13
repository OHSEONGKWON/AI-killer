"""
일반 사용자(users) 관련 라우터.

- /users/me: 현재 인증된 사용자의 계정을 삭제(탈퇴)합니다.
"""

from fastapi import APIRouter, Depends, HTTPException

from ...dependencies import get_db, get_current_user
from ... import models, crud

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
