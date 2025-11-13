"""
인증(auth) 관련 라우터.

주요 기능:
- 카카오 로그인 OAuth 2.0 플로우
- 일반 로그인/회원가입
- JWT 토큰 발급 및 검증
"""

from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.responses import RedirectResponse
import httpx

from ...dependencies import get_db, get_current_user
from ... import models, security, crud
from ...config import settings

router = APIRouter()

# settings에서 카카오 설정 읽기
KAKAO_REST_API_KEY = settings.KAKAO_REST_API_KEY
KAKAO_REDIRECT_URI = settings.KAKAO_REDIRECT_URI or "http://localhost:8000/api/v1/auth/kakao/callback"


@router.get("/auth/kakao", summary="카카오 로그인 시작")
async def kakao_login_start():
    """
    카카오 로그인 페이지로 리다이렉트합니다.
    
    Vue 프론트엔드에서 이 엔드포인트를 호출하면 카카오 로그인 페이지로 이동합니다.
    사용자가 로그인하면 KAKAO_REDIRECT_URI로 code와 함께 리다이렉트됩니다.
    
    흐름:
    1. Vue에서 GET /api/v1/auth/kakao 호출
    2. 카카오 로그인 페이지로 리다이렉트
    3. 사용자 로그인
    4. 카카오가 /api/v1/auth/kakao/callback?code=xxx 로 리다이렉트
    5. 콜백에서 토큰 발급
    """
    if not KAKAO_REST_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="카카오 REST API 키가 설정되지 않았습니다. .env 파일을 확인하세요."
        )
    
    # 카카오 인증 URL 생성
    kakao_auth_url = (
        f"https://kauth.kakao.com/oauth/authorize"
        f"?client_id={KAKAO_REST_API_KEY}"
        f"&redirect_uri={KAKAO_REDIRECT_URI}"
        f"&response_type=code"
    )
    
    return RedirectResponse(url=kakao_auth_url)


@router.get("/auth/kakao/callback", summary="카카오 로그인 콜백")
async def kakao_callback(code: str, db=Depends(get_db)):
    """
    카카오 로그인 후 리다이렉트되는 콜백 엔드포인트입니다.
    
    처리 순서:
    1. code로 카카오 액세스 토큰 발급
    2. 액세스 토큰으로 사용자 정보 조회
    3. 사용자 정보로 회원가입/로그인 처리
    4. JWT 토큰 발급
    5. 프론트엔드로 리다이렉트 (토큰 전달)
    """
    if not KAKAO_REST_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="카카오 REST API 키가 설정되지 않았습니다."
        )
    
    try:
        # 1. 카카오 액세스 토큰 발급
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://kauth.kakao.com/oauth/token",
                data={
                    "grant_type": "authorization_code",
                    "client_id": KAKAO_REST_API_KEY,
                    "redirect_uri": KAKAO_REDIRECT_URI,
                    "code": code,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            
            if token_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"카카오 토큰 발급 실패: {token_response.text}"
                )
            
            token_data = token_response.json()
            kakao_access_token = token_data["access_token"]
            
            # 2. 카카오 사용자 정보 조회
            user_response = await client.get(
                "https://kapi.kakao.com/v2/user/me",
                headers={"Authorization": f"Bearer {kakao_access_token}"},
            )
            
            if user_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"카카오 사용자 정보 조회 실패: {user_response.text}"
                )
            
            user_data = user_response.json()
            kakao_id = user_data["id"]
            kakao_account = user_data.get("kakao_account", {})
            profile = kakao_account.get("profile", {})
            
            # 3. 사용자 정보 추출
            nickname = profile.get("nickname", f"kakao_user_{kakao_id}")
            email = kakao_account.get("email", f"kakao_{kakao_id}@kakao.user")
            
            # 4. 데이터베이스에서 사용자 조회/생성
            user = await crud.get_user_by_kakao_id(db, kakao_id=kakao_id)
            
            if not user:
                # 신규 사용자 생성
                user_info = {
                    "id": kakao_id,
                    "nickname": nickname,
                    "email": email,
                }
                user = await crud.create_kakao_user(db, user_info=user_info)
            
            # 5. JWT 토큰 발급
            access_token = security.create_access_token(data={"sub": user.username})
            
            # 6. 프론트엔드로 리다이렉트 (토큰 전달)
            # Vue 프론트엔드 주소로 리다이렉트 (토큰을 쿼리 파라미터로 전달)
            frontend_url = settings.FRONTEND_URL
            redirect_url = f"{frontend_url}/auth/callback?token={access_token}"
            
            return RedirectResponse(url=redirect_url)
    
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"카카오 API 호출 중 오류 발생: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"카카오 로그인 처리 중 오류 발생: {str(e)}"
        )


@router.post("/auth/register", response_model=models.UserResponse, summary="회원가입")
async def register(user_create: models.UserCreate, db=Depends(get_db)):
    """
    일반 회원가입 (이메일/비밀번호 방식)
    
    Args:
        user_create: username, email, password
    
    Returns:
        생성된 사용자 정보
    """
    try:
        # 중복 체크 (username과 email 모두)
        existing_user = await crud.get_user_by_username(db, username=user_create.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 존재하는 사용자명입니다."
            )
        
        existing_email = await crud.get_user_by_email(db, email=user_create.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 등록된 이메일입니다."
            )
        
        # 비밀번호 해시화
        hashed_password = security.get_password_hash(user_create.password)
        
        # 사용자 생성
        db_user = models.User(
            username=user_create.username,
            email=user_create.email,
            hashed_password=hashed_password,
            is_admin=False
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        
        return db_user
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        print(f"회원가입 오류: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"회원가입 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/auth/login", response_model=models.Token, summary="로그인")
async def login(username: str = Form(...), password: str = Form(...), db=Depends(get_db)):
    """
    일반 로그인 (이메일/비밀번호 방식)
    
    Args:
        username: 사용자명 (Form 데이터)
        password: 비밀번호 (Form 데이터)
    
    Returns:
        JWT 액세스 토큰
    """
    # 사용자 조회
    user = await crud.get_user_by_username(db, username=username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="잘못된 사용자명 또는 비밀번호입니다."
        )
    
    # 비밀번호 검증
    if not security.verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="잘못된 사용자명 또는 비밀번호입니다."
        )
    
    # JWT 토큰 발급
    access_token = security.create_access_token(data={"sub": user.username})
    return models.Token(access_token=access_token, token_type="bearer")


@router.post("/auth/logout", summary="로그아웃")
async def logout(current_user: models.User = Depends(get_current_user)):
    """JWT 기반 로그아웃 확인 엔드포인트.

    서버에서 상태를 저장하지 않으므로 별도 무효화 작업은 없고,
    클라이언트에서 저장된 토큰(JWT)을 삭제하도록 안내합니다.
    """
    return {"message": "Successfully logged out"}
