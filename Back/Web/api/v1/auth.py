"""
인증(auth) 관련 라우터.

현재 상태:
- 카카오 로그인 콜백은 실제 카카오 API 연동 전, 임시 사용자 생성/토큰 발급 로직으로 동작합니다.
- 로그아웃은 서버 상태를 변경하지 않고, 클라이언트가 JWT를 폐기하도록 안내만 합니다.
"""

from fastapi import APIRouter, Depends

from ...dependencies import get_db, get_current_user
from ... import models, security, crud

router = APIRouter()


@router.post("/auth/kakao/callback", response_model=models.Token, summary="카카오 로그인 콜백")
async def kakao_login(kakao_code: models.KakaoCode, db=Depends(get_db)):
    """카카오 인증 이후 전달된 code로 사용자 식별 후 JWT 발급(임시 로직).

    실제 연동 시에는 카카오 토큰 교환 → 사용자 정보 조회 → 내부 사용자 연동 순으로 구현합니다.
    """
    # 임시: code 값을 기반으로 가상의 username 구성
    username_for_token = "kakao_user_" + kakao_code.code
    user = await crud.get_user_by_username(db, username=username_for_token)
    if not user:
        # 임시 사용자 정보로 가입 처리
        user_info = {"id": 123456789, "nickname": username_for_token, "email": "kakao@example.com"}
        user = await crud.create_kakao_user(db, user_info=user_info)

    # JWT 발급: sub(subject)에 username을 담습니다.
    access_token = security.create_access_token(data={"sub": user.username})
    return models.Token(access_token=access_token, token_type="bearer")


@router.post("/auth/logout", summary="로그아웃")
async def logout(current_user: models.User = Depends(get_current_user)):
    """JWT 기반 로그아웃 확인 엔드포인트.

    서버에서 상태를 저장하지 않으므로 별도 무효화 작업은 없고,
    클라이언트에서 저장된 토큰(JWT)을 삭제하도록 안내합니다.
    """
    return {"message": "Successfully logged out"}
