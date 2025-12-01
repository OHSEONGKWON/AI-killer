# AI-killer

**한국어 텍스트 AI 작성 검증 서비스**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.118.2-green.svg)](https://fastapi.tiangolo.com/)
[![Vue.js 3](https://img.shields.io/badge/Vue.js-3-brightgreen.svg)](https://vuejs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

사용자가 입력한 한국어 텍스트가 사람이 작성한 글인지, AI가 생성한 글인지 판별하고, 문법 검사 및 표절 여부를 확인하는 웹 서비스입니다.

## 🎯 핵심 기능

### 1. 📝 문법 검사 (Grammar Check)
- **Gemini 2.0 Flash AI** 기반 한국어 문법 및 스타일 분석
- ✍️ 맞춤법/문법 오류 자동 수정
- ✨ 문체 개선 및 윤문 (세련된 표현)
- 📊 문법 점수 (0-100) 및 자연스러움 평가
- 💡 어휘 개선 제안
- 🔄 원문 → 교정본 → 윤문본 3단계 비교
- 상세한 수정 내역 설명 제공

### 2. 🔍 표절 검사 (Plagiarism Detection)
- **Gemini 2.5 Pro AI** 기반 지능형 표절 탐지
- 🌐 인터넷 상 유사 콘텐츠 자동 추적
- 🎯 EXACT(정확 일치) vs SUSPICIOUS(의심) 구간 구분
- 📊 유사도 점수 (0-100) 산출
- 🔗 출처 URL 자동 추출
- 🎨 HTML 하이라이팅으로 시각화
- 표절 의심 부분 상세 분석

### 3. 🤖 AI 텍스트 유사도 검사 (AI Similarity Analysis)
- **멀티 AI 엔진** 기반 정밀 분석:
  - 🤖 **Gemini 2.0 Flash**: 주제 기반 AI 텍스트 생성
  - 🧮 **SBERT (ko-sroberta-multitask)**: 코사인 유사도 계산
  - 📈 **KoGPT2 Perplexity**: 텍스트 자연스러움 측정
- 🎯 Top-3 평균 기반 최종 AI 확률 산출
- 📊 20개 AI 생성 문장과의 유사도 비교
- ⚡ 실시간 스트리밍(SSE) 지원
- AI 작성 확률 해석:
  - **0.0-0.3**: 사람이 작성한 것으로 추정 ✅
  - **0.3-0.6**: 불확실 (혼합 가능성) ⚠️
  - **0.6-0.8**: AI 작성 가능성 높음 🔶
  - **0.8-1.0**: AI 작성으로 강력히 의심 ❌

### 4. 🔐 사용자 인증
- 📧 이메일/비밀번호 기반 회원가입/로그인
- 🎫 JWT 토큰 인증
- 🔑 카카오 OAuth 2.0 소셜 로그인
- 👤 마이페이지 (정보 수정, 비밀번호 변경)
- 👑 관리자 기능 (사용자 관리)

## 🛠️ 기술 스택

### Backend
- **FastAPI 0.118.2**: 비동기 웹 프레임워크
- **SQLModel**: SQLAlchemy + Pydantic ORM
- **SQLite**: 개발용 데이터베이스 (프로덕션: PostgreSQL 권장)
- **Alembic**: DB 마이그레이션
- **Google Gemini API**: 문법/표절/유사도 분석
- **Transformers**: KoGPT2 (perplexity), SBERT (similarity)
- **Uvicorn**: ASGI 서버

### Frontend
- **Vue.js 3**: Composition API
- **Vue Router**: SPA 라우팅
- **Axios**: HTTP 클라이언트
- **Fetch API**: SSE 스트리밍

### AI/ML
- **Gemini 2.0 Flash Experimental**: 문법 검사, 유사도 텍스트 생성
- **Gemini 2.5 Pro**: 표절 탐지
- **SBERT (jhgan/ko-sroberta-multitask)**: 한국어 문장 임베딩
- **KoGPT2 (skt/kogpt2-base-v2)**: 한국어 Perplexity 계산

## 📁 프로젝트 구조

```
AI-killer/
├── Back/                       # 백엔드 (FastAPI)
│   └── Web/
│       ├── main.py            # FastAPI 앱 엔트리포인트
│       ├── config.py          # 환경 설정 (필수 검증 포함)
│       ├── exceptions.py      # 커스텀 예외 클래스
│       ├── database.py        # SQLModel 비동기 DB 엔진
│       ├── models.py          # DB 테이블 및 Pydantic 스키마
│       ├── crud.py            # 데이터베이스 CRUD 함수
│       ├── security.py        # JWT, 비밀번호 해싱
│       ├── dependencies.py    # FastAPI 의존성 주입
│       ├── logging_config.py  # 구조화된 로깅 시스템
│       │
│       ├── gemini_grammar.py       # Gemini 문법 검사
│       ├── gemini_plagiarism.py    # Gemini 표절 검사
│       ├── gemini_similarity.py    # Gemini 유사도 검사
│       ├── perplexity_kobert.py    # KoGPT2 Perplexity
│       ├── sbert_analyzer.py       # SBERT 유사도
│       │
│       ├── api/v1/            # API 라우터
│       │   ├── __init__.py
│       │   ├── grammar.py     # POST /api/v1/grammar/check
│       │   ├── plagiarism.py  # POST /api/v1/plagiarism/check
│       │   ├── similarity.py  # POST /api/v1/similarity/check
│       │   ├── auth.py        # 인증 (카카오 OAuth)
│       │   ├── users.py       # 사용자 관리
│       │   └── admin.py       # 관리자 기능
│       │
│       ├── alembic/           # DB 마이그레이션
│       │   └── versions/
│       │
│       └── tests/             # 단위 테스트
│           ├── test_api_grammar.py
│           ├── test_api_plagiarism.py
│           └── test_api_similarity.py
│
├── Front/                     # 프론트엔드 (Vue.js 3)
│   └── src/
│       ├── App.vue
│       ├── main.js
│       ├── components/
│       │   └── Sidebar.vue
│       ├── views/
│       │   ├── GrammarCheckView.vue       # 문법 검사 페이지
│       │   ├── PlagiarismCheckView.vue    # 표절 검사 페이지
│       │   ├── SimilarityCheckView.vue    # 유사도 검사 페이지
│       │   ├── Login.vue
│       │   ├── SignUpView.vue
│       │   ├── MyPageView.vue
│       │   └── AdminUsersView.vue
│       ├── router/
│       │   └── index.js
│       ├── services/
│       │   └── api.js         # Axios 설정
│       └── store/
│           └── auth.js        # 인증 상태 관리
│
├── .env                       # 환경 변수 (git ignored)
├── requirements.txt           # Python 의존성
├── pyproject.toml            # Python 프로젝트 설정
├── package.json              # 루트 package.json
└── README.md                 # 이 파일
```

## 💾 데이터베이스 구조

### 📋 User 테이블
| 필드 | 타입 | 설명 |
|------|------|------|
| id | Integer | 기본키 |
| username | String | 사용자명 (유니크) |
| email | String | 이메일 (유니크) |
| hashed_password | String | 해시된 비밀번호 (Optional) |
| kakao_id | Integer | 카카오 ID (Optional, 유니크) |
| is_admin | Boolean | 관리자 여부 |
| active | Boolean | 활성 상태 |

### 📊 AnalysisHistory 테이블
| 필드 | 타입 | 설명 |
|------|------|------|
| id | Integer | 기본키 |
| user_id | Integer | 사용자 ID (FK) |
| analysis_type | String | grammar/plagiarism/similarity |
| input_text | String | 입력 텍스트 |
| input_length | Integer | 텍스트 길이 |
| result_data | JSON | 분석 결과 |
| created_at | DateTime | 생성 시각 |

### 📈 ApiUsage 테이블
| 필드 | 타입 | 설명 |
|------|------|------|
| user_id | Integer | 사용자 ID (PK, FK) |
| date | Date | 날짜 (PK) |
| grammar_count | Integer | 문법 검사 횟수 |
| plagiarism_count | Integer | 표절 검사 횟수 |
| similarity_count | Integer | 유사도 검사 횟수 |
| total_count | Integer | 총 사용 횟수 |

## 🚀 빠른 시작 (Quick Start)

### 1️⃣ 환경 설정

```powershell
# 1. 저장소 클론
git clone https://github.com/OHSEONGKWON/AI-killer.git
cd AI-killer

# 2. Python 가상환경 생성 및 활성화
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. 백엔드 의존성 설치
pip install -r requirements.txt

# 4. 환경 변수 설정 (.env 파일 생성)
# 아래 내용을 복사하여 프로젝트 루트에 .env 파일 생성
```

### 2️⃣ .env 파일 설정

```env
# 필수 환경 변수
JWT_SECRET_KEY=your-super-secret-jwt-key-at-least-32-chars-long
GEMINI_API_KEY=your-gemini-api-key-from-google-ai-studio

# 선택적 환경 변수
KAKAO_REST_API_KEY=your-kakao-api-key
KAKAO_REDIRECT_URI=http://localhost:8080/auth/callback
FRONTEND_URL=http://localhost:8080

# 로깅 설정
LOG_LEVEL=INFO
JSON_LOGS=0
ENVIRONMENT=development
```

**🔑 API 키 발급 방법:**
- **JWT_SECRET_KEY**: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- **GEMINI_API_KEY**: [Google AI Studio](https://ai.google.dev/) 에서 발급
- **KAKAO_REST_API_KEY**: [Kakao Developers](https://developers.kakao.com/) 에서 발급

### 3️⃣ 데이터베이스 마이그레이션

```powershell
cd Back/Web
python -m alembic upgrade head
```

### 4️⃣ 서버 실행

**백엔드 (포트 8001):**
```powershell
# Back/Web 디렉토리에서
uvicorn main:app --reload --port 8001
```

**프론트엔드 (포트 8080):**
```powershell
# Front 디렉토리에서
npm install
npm run serve
```

### 5️⃣ 접속

- **프론트엔드**: http://localhost:8080
- **API 문서 (Swagger)**: http://localhost:8001/api/docs
- **API 문서 (ReDoc)**: http://localhost:8001/api/redoc

## 📝 API 엔드포인트

### 문법 검사
```http
POST /api/v1/grammar/check
Content-Type: application/json

{
  "content": "검사할 텍스트를 입력하세요."
}
```

### 표절 검사
```http
POST /api/v1/plagiarism/check
Content-Type: application/json

{
  "content": "표절 검사할 텍스트를 입력하세요."
}
```

### 유사도 검사
```http
POST /api/v1/similarity/check
Content-Type: application/json
Authorization: Bearer <JWT_TOKEN>

{
  "topic": "인공지능의 미래",
  "text": "검사할 텍스트를 입력하세요.",
  "num_sentences": 20
}
```

### 회원가입
```http
POST /api/v1/users/signup
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

## 🧪 테스트 실행

```powershell
# 모든 테스트 실행
pytest -v

# 특정 테스트 실행
pytest tests/test_api_grammar.py -v

# 커버리지 포함
pytest --cov=Back.Web --cov-report=html
```

## 🚢 배포 가이드 (프로덕션)

### 1. 환경 변수 설정
```env
ENVIRONMENT=production
LOG_LEVEL=WARNING
JSON_LOGS=1

# PostgreSQL 사용 권장
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname
```

### 2. Docker 배포 (예시)

**Dockerfile (백엔드):**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY Back/Web /app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
```

**docker-compose.yml:**
```yaml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "8001:8001"
    environment:
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    depends_on:
      - postgres
  
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: ai_killer
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### 3. 보안 체크리스트
- [ ] JWT_SECRET_KEY는 최소 32자 이상의 안전한 랜덤 문자열
- [ ] CORS origins를 프로덕션 도메인으로 제한
- [ ] HTTPS 사용 (Let's Encrypt 권장)
- [ ] API Rate Limiting 적용
- [ ] 환경 변수를 시크릿 매니저에 저장 (AWS Secrets Manager, Azure Key Vault 등)
- [ ] 로그 레벨을 WARNING 이상으로 설정
- [ ] Sentry 등 에러 트래킹 서비스 연동

## 🐛 문제 해결 (Troubleshooting)

### 1. 환경 변수 오류
```
❌ 환경 변수 검증 실패:
  - JWT_SECRET_KEY: Field required
```
**해결**: `.env` 파일에 필수 환경 변수를 설정하세요.

### 2. Gemini API 오류
```
APIKeyError: GEMINI_API_KEY가 설정되지 않았습니다.
```
**해결**: [Google AI Studio](https://ai.google.dev/)에서 API 키 발급 후 `.env`에 추가

### 3. 모델 로딩 오류
```
ModelLoadError: AI 모델 'skt/kogpt2-base-v2' 로딩에 실패했습니다.
```
**해결**: 
- 인터넷 연결 확인
- `pip install transformers sentence-transformers` 재실행
- 첫 실행 시 모델 다운로드로 시간이 소요될 수 있음

### 4. 포트 충돌
```
OSError: [Errno 98] Address already in use
```
**해결**: 다른 포트 사용 `uvicorn main:app --port 8002`

## 📊 성능 최적화 팁

1. **AI 모델 캐싱**: SBERT, KoGPT2 모델은 싱글톤 패턴으로 메모리에 유지됨
2. **비동기 처리**: `asyncio.to_thread`로 블로킹 AI 작업 비동기화
3. **DB 인덱스**: username, email, kakao_id에 인덱스 설정됨
4. **SSE 스트리밍**: 유사도 검사 결과를 실시간으로 전송

## 🤝 기여 (Contributing)

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

MIT License - 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 👥 개발팀

- **OHSEONGKWON** - 백엔드/프론트엔드 개발

## 📞 문의

프로젝트 링크: [https://github.com/OHSEONGKWON/AI-killer](https://github.com/OHSEONGKWON/AI-killer)

---

**⚠️ 주의사항:**
- 이 프로젝트는 교육 및 연구 목적으로 개발되었습니다.
- Gemini API 사용량에 따라 과금될 수 있습니다.
- 프로덕션 환경에서는 반드시 PostgreSQL 등 안정적인 DB 사용을 권장합니다.
- AI 분석 결과는 참고용이며, 100% 정확도를 보장하지 않습니다.
