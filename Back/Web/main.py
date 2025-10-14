# --------------------------------------------------------------------------
# 1. 라이브러리 및 모듈 임포트
# --------------------------------------------------------------------------
import os
import asyncio
from typing import List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import openai

# 🔽 1번 항목: CORS 미들웨어를 불러옵니다.
from fastapi.middleware.cors import CORSMiddleware

# --- 팀원들이 개발 중인 모듈을 '블랙박스'처럼 가져옵니다. ---
from kobert_analyzer import calculate_kobert_score
from similarity_analyzer import calculate_similarity_score

# --------------------------------------------------------------------------
# 2. FastAPI 앱 설정 및 초기화
# --------------------------------------------------------------------------
app = FastAPI()

# 🔽 1번 항목: CORS 미들웨어 설정을 추가합니다.
# 이 부분이 백엔드와 프론트엔드 서버 간의 통신을 허용하는 역할을 합니다.
origins = [
    "http://localhost:8080",  # Vue.js 개발 서버의 기본 주소
    "http://127.0.0.1:8080", # 다른 형태의 로컬 주소
    # 나중에 실제 웹사이트에 배포한다면, 그 주소도 여기에 추가해야 합니다.
    # 예: "https://www.your-awesome-site.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # origins 리스트에 있는 주소에서의 요청을 허용합니다.
    allow_credentials=True,      # 쿠키와 같은 인증 정보를 허용합니다.
    allow_methods=["*"],         # 모든 HTTP 메소드(POST, GET 등)를 허용합니다.
    allow_headers=["*"],         # 모든 HTTP 헤더를 허용합니다.
)

# --- OpenAI API 키 설정 (환경변수에서 안전하게 로드) ---
openai.api_key = os.getenv("OPENAI_API_KEY")

# --------------------------------------------------------------------------
# 3. API 데이터 모델 정의 (요청/응답 형식)
# --------------------------------------------------------------------------
class AnalysisRequest(BaseModel):
    title: str = Field(..., min_length=5, example="AI 시대의 교육 혁신 방안 연구")
    abstract: str = Field(..., min_length=20, example="본 연구는 인공지능 기술이 교육 현장에 미치는 영향과...")

class AnalysisDetails(BaseModel):
    kobert_score: float
    similarity_score: float

class AnalysisResponse(BaseModel):
    ai_probability: float
    analysis_details: AnalysisDetails

# --------------------------------------------------------------------------
# 4. 핵심 로직 및 헬퍼 함수
# --------------------------------------------------------------------------

def combine_scores_placeholder(kobert_score: float, similarity_score: float) -> float:
    """
    [임시 최종 확률 계산 로직]
    이 함수는 최종 확률 계산식이 정해지면 교체될 '부품'입니다.
    """
    print("💡 주의: 임시 최종 확률 계산 로직을 사용 중입니다.")
    final_score = (kobert_score * 0.7) + (similarity_score * 0.3)
    return final_score

async def generate_ai_abstracts(title: str) -> List[str]:
    """OpenAI GPT 모델을 호출하여 비교용 초록들을 비동기적으로 생성합니다."""
    try:
        chat_completion = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "당신은 한국어 논문 초록을 작성하는 전문 AI입니다."},
                {"role": "user", "content": f"다음 제목의 논문에 대한 초록을 200자 내외로 작성해주세요: {title}"}
            ],
            n=3
        )
        return [choice.message.content for choice in chat_completion.choices]
    except openai.error.AuthenticationError as e:
        raise HTTPException(status_code=401, detail=f"OpenAI API 인증 실패: {e}")
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"OpenAI API 서비스 호출 실패: {e}")

# --------------------------------------------------------------------------
# 5. 메인 API 엔드포인트
# --------------------------------------------------------------------------
@app.post("/api/v1/analyze", response_model=AnalysisResponse)
async def analyze_text(request: AnalysisRequest):
    """
    백엔드의 메인 분석 API입니다. 여러 분석 작업을 병렬로 처리하여 성능을 최적화하고,
    오류 발생 시에도 안정적인 응답을 보장합니다.
    """
    try:
        results = await asyncio.gather(
            asyncio.to_thread(calculate_kobert_score, request.abstract),
            generate_ai_abstracts(request.title)
        )
        kobert_score, generated_abstracts = results

    except Exception as e:
        print(f"분석 초기 단계 오류 발생: {e}")
        raise HTTPException(status_code=500, detail="내부 분석 모듈 또는 외부 API 호출 중 오류가 발생했습니다.")

    similarity_score = calculate_similarity_score(
        original_text=request.abstract,
        generated_texts=generated_abstracts
    )

    final_probability = combine_scores_placeholder(
        kobert_score=kobert_score,
        similarity_score=similarity_score
    )

    return AnalysisResponse(
        ai_probability=final_probability,
        analysis_details=AnalysisDetails(
            kobert_score=kobert_score,
            similarity_score=similarity_score
        )
    )