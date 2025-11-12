# 프론트엔드 연결 가이드

## 📋 체크리스트

### ✅ 백엔드 준비 (완료 여부 확인)

- [ ] 가상환경 활성화
- [ ] 환경변수 설정 (.env)
- [ ] 데이터베이스 마이그레이션
- [ ] 관리자 계정 생성
- [ ] 기본 가중치 설정 초기화
- [ ] 서버 실행 확인

### 🎯 프론트엔드 연결 정보

- **백엔드 서버 주소**: `http://localhost:8000`
- **API 문서 (Swagger)**: `http://localhost:8000/docs`
- **Postman Collection**: `AI-killer.postman_collection.json`

---

## 🔧 1단계: 백엔드 서버 실행

### 1-1. 가상환경 활성화

```powershell
cd C:\GitHub\AI-killer
.\.venv\Scripts\Activate.ps1
```

**확인**: 터미널에 `(.venv)` 표시가 나타나야 합니다.

### 1-2. 환경변수 확인

```powershell
# .env 파일이 없다면 생성
if (!(Test-Path .env)) {
    Copy-Item .env.example .env
    Write-Host "✅ .env 파일 생성 완료! 실제 API 키로 수정하세요." -ForegroundColor Green
} else {
    Write-Host "✅ .env 파일이 이미 존재합니다." -ForegroundColor Green
}
```

**필수 환경변수** (`.env` 파일에서 확인/수정):
```env
JWT_SECRET_KEY=최소_32자_이상의_랜덤_문자열
KAKAO_REST_API_KEY=카카오_개발자_콘솔에서_발급
KAKAO_REDIRECT_URI=http://localhost:8000/api/v1/auth/kakao/callback
```

**JWT 키 생성 명령어**:
```powershell
# PowerShell
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 64 | % {[char]$_})
```

### 1-3. 데이터베이스 마이그레이션

```powershell
cd Back\Web
alembic upgrade head
```

**예상 출력**:
```
INFO  [alembic.runtime.migration] Running upgrade  -> 6de745c9587c, Initial migration
INFO  [alembic.runtime.migration] Running upgrade 6de745c9587c -> bf4638d3da59, Add analysis_config table
```

### 1-4. 서버 실행

```powershell
# 개발 모드 (자동 재시작)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 또는 프로덕션 모드
# uvicorn main:app --host 0.0.0.0 --port 8000
```

**확인**:
- 브라우저에서 http://localhost:8000/docs 접속
- Swagger UI가 정상 표시되면 성공!

---

## 🔐 2단계: 관리자 계정 생성

### 방법 1: Python 스크립트로 생성 (권장)

아래 스크립트를 `create_admin.py`로 저장 후 실행:

```python
# create_admin.py
import asyncio
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from database import engine
from models import User
from security import get_password_hash

async def create_admin():
    async with AsyncSession(engine) as session:
        # 기존 관리자 확인
        statement = select(User).where(User.username == "admin")
        result = await session.exec(statement)
        existing = result.first()
        
        if existing:
            print("⚠️  admin 계정이 이미 존재합니다.")
            return
        
        # 관리자 생성
        admin = User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("admin123"),  # 실제로는 강력한 비밀번호 사용!
            is_admin=True
        )
        session.add(admin)
        await session.commit()
        print("✅ 관리자 계정 생성 완료!")
        print("   Username: admin")
        print("   Password: admin123")
        print("   ⚠️  운영 환경에서는 반드시 비밀번호를 변경하세요!")

if __name__ == "__main__":
    asyncio.run(create_admin())
```

**실행**:
```powershell
python create_admin.py
```

### 방법 2: 데이터베이스에 직접 삽입

```powershell
# SQLite DB 열기
sqlite3 test.db

# 관리자 계정 삽입 (비밀번호 해시는 security.py 참고)
INSERT INTO user (username, email, hashed_password, is_admin) 
VALUES ('admin', 'admin@example.com', '$2b$12$해시된_비밀번호', 1);

# 확인
SELECT * FROM user WHERE is_admin = 1;
.exit
```

---

