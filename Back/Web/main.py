# main.py
from typing import List
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import SQLModel
import httpx
import asyncio
from .dependencies import get_db, get_current_user, get_current_admin_user
# --- 🔽 프론트엔드 연결을 위한 CORS 미들웨어 import ---
from fastapi.middleware.cors import CORSMiddleware

# --- 프로젝트 모듈 import ---
from . import crud, models, security
from .database import engine
from .dependencies import get_db, get_current_user, get_current_admin_user
from .config import settings

# --- 팀원 분석 모듈 import ---
from kobert_analyzer import calculate_kobert_score
from similarity_analyzer import calculate_similarity_score


app = FastAPI(title="AI 논문 초록 분석 API")

# --- 🔽 프론트엔드 연결을 위한 CORS 설정 추가 ---
# 프론트엔드 개발 서버의 주소를 origins 리스트에 추가해야 합니다.
origins = [
    "http://localhost:8080", # Vue 개발 서버의 기본 주소
    "http://127.0.0.1:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # 허용할 출처를 지정합니다.
    allow_credentials=True,      # 인증 정보(쿠키 등)를 허용합니다.
    allow_methods=["*"],         # 모든 HTTP 메소드(POST, GET 등)를 허용합니다.
    allow_headers=["*"],         # 모든 HTTP 헤더를 허용합니다.
)

# 서버 시작 시 DB 테이블 생성
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

# --- 임시 함수 및 외부 API 호출 함수 ---
def combine_scores_placeholder(kobert_score: float, similarity_score: float) -> float:
    print("💡 주의: 임시 최종 확률 계산 로직을 사용 중입니다.")
    return (kobert_score * 0.7) + (similarity_score * 0.3)

async def generate_ai_abstracts(title: str) -> List[str]:
    print("(OpenAI 모듈) 초록 생성 시작...")
    await asyncio.sleep(1.5) # 네트워크 통신 시간 흉내
    print("(OpenAI 모듈) 초록 생성 완료")
    return [f"{title}에 대한 첫 번째 AI 생성 초록.", f"{title}에 대한 두 번째 AI 생성 초록."]


# --- 분석 API (인증 불필요) ---
@app.post("/api/v1/analyze", response_model=models.AnalysisResponse)
async def analyze(request: models.AnalysisRequest, db = Depends(get_db)):
    try:
        results = await asyncio.gather(
            asyncio.to_thread(calculate_kobert_score, request.abstract),
            generate_ai_abstracts(request.title)
        )
        kobert_score, generated_abstracts = results

    except Exception as e:
        print(f"분석 초기 단계 오류 발생: {e}")
        raise HTTPException(status_code=500, detail="내부 분석 모듈 또는 외부 API 호출 중 오류가 발생했습니다.")

    # similarity 모듈은 현재 동기 블로킹(예: time.sleep)을 포함할 수 있으므로
    # 이벤트 루프를 차단하지 않도록 스레드에서 실행합니다.
    similarity_score = await asyncio.to_thread(
        calculate_similarity_score,
        request.abstract,
        generated_abstracts
    )
    final_probability = combine_scores_placeholder(
        kobert_score=kobert_score,
        similarity_score=similarity_score
    )
    return models.AnalysisResponse(
        ai_probability=final_probability,
        analysis_details=models.AnalysisDetails(
            kobert_score=kobert_score,
            similarity_score=similarity_score
        )
    )

# --- 인증 API ---
@app.post("/api/v1/auth/kakao/callback", response_model=models.Token)
async def kakao_login(kakao_code: models.KakaoCode, db = Depends(get_db)):
    # ... (카카오 로그인 로직) ...
    username_for_token = "kakao_user_" + kakao_code.code
    user = await crud.get_user_by_username(db, username=username_for_token)
    if not user:
        user_info = {"id": 123456789, "nickname": username_for_token, "email": "kakao@example.com"}
        user = await crud.create_kakao_user(db, user_info=user_info)

    access_token = security.create_access_token(data={"sub": user.username})
    return models.Token(access_token=access_token, token_type="bearer")


# --- 유저 API ---
@app.delete("/api/v1/users/me", description="현재 로그인된 사용자를 탈퇴 처리합니다.")
async def delete_me(db = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    success = await crud.delete_user(db, user_id=current_user.id)
    if success:
        return {"message": "회원 탈퇴가 완료되었습니다."}
    raise HTTPException(status_code=404, detail="User not found")

# 🔽🔽🔽 --- 로그아웃 API --- 🔽🔽🔽
@app.post("/api/v1/auth/logout", description="현재 로그인된 사용자를 로그아웃 처리합니다.")
async def logout(current_user: models.User = Depends(get_current_user)):
    """
    JWT 기반 로그아웃을 처리합니다.
    실제 토큰 무효화는 클라이언트 측에서 JWT를 삭제함으로써 이루어집니다.
    이 엔드포인트는 클라이언트에게 로그아웃 처리를 해도 좋다는 확인을 보내는 역할을 합니다.
    """
    
    # 서버 측에서는 특별한 작업을 수행하지 않습니다.
    # get_current_user 의존성을 통해 유효한 사용자인지만 확인합니다.
    return {"message": "Successfully logged out"}

# --- 관리자 API (관리자 인증 필요) 👮 ---
@app.get("/api/v1/admin/users", response_model=List[models.UserResponse], description="전체 사용자 목록을 조회합니다.")
async def read_users(
    skip: int = 0, limit: int = 100, db = Depends(get_db),
    admin_user: models.User = Depends(get_current_admin_user)
):
    users = await crud.get_users(db, skip=skip, limit=limit)
    return users

@app.get("/api/v1/admin/users/{user_id}", response_model=models.UserResponse, description="특정 사용자의 정보를 조회합니다.")
async def read_user(
    user_id: int, db = Depends(get_db),
    admin_user: models.User = Depends(get_current_admin_user)
):
    db_user = await crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user