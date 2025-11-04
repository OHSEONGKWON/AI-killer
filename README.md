# AI-killer

**한국어 논문/에세이 AI 작성 검증 서비스**

[![CI](https://github.com/OHSEONGKWON/AI-killer/actions/workflows/ci.yml/badge.svg)](https://github.com/OHSEONGKWON/AI-killer/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.118.2-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

사용자가 입력한 한국어 논문 초록이나 에세이가 사람이 쓴 글인지, AI가 쓴 글인지 판별하는 웹 서비스입니다. FastAPI 백엔드와 Vue.js 프론트엔드로 구성되어 있으며, 세 가지 핵심 기능을 제공합니다:

## 🎯 핵심 기능

### 1. AI 텍스트 분석
- **4가지 지표를 활용한 정밀 분석**:
  - **SBERT**: 코사인 유사도 기반 AI 생성 텍스트와의 유사성 측정
  - **KoBERT**: 한국어 AI vs Human 분류 확률
  - **Perplexity**: 텍스트 혼란도 (낮을수록 AI-like)
  - **Burstiness**: 텍스트 패턴 변동성 (낮을수록 AI-like)
- **텍스트 유형별 가중치 최적화**: 논문, 에세이, 블로그 등 장르별 맞춤 분석
- **관리자 제어**: 관리자가 각 지표의 가중치를 동적으로 조정 가능
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
# 프로젝트 루트에서
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

> **참고**: PowerShell에서 스크립트 실행 오류 발생 시, 다음 명령어를 한 번 실행하세요:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```

### 2. 환경변수 설정 (중요!)

**보안 주의사항**: 실제 시크릿 키는 절대 git에 커밋하지 마세요!

1. 프로젝트 루트에 `.env` 파일을 생성합니다:
   ```powershell
   Copy-Item .env.example .env
   ```

2. `.env` 파일을 열어 실제 키 값으로 교체하세요:

**필수 설정** (이 값들이 없으면 서버가 시작되지 않습니다):
```env
# 카카오 OAuth (카카오 개발자 콘솔에서 발급)
KAKAO_REST_API_KEY=실제_카카오_REST_API_키
KAKAO_REDIRECT_URI=http://localhost:8000/api/v1/auth/kakao/callback

# JWT 설정 (아래 명령어로 강력한 키 생성 권장)
JWT_SECRET_KEY=최소_32자_이상의_강력한_랜덤_문자열
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

**JWT 비밀키 생성 방법**:
```powershell
# PowerShell에서 64자 랜덤 키 생성
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 64 | % {[char]$_})
```
또는 Python:
```powershell
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

**선택 설정** (기능 사용 시 필요):
```env
# OpenAI API (AI 분석 기능)
OPENAI_API_KEY=실제_OpenAI_API_키

# 표절 검사 API
PLAGIARISM_API_URL=https://api.plagiarism-checker.com/check
PLAGIARISM_API_KEY=실제_표절검사_API_키

# 문법 검사 API
GRAMMAR_API_URL=https://api.grammar-checker.com/check
GRAMMAR_API_KEY=실제_문법검사_API_키
```

자세한 내용은 `.env.example` 파일의 주석을 참고하세요.

### 3. 서버 실행

**중요**: 첫 실행 전에 데이터베이스 마이그레이션을 수행하세요!

```powershell
# 프로젝트 루트에서
cd Back\Web

# 데이터베이스 마이그레이션 실행 (최초 1회 또는 스키마 변경 시)
alembic upgrade head

# 서버 실행
uvicorn main:app --reload
```

서버가 `http://127.0.0.1:8000`에서 실행됩니다.

- **API 문서**: http://127.0.0.1:8000/docs (Swagger UI)
- **대체 문서**: http://127.0.0.1:8000/redoc (ReDoc)

> **팁**: `--reload` 옵션은 코드 변경 시 자동으로 서버를 재시작합니다 (개발 환경 전용).

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

## 🗄️ 데이터베이스 마이그레이션 (Alembic)

프로젝트는 Alembic을 사용하여 데이터베이스 스키마 변경을 관리합니다.

### 마이그레이션 적용

```powershell
# 최신 마이그레이션 적용
cd Back\Web
alembic upgrade head

# 특정 버전으로 업그레이드
alembic upgrade <revision_id>

# 한 단계 업그레이드
alembic upgrade +1
```

### 마이그레이션 생성 (모델 변경 후)

`models.py` 또는 `analysis_models.py`에서 테이블 구조를 변경한 후:

```powershell
# 자동으로 변경사항 감지하여 마이그레이션 파일 생성
alembic revision --autogenerate -m "설명"

# 예시
alembic revision --autogenerate -m "Add user_role column"

# 생성된 마이그레이션 검토 후 적용
alembic upgrade head
```

### 마이그레이션 롤백

```powershell
# 한 단계 롤백
alembic downgrade -1

# 특정 버전으로 롤백
alembic downgrade <revision_id>

# 모든 마이그레이션 롤백 (주의!)
alembic downgrade base
```

### 마이그레이션 이력 확인

```powershell
# 현재 버전 확인
alembic current

# 마이그레이션 이력 확인
alembic history

# 대기 중인 마이그레이션 확인
alembic history --indicate-current
```

> **주의**: 프로덕션 환경에서는 마이그레이션 전에 반드시 데이터베이스 백업을 수행하세요!

## 🎛️ 관리자 기능: AI 분석 가중치 관리

관리자는 텍스트 유형별로 4가지 AI 검출 지표의 가중치를 조정할 수 있습니다.

### 기본 프리셋 초기화

```bash
# POST /admin/analysis-configs/init-defaults
curl -X POST http://localhost:8000/admin/analysis-configs/init-defaults \
  -H "Authorization: Bearer <admin_token>"
```

**생성되는 기본 프리셋**:
- **paper** (논문): KoBERT 40%, SBERT 30%, Perplexity 20%, Burstiness 10%
- **essay** (에세이): SBERT 35%, KoBERT 30%, Burstiness 20%, Perplexity 15%
- **blog** (블로그): KoBERT 35%, Burstiness 25%, SBERT 25%, Perplexity 15%

### 설정 조회

```bash
# 모든 설정 조회
GET /admin/analysis-configs

# 특정 텍스트 유형 조회
GET /admin/analysis-configs/paper
```

**응답 예시**:
```json
{
  "id": 1,
  "text_type": "paper",
  "description": "논문 초록용 가중치 (KoBERT 강조)",
  "sbert_weight": 0.3,
  "kobert_weight": 0.4,
  "perplexity_weight": 0.2,
  "burstiness_weight": 0.1,
  "is_active": true,
  "is_default": false
}
```

### 설정 생성/수정

```bash
# 새 설정 생성
POST /admin/analysis-configs
{
  "text_type": "report",
  "description": "보고서용 가중치",
  "sbert_weight": 0.25,
  "kobert_weight": 0.35,
  "perplexity_weight": 0.25,
  "burstiness_weight": 0.15,
  "is_active": true,
  "is_default": false
}

# 기존 설정 수정
PUT /admin/analysis-configs/paper
{
  "kobert_weight": 0.5,
  "perplexity_weight": 0.15
}

# 설정 삭제
DELETE /admin/analysis-configs/paper
```

**가중치 규칙**:
- 각 가중치는 0.0~1.0 범위
- 4가지 가중치의 합이 1.0에 가까울수록 정확 (권장)
- 합이 1.0이 아니어도 동작하지만 경고 메시지 반환

### 분석 요청 시 텍스트 유형 지정

```bash
POST /api/v1/analyze
{
  "title": "논문 제목",
  "content": "분석할 텍스트...",
  "text_type": "paper"  # 선택적, 기본값: "paper"
}
```

시스템은 지정된 `text_type`에 맞는 가중치 설정을 자동으로 적용하여 최종 AI 확률을 계산합니다.

## 🧪 테스트 실행

### 단위 테스트 실행

프로젝트에는 핵심 모듈의 단위 테스트가 포함되어 있습니다.

```powershell
# 가상환경 활성화 후
cd Back\Web
pytest tests/ -v
```

**커버리지 측정**:
```powershell
pytest tests/ --cov=. --cov-report=html
# 결과는 htmlcov/index.html에서 확인
```

**특정 테스트만 실행**:
```powershell
pytest tests/test_analysis.py -v
pytest tests/test_security.py -v
pytest tests/test_kobert_analyzer.py -v
```

## 🧪 Postman 테스트

프로젝트 루트에 있는 `AI-killer.postman_collection.json` 파일을 Postman에 임포트하면 모든 API를 쉽게 테스트할 수 있습니다.

1. Postman 실행
2. **Import** 클릭
3. `AI-killer.postman_collection.json` 파일 선택
4. 컬렉션에서 원하는 API 선택 후 **Send**

## 🛠️ 기술 스택

- **Backend**: FastAPI 0.118.2, Python 3.11+
- **Database**: SQLite (SQLModel + aiosqlite), Alembic (마이그레이션)
- **Authentication**: JWT (python-jose), Kakao OAuth
- **AI Model**: KoBERT (팀원 구현 예정)
- **External APIs**: 표절 검사 API, 문법 검사 API (연동 예정)
- **Logging**: Structured JSON 로깅, Sentry (선택)
- **Testing**: pytest, pytest-asyncio, pytest-cov
- **CI/CD**: GitHub Actions (린트, 테스트, 보안 검사)

## 🧑‍💻 개발 가이드

### 코드 품질 검사

프로젝트는 Ruff를 사용하여 코드 품질을 관리합니다.

```powershell
# Ruff 설치
pip install ruff

# 린트 검사
ruff check Back/Web

# 자동 수정 가능한 문제 수정
ruff check Back/Web --fix

# 코드 포매팅 (Black 스타일)
ruff format Back/Web
```

### 로컬 CI 테스트

GitHub Actions 워크플로우를 로컬에서 미리 테스트:

```powershell
# 린트 + 테스트 한 번에
ruff check Back/Web; pytest Back/Web/tests/ -v --cov=Back/Web
```

### 환경 관리

- **개발 환경**: `LOG_LEVEL=DEBUG`, `JSON_LOGS=0`
- **운영 환경**: `LOG_LEVEL=INFO`, `JSON_LOGS=1`, `SENTRY_DSN` 설정

## 📌 향후 개발 계획

- [x] ~~Alembic 마이그레이션 시스템 도입~~ ✅
- [x] ~~Structured JSON 로깅 및 Sentry 연동~~ ✅
- [x] ~~GitHub Actions CI/CD 파이프라인~~ ✅
- [x] ~~단위 테스트 프레임워크 구축~~ ✅
- [ ] KoBERT 실제 모델 통합 (팀원 작업)
- [ ] 실제 표절 검사 API 연동 (Copyscape, Turnitin 등)
- [ ] 실제 문법 검사 API 연동 (LanguageTool, Grammarly 등)
- [ ] 사용자별 분석 이력 조회 기능
- [ ] 분석 결과 통계 및 리포트 생성
- [ ] Vue.js 프론트엔드 연동
- [ ] PostgreSQL 전환 및 인덱스 최적화
- [ ] Redis 캐싱 및 Celery 백그라운드 작업

## 👥 팀 구성

- **백엔드 개발**: FastAPI, 데이터베이스, API 설계
- **AI 모델**: KoBERT 기반 한국어 텍스트 분석 모델
- **프론트엔드**: Vue.js 웹 인터페이스

## 📄 라이선스

MIT License