## 🎛️ 3단계: 기본 가중치 설정 초기화

### 3-1. 관리자 로그인 (토큰 발급)

**API 문서에서 테스트**:
1. http://localhost:8000/docs 접속
2. `POST /api/v1/auth/login` 클릭
3. 아래 내용 입력:
   ```json
   {
     "username": "admin",
     "password": "admin123"
   }
   ```
4. `access_token` 복사

**또는 curl**:
```powershell
curl -X POST http://localhost:8000/api/v1/auth/login `
  -H "Content-Type: application/json" `
  -d '{\"username\":\"admin\",\"password\":\"admin123\"}'
```

### 3-2. 기본 프리셋 생성

**Swagger UI에서**:
1. 오른쪽 상단 `Authorize` 버튼 클릭
2. `Bearer <토큰>` 형식으로 입력
3. `POST /admin/analysis-configs/init-defaults` 실행

**또는 curl**:
```powershell
$token = "여기에_위에서_받은_토큰_붙여넣기"

curl -X POST http://localhost:8000/admin/analysis-configs/init-defaults `
  -H "Authorization: Bearer $token"
```

**예상 응답**:
```json
{
  "message": "3개의 기본 설정이 생성되었습니다.",
  "created": ["paper", "essay", "blog"]
}
```

---

## 🌐 4단계: CORS 설정 확인

### 프론트엔드 서버 주소 추가

`Back/Web/main.py` 파일에서 프론트엔드 주소 확인:

```python
origins = [
    "http://localhost:8080",     # Vue 기본 포트
    "http://127.0.0.1:8080",
    "http://localhost:3000",     # React 기본 포트
    "http://localhost:5173",     # Vite 기본 포트
]
```

**프론트엔드 포트가 다르다면** 위 배열에 추가하고 서버 재시작!

---

## 📡 5단계: API 엔드포인트 테스트

### 주요 엔드포인트 목록

#### 🔓 인증 (Authentication)
- `POST /api/v1/auth/login` - 로그인 (토큰 발급)
- `POST /api/v1/auth/register` - 회원가입
- `GET /api/v1/auth/kakao` - 카카오 로그인
- `POST /api/v1/auth/kakao/callback` - 카카오 콜백

#### 📊 AI 분석 (Analysis)
- `POST /api/v1/analyze` - AI 작성 확률 분석 (4가지 지표)

**요청 예시**:
```json
{
  "title": "인공지능의 미래",
  "content": "인공지능 기술은 우리 사회의 많은 분야에서...",
  "text_type": "paper"  // paper, essay, blog
}
```

**응답 예시**:
```json
{
  "ai_probability": 0.75,
  "analysis_details": {
    "kobert_score": 0.8,
    "similarity_score": 0.7,
    "perplexity_score": 0.75,
    "burstiness_score": 0.7
  }
}
```

#### 📝 표절 검사 (Plagiarism)
- `POST /api/v1/plagiarism/check` - 표절 검사

#### ✏️ 문법 검사 (Grammar)
- `POST /api/v1/grammar/check` - 문법 검사

#### 👤 사용자 관리 (Users)
- `GET /api/v1/users/me` - 현재 사용자 정보 조회 (로그인 필요)

#### 👨‍💼 관리자 기능 (Admin)
- `GET /admin/analysis-configs` - 모든 가중치 설정 조회
- `GET /admin/analysis-configs/{text_type}` - 특정 유형 조회
- `POST /admin/analysis-configs` - 새 설정 생성
- `PUT /admin/analysis-configs/{text_type}` - 설정 수정
- `DELETE /admin/analysis-configs/{text_type}` - 설정 삭제
- `POST /admin/analysis-configs/init-defaults` - 기본 프리셋 생성

---

## 🧪 6단계: Postman으로 테스트 (선택)

### Postman Collection 임포트

1. Postman 열기
2. `File` → `Import`
3. `AI-killer.postman_collection.json` 선택
4. 26개 엔드포인트 자동 로드

### 환경변수 설정

Postman에서 `Variables` 탭:
```
base_url = http://localhost:8000
token = (로그인 후 자동 설정)
```

---

## 🔥 7단계: 프론트엔드에서 호출하기

### Vue.js / React / Angular 예시

#### 1. Axios 설치
```bash
npm install axios
```

#### 2. API 클라이언트 생성

```javascript
// api/client.js
import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// 토큰 자동 추가 (로그인 후)
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 에러 처리
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // 토큰 만료 시 로그인 페이지로
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

