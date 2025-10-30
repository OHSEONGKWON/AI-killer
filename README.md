# AI-killer

**한국어 논문/에세이 AI 작성 검증 서비스**

사용자가 입력한 한국어 논문 초록이나 에세이가 사람이 쓴 글인지, AI가 쓴 글인지 판별하는 웹 서비스입니다. FastAPI 백엔드와 Vue.js 프론트엔드로 구성되어 있으며, 세 가지 핵심 기능을 제공합니다:

## 🎯 핵심 기능

### 1. AI 텍스트 분석
- **KoBERT 모델**을 활용한 한국어 텍스트 AI 작성 확률 분석
- 0~1 사이의 확률 값으로 AI 작성 가능성 제시
- 분석 결과를 데이터베이스에 자동 저장하여 이력 관리

### 2. 표절 검사
- 외부 API를 통한 웹 검색 기반 유사 콘텐츠 탐지
- 유사도 점수와 출처 정보 제공
- 임계값(0.7) 기준 표절 여부 판단

### 3. 문법 검사
- 외부 문법 검사 API를 통한 맞춤법, 문법 오류 검사
- 오류 위치(start_index, end_index)와 교정 제안 제공
- 오류 유형별 분류 (spelling, grammar, punctuation)

## 📁 백엔드 폴더 구조

```
Back/
  Web/
    __init__.py
    main.py                 # FastAPI 앱 엔트리
    config.py               # 환경 설정 (pydantic-settings)
    database.py             # SQLModel 비동기 엔진/세션
    models.py               # Pydantic/SQLModel 스키마
    analysis_models.py      # AnalysisRecord 테이블 모델
    crud.py                 # DB 액세스 함수 (User, AnalysisRecord CRUD)
    security.py             # JWT, 비밀번호 해시
    dependencies.py         # 의존성 (get_db, get_current_user)
    kobert_analyzer.py      # KoBERT 분석 모듈 (팀원 구현 예정)
    api/
      __init__.py
      v1/
        __init__.py         # v1 라우터 집계 (prefix=/api/v1)
        analysis.py         # POST /api/v1/analyze (AI 작성 분석)
        plagiarism.py       # POST /api/v1/plagiarism/check (표절 검사)
        grammar.py          # POST /api/v1/grammar/check (문법 검사)
        auth.py             # 카카오 OAuth 로그인/로그아웃
        users.py            # 사용자 관리 (계정 삭제)
        admin.py            # 관리자 기능 (사용자 조회)
```

## 💾 데이터베이스 구조

### User 테이블
사용자 정보를 저장하는 테이블입니다.

| 필드 | 타입 | 설명 |
|------|------|------|
| id | Integer | 기본키 (자동 증가) |
| username | String | 사용자명 (유니크, 인덱스) |
| email | String | 이메일 (유니크) |
| hashed_password | String | 해시된 비밀번호 (Optional) |
| kakao_id | Integer | 카카오 계정 ID (유니크, 인덱스, Optional) |
| is_admin | Boolean | 관리자 여부 (기본값: False) |

### AnalysisRecord 테이블
AI 텍스트 분석 결과를 저장하는 테이블입니다.

| 필드 | 타입 | 설명 |
|------|------|------|
| id | Integer | 기본키 (자동 증가) |
| title | String | 분석한 글의 제목 |
| content | String | 분석한 본문 텍스트 |
| ai_probability | Float | 최종 AI 작성 확률 (0~1) |
| kobert_score | Float | KoBERT 분석 점수 (0~1) |
| similarity_score | Float | 유사도 점수 (현재 0.0, 향후 확장 가능) |
| created_at | String | 분석 수행 시각 (ISO 8601 형식) |

**특징:**
- 모든 분석 요청은 자동으로 데이터베이스에 저장됩니다
- 추후 사용자별 분석 이력 조회 기능 추가 가능
- 통계 및 리포트 생성에 활용 가능## 🚀 실행 방법 (Windows PowerShell)

### 1. 가상환경 생성 및 활성화, 의존성 설치

```powershell
cd Back
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. 환경변수 설정

프로젝트 루트에 `.env` 파일을 만들고 다음 키를 설정하세요:

```env
# 카카오 OAuth (필수)
KAKAO_REST_API_KEY=your_kakao_rest_api_key
KAKAO_REDIRECT_URI=http://localhost:8000/api/v1/auth/kakao/callback

# JWT 설정 (필수)
JWT_SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# 외부 API 설정 (선택, 실제 연동 시 필요)
PLAGIARISM_API_URL=https://api.plagiarism-checker.com/check
PLAGIARISM_API_KEY=your_plagiarism_api_key
GRAMMAR_API_URL=https://api.grammar-checker.com/check
GRAMMAR_API_KEY=your_grammar_api_key
```

### 3. 서버 실행

```powershell
cd Web
uvicorn main:app --reload
```

서버가 `http://127.0.0.1:8000`에서 실행됩니다.

- **API 문서**: http://127.0.0.1:8000/docs (Swagger UI)
- **대체 문서**: http://127.0.0.1:8000/redoc (ReDoc)

## 📡 API 엔드포인트

### AI 분석
- **POST** `/api/v1/analyze` - AI 작성 확률 분석
  - 요청: `{ "title": "제목", "content": "본문" }`
  - 응답: `{ "ai_probability": 0.85, "analysis_details": {...} }`
  - **결과는 자동으로 DB에 저장됩니다**

