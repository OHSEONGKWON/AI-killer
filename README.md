# AI-killer

블로그/에세이 AI 작성 검증 서비스입니다. FastAPI 백엔드와 분석 유틸을 포함하며, 기능별 라우터로 모듈화되어 유지보수와 기능 추가가 쉽습니다.

## 백엔드 폴더 구조 (요약)

```
Back/
  Web/
    __init__.py
    main.py                 # FastAPI 앱 엔트리
    config.py               # 환경 설정 (pydantic-settings)
    database.py             # SQLModel 비동기 엔진/세션
    models.py               # Pydantic/SQLModel 스키마
    crud.py                 # DB 액세스 함수 모음
    security.py             # JWT, 비밀번호 해시
    dependencies.py         # 의존성 (DB, 인증)
    kobert_analyzer.py      # KoBERT 스코어 (임시)
    similarity_analyzer.py  # 유사도 스코어 (임시)
    api/
      __init__.py
      v1/
        __init__.py         # v1 라우터 집계 (prefix=/api/v1)
        analysis.py         # POST /api/v1/analyze (AI 작성 검증)
        auth.py             # POST /api/v1/auth/kakao/callback, POST /api/v1/auth/logout
        users.py            # DELETE /api/v1/users/me
        admin.py            # GET /api/v1/admin/users, GET /api/v1/admin/users/{id}
        highlighting.py     # POST /api/v1/highlighting/analyze (AI-like 문장 하이라이팅)
        assistant.py        # POST /api/v1/assistant/improve (글쓰기 개선 제안)
        plagiarism.py       # POST /api/v1/plagiarism/check (표절/유사도 검사)
```## 실행 방법 (Windows PowerShell)

1) 가상환경 생성 및 활성화, 의존성 설치

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2) 환경변수 설정 파일 준비

프로젝트 루트에 `.env` 파일을 만들고 다음 키를 채워주세요 (`Back/Web/config.py` 참고):

```
KAKAO_REST_API_KEY=...
KAKAO_REDIRECT_URI=...
JWT_SECRET_KEY=changeme
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

3) 서버 실행

```powershell
cd Back\Web
uvicorn main:app --reload
```

서버가 실행되면 다음 엔드포인트들이 제공됩니다:

**분석 & AI 검증**
- POST /api/v1/analyze - 블로그/에세이 AI 작성 검증
- POST /api/v1/highlighting/analyze - AI-like 문장 하이라이팅
- POST /api/v1/plagiarism/check - 표절/유사도 검사

**글쓰기 지원**
- POST /api/v1/assistant/improve - 글쓰기 개선 제안
- POST /api/v1/assistant/rewrite - 문장 리라이팅

**인증 & 사용자**
- POST /api/v1/auth/kakao/callback - 카카오 로그인
- POST /api/v1/auth/logout - 로그아웃
- DELETE /api/v1/users/me - 내 계정 삭제

**관리자**
- GET /api/v1/admin/users - 전체 사용자 조회
- GET /api/v1/admin/users/{user_id} - 특정 사용자 조회

## 라우터 추가 가이드

새로운 기능을 추가하려면 `Back/Web/api/v1`에 파일을 만들고 `APIRouter`를 정의한 뒤, `Back/Web/api/v1/__init__.py`에 `include_router`를 추가하세요.

예)

```python
# Back/Web/api/v1/foo.py
from fastapi import APIRouter
router = APIRouter()

@router.get("/foo")
def read_foo():
		return {"ok": True}
```

```python
# Back/Web/api/v1/__init__.py
from fastapi import APIRouter
from . import analysis, auth, admin, users, foo

router = APIRouter(prefix="/api/v1")
router.include_router(analysis.router, tags=["analysis"])
router.include_router(auth.router, tags=["auth"])
router.include_router(admin.router, tags=["admin"])
router.include_router(users.router, tags=["users"])
router.include_router(foo.router, tags=["foo"])  # 추가
```

이제 `GET /api/v1/foo`가 자동으로 포함됩니다.

## 주요 기능 사용 예제

### 1. AI-like 문장 하이라이팅

블로그/에세이에서 AI가 작성한 것처럼 보이는 문장을 찾아 표시합니다.

```json
POST /api/v1/highlighting/analyze
{
  "content": "중요한 점은 블로그를 작성할 때 독자의 관심을 끌어야 합니다. 결론적으로 좋은 콘텐츠를 만들 수 있습니다."
}

Response:
{
  "segments": [
    {
      "text": "중요한 점은 블로그를 작성할 때 독자의 관심을 끌어야 합니다.",
      "start_index": 0,
      "end_index": 38,
      "ai_score": 0.7,
      "reason": "형식적인 강조 표현"
    }
  ],
  "overall_ai_ratio": 0.45
}
```

### 2. 글쓰기 개선 제안

더 인간적이고 창의적인 글로 개선할 수 있는 구체적인 제안을 받습니다.

```json
POST /api/v1/assistant/improve
{
  "content": "이 글에서 중요한 점은 독자에게 도움이 되는 것입니다.",
  "improvement_focus": "creativity"
}

Response:
{
  "suggestions": [
    {
      "original_text": "중요한 점은",
      "improved_text": "핵심은",
      "improvement_type": "creativity",
      "explanation": "더 직관적인 표현으로 바꾸면 읽기 편해요"
    }
  ],
  "overall_score": 65.5
}
```

### 3. 표절/유사도 검사

웹에서 유사한 콘텐츠를 찾아 표절 여부를 확인합니다.

```json
POST /api/v1/plagiarism/check
{
  "content": "검사할 블로그 본문 텍스트...",
  "check_web": true,
  "check_internal": false
}

Response:
{
  "overall_similarity": 0.65,
  "matched_sources": [
    {
      "source_url": "https://example.com/similar",
      "source_title": "비슷한 글",
      "similarity_score": 0.65,
      "matched_text": "일치하는 구간..."
    }
  ],
  "is_plagiarized": false
}
```