#### 3. API 함수 작성

```javascript
// api/analysis.js
import apiClient from './client';

export const analyzeText = async (title, content, textType = 'paper') => {
  const response = await apiClient.post('/api/v1/analyze', {
    title,
    content,
    text_type: textType,
  });
  return response.data;
};

// 사용 예시
const result = await analyzeText(
  '인공지능의 미래',
  '인공지능 기술은...',
  'paper'
);
console.log('AI 확률:', result.ai_probability);
```

#### 4. 로그인/로그아웃

```javascript
// api/auth.js
import apiClient from './client';

export const login = async (username, password) => {
  const response = await apiClient.post('/api/v1/auth/login', {
    username,
    password,
  });
  
  const { access_token } = response.data;
  localStorage.setItem('access_token', access_token);
  
  return response.data;
};

export const logout = () => {
  localStorage.removeItem('access_token');
};

export const getCurrentUser = async () => {
  const response = await apiClient.get('/api/v1/users/me');
  return response.data;
};
```

---

## 🐛 문제 해결 (Troubleshooting)

### ❌ CORS 오류: "No 'Access-Control-Allow-Origin' header"

**원인**: 프론트엔드 주소가 CORS 설정에 없음

**해결**:
1. `Back/Web/main.py` 열기
2. `origins` 배열에 프론트엔드 주소 추가:
   ```python
   origins = [
       "http://localhost:8080",
       "http://localhost:3000",  # 추가
       "http://프론트엔드주소",   # 추가
   ]
   ```
3. 백엔드 서버 재시작

### ❌ 401 Unauthorized

**원인**: 토큰이 없거나 만료됨

**해결**:
1. 로그인 API 호출하여 새 토큰 발급
2. `Authorization: Bearer <토큰>` 헤더 확인
3. 토큰 만료 시간 확인 (기본 60분)

### ❌ 422 Unprocessable Entity

**원인**: 요청 데이터 검증 실패

**해결**:
1. API 문서(/docs)에서 필수 필드 확인
2. 데이터 타입 확인 (문자열, 숫자, 불리언 등)
3. 예시:
   ```json
   {
     "title": "필수",        // ✅ 문자열
     "content": "필수",      // ✅ 문자열
     "text_type": "paper"   // ✅ 선택 (기본값: paper)
   }
   ```

### ❌ 500 Internal Server Error

**원인**: 서버 내부 오류

**해결**:
1. 백엔드 터미널에서 오류 로그 확인
2. `.env` 파일의 환경변수 확인
3. 데이터베이스 마이그레이션 상태 확인:
   ```powershell
   alembic current
   alembic upgrade head
   ```

---

## 📚 추가 자료

- **API 문서**: http://localhost:8000/docs (Swagger UI)
- **Postman Collection**: `AI-killer.postman_collection.json`
- **README**: 전체 프로젝트 가이드
- **GitHub Issues**: https://github.com/OHSEONGKWON/AI-killer/issues

---

## ✅ 연결 완료 체크리스트

프론트엔드 팀에게 전달할 정보:

- [ ] 백엔드 서버 주소: `http://localhost:8000`
- [ ] API 문서 주소: `http://localhost:8000/docs`
- [ ] Postman Collection 파일 공유
- [ ] 테스트 계정 (username/password) 공유
- [ ] 주요 엔드포인트 목록 공유
- [ ] CORS 설정에 프론트엔드 주소 추가 완료
- [ ] WebSocket 필요 시 별도 논의

---

**🎉 모든 준비가 완료되었습니다!**

문제가 발생하면 백엔드 터미널의 로그를 확인하거나 `/docs`에서 직접 테스트해보세요.
