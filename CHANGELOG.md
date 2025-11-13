# Changelog

## [2025-11-13] 품질 개선 업데이트

### ✨ 프론트엔드 개선
- **API 호출 통합**: 모든 API 호출을 `services/api.js`로 통일
  - Axios 인터셉터 추가로 JWT 토큰 자동 전송
  - 401 에러 시 자동 로그아웃 처리
  - `authAPI`, `analysisAPI` 메서드로 구조화
  
- **인증 상태 관리 개선**: `store/auth.js` 실제 사용
  - 앱 시작 시 localStorage 토큰으로 사용자 정보 자동 로드
  - 로그인 시 사용자 정보 스토어에 저장
  - 헤더에 사용자명 표시
  
- **Loading 상태 추가**: 회원가입/로그인 버튼에 로딩 표시
  - 중복 요청 방지 (disabled 처리)
  - 사용자 피드백 개선

### 🔒 백엔드 보안 & 검증 강화
- **입력 검증 강화**: Pydantic Field로 데이터 유효성 검사
  - 비밀번호: 6~50자 제한
  - 분석 텍스트: 10~10000자 제한
  - 제목: 최대 200자 제한
  
- **중복 검사 개선**: 회원가입 시 email 중복도 확인
  - `get_user_by_email()` 함수 추가
  - username과 email 모두 중복 검사
  
- **환경 변수 검증**: 서버 시작 시 필수 설정 확인
  - JWT_SECRET_KEY 누락 시 에러 경고
  - KAKAO_API_KEY, OPENAI_API_KEY 누락 시 경고
  - `validate_required_settings()` 함수로 자동 검증

### 📡 API 개선
- **GET /users/me 추가**: 현재 사용자 정보 조회 엔드포인트
  - JWT 토큰으로 인증
  - 프론트엔드 auth 초기화에 사용

### 🐛 버그 수정
- App.vue에서 auth.user → auth.state 수정
- HomeView.vue에서 axios 직접 호출 → analysisAPI 사용
- Login/SignUp에서 중복 코드 제거

### 📝 코드 품질
- 입력 검증 중복 코드 제거
- 에러 메시지 일관성 개선
- TypeScript 스타일 개선 (명확한 타입)

---

## [2025-11-12] 인증 시스템 수정

### 🔐 보안 개선
- **bcrypt 72바이트 제한 처리**: `security.py`에 password truncation 추가
- **프론트엔드 비밀번호 검증**: 6~50자 제한 (HTML5 + JS)

### 🔧 버그 수정
- **AsyncSession 호환성**: `db.exec()` → `db.execute()` + `scalars()`
- **.env 경로 수정**: `Path(__file__).parent.parent.parent / ".env"`
- **CORS 설정**: 8080, 8081 포트 모두 허용

### 📦 기능 추가
- **카카오 OAuth 콜백 컴포넌트**: `AuthCallback.vue`
- **서버 시작 스크립트**: `start-backend.ps1`, `start-frontend.ps1`

---

## [Initial Release] 기본 구조

- FastAPI 백엔드 구조
- Vue 3 프론트엔드
- JWT 인증 시스템
- 4가지 AI 분석 지표 프레임워크
- SQLite 데이터베이스
- Alembic 마이그레이션