### 표절 검사
- **POST** `/api/v1/plagiarism/check` - 표절/유사도 검사
  - 요청: `{ "content": "검사할 텍스트", "check_web": true }`
  - 응답: `{ "overall_similarity": 0.65, "matched_sources": [...], "is_plagiarized": false }`
  - 현재는 시뮬레이션 응답 반환 (실제 API 연동 대기 중)

### 문법 검사
- **POST** `/api/v1/grammar/check` - 맞춤법/문법 검사
  - 요청: `{ "content": "검사할 텍스트" }`
  - 응답: `{ "errors": [...], "total_errors": 2 }`
  - 현재는 시뮬레이션 응답 반환 (실제 API 연동 대기 중)

### 인증 & 사용자
- **POST** `/api/v1/auth/kakao/callback` - 카카오 로그인
- **POST** `/api/v1/auth/logout` - 로그아웃
- **DELETE** `/api/v1/users/me` - 내 계정 삭제

### 관리자 (관리자 권한 필요)
- **GET** `/api/v1/admin/users` - 전체 사용자 조회
- **GET** `/api/v1/admin/users/{user_id}` - 특정 사용자 조회

## 🔧 라우터 추가 가이드

새로운 기능을 추가하려면:

1. `Back/Web/api/v1/`에 새 파일 생성 (예: `new_feature.py`)
2. `APIRouter` 정의 및 엔드포인트 작성
3. `Back/Web/api/v1/__init__.py`에 라우터 등록

**예제:**

```python
# Back/Web/api/v1/new_feature.py
from fastapi import APIRouter
router = APIRouter()

@router.get("/new-feature")
def read_new_feature():
    return {"message": "새 기능입니다"}
```

```python
# Back/Web/api/v1/__init__.py
from fastapi import APIRouter
from . import analysis, auth, admin, users, plagiarism, grammar, new_feature

router = APIRouter(prefix="/api/v1")
router.include_router(analysis.router, tags=["분석"])
router.include_router(plagiarism.router, tags=["표절검사"])
router.include_router(grammar.router, tags=["문법검사"])
router.include_router(auth.router, tags=["인증"])
router.include_router(users.router, tags=["사용자"])
router.include_router(admin.router, tags=["관리자"])
router.include_router(new_feature.router, tags=["새기능"])  # 추가
```

## 📝 주요 기능 사용 예제

### 1. AI 텍스트 분석

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "인공지능의 발전",
    "content": "최근 인공지능 기술의 발전은 놀라운 속도로 진행되고 있다."
  }'
```

**응답:**
```json
{
  "ai_probability": 0.85,
  "analysis_details": {
    "kobert_score": 0.85,
    "similarity_score": 0.0
  }
}
```

### 2. 표절 검사

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/plagiarism/check" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "검사할 논문 본문...",
    "check_web": true,
    "check_internal": false
  }'
```

**응답:**
```json
{
  "overall_similarity": 0.65,
  "matched_sources": [
    {
      "source_url": "https://example.com/similar-article",
      "source_title": "비슷한 주제의 논문",
      "similarity_score": 0.65,
      "matched_text": "일치하는 구간 텍스트..."
    }
  ],
  "is_plagiarized": false
}
```

### 3. 문법 검사

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/grammar/check" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "맞춤법과 문법을 검사할 텍스트입니다."
  }'
```

**응답:**
```json
{
  "errors": [
    {
      "message": "맞춤법 오류: '있다'를 '있다'로 수정",
      "start_index": 10,
      "end_index": 12,
      "error_type": "spelling",
      "suggestions": ["있다", "이따"]
    }
  ],
  "total_errors": 1,
  "corrected_text": null
}
```

## 🧪 Postman 테스트

프로젝트 루트에 있는 `AI-killer.postman_collection.json` 파일을 Postman에 임포트하면 모든 API를 쉽게 테스트할 수 있습니다.

1. Postman 실행
2. **Import** 클릭
3. `AI-killer.postman_collection.json` 파일 선택
4. 컬렉션에서 원하는 API 선택 후 **Send**

## 🛠️ 기술 스택

- **Backend**: FastAPI 0.118.2, Python 3.11+
- **Database**: SQLite (SQLModel + aiosqlite)
- **Authentication**: JWT (python-jose), Kakao OAuth
- **AI Model**: KoBERT (팀원 구현 예정)
- **External APIs**: 표절 검사 API, 문법 검사 API (연동 예정)

## 📌 향후 개발 계획

- [ ] KoBERT 실제 모델 통합 (팀원 작업)
- [ ] 실제 표절 검사 API 연동 (Copyscape, Turnitin 등)
- [ ] 실제 문법 검사 API 연동 (LanguageTool, Grammarly 등)
- [ ] 사용자별 분석 이력 조회 기능
- [ ] 분석 결과 통계 및 리포트 생성
- [ ] Vue.js 프론트엔드 연동
- [ ] 데이터베이스 인덱스 최적화
- [ ] 단위 테스트 및 통합 테스트 작성

## 👥 팀 구성

- **백엔드 개발**: FastAPI, 데이터베이스, API 설계
- **AI 모델**: KoBERT 기반 한국어 텍스트 분석 모델
- **프론트엔드**: Vue.js 웹 인터페이스

## 📄 라이선스

MIT License
