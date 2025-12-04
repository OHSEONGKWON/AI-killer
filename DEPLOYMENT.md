# 배포 가이드

## 환경 설정

### 필수 환경 변수
- `JWT_SECRET_KEY`: JWT 토큰 서명 키
- `GEMINI_API_KEY`: Google Gemini API 키

### 선택적 환경 변수
- `SERPER_API_KEY`: Serper 웹 검색 API 키
- `KAKAO_REST_API_KEY`: 카카오 OAuth API 키
- `OPENAI_API_KEY`: OpenAI API 키

## 로컬 실행

```bash
# 백엔드
cd Back/Web
uvicorn main:app --reload --port 8001

# 프론트엔드
cd Front
npm run serve --port 8080
```

## 프로덕션 배포

Docker를 사용한 컨테이너 배포가 권장됩니다.

```bash
docker-compose up -d
```

## 데이터베이스 마이그레이션

```bash
cd Back/Web
alembic upgrade head
```
