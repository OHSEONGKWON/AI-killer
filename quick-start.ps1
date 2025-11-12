# ============================================================================
# AI-killer 백엔드 빠른 시작 스크립트 (PowerShell)
# ============================================================================
# 프론트엔드 연결을 위해 백엔드를 한 번에 준비합니다.
# 
# 사용법:
#   .\quick-start.ps1
#
# 또는 권한 오류 시:
#   Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
#   .\quick-start.ps1
# ============================================================================

Write-Host "`n🚀 AI-killer 백엔드 빠른 시작" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan

# 0. 현재 위치 확인
$ProjectRoot = "C:\GitHub\AI-killer"
if ($PWD.Path -ne $ProjectRoot) {
    Write-Host "`n📂 프로젝트 루트로 이동 중..." -ForegroundColor Yellow
    Set-Location $ProjectRoot
}

# 1. 가상환경 확인
Write-Host "`n✅ 1단계: 가상환경 확인" -ForegroundColor Green
if (!(Test-Path ".venv")) {
    Write-Host "   ❌ 가상환경이 없습니다. 먼저 생성하세요:" -ForegroundColor Red
    Write-Host "      python -m venv .venv" -ForegroundColor Yellow
    exit 1
}

Write-Host "   ✓ 가상환경 존재 확인" -ForegroundColor Gray

# 가상환경 활성화
Write-Host "   ✓ 가상환경 활성화 중..." -ForegroundColor Gray
& ".\.venv\Scripts\Activate.ps1"

# 2. 환경변수 파일 확인
Write-Host "`n✅ 2단계: 환경변수 확인" -ForegroundColor Green
if (!(Test-Path ".env")) {
    Write-Host "   ⚠️  .env 파일이 없습니다. 생성 중..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "   ✓ .env 파일 생성 완료" -ForegroundColor Gray
    Write-Host "   ⚠️  JWT_SECRET_KEY와 API 키를 설정하세요!" -ForegroundColor Yellow
    
    # JWT 키 자동 생성
    Write-Host "`n   🔑 JWT Secret Key 생성 중..." -ForegroundColor Cyan
    $jwtKey = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 64 | ForEach-Object {[char]$_})
    
    # .env 파일에서 JWT_SECRET_KEY 교체
    $envContent = Get-Content .env
    $envContent = $envContent -replace "JWT_SECRET_KEY=your_super_secret.*", "JWT_SECRET_KEY=$jwtKey"
    $envContent | Set-Content .env
    
    Write-Host "   ✓ JWT_SECRET_KEY 자동 생성 완료" -ForegroundColor Gray
} else {
    Write-Host "   ✓ .env 파일 존재 확인" -ForegroundColor Gray
}

# 3. 데이터베이스 마이그레이션
Write-Host "`n✅ 3단계: 데이터베이스 마이그레이션" -ForegroundColor Green
Set-Location "Back\Web"

Write-Host "   ✓ 마이그레이션 실행 중..." -ForegroundColor Gray
$migrationOutput = alembic upgrade head 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✓ 마이그레이션 완료" -ForegroundColor Gray
} else {
    Write-Host "   ⚠️  마이그레이션 경고 (무시 가능)" -ForegroundColor Yellow
}

# 4. 관리자 계정 생성
Write-Host "`n✅ 4단계: 관리자 계정 생성" -ForegroundColor Green
Write-Host "   ✓ 관리자 계정 생성 중..." -ForegroundColor Gray
python create_admin.py

# 5. 서버 시작 안내
Write-Host "`n" + ("=" * 60) -ForegroundColor Cyan
Write-Host "🎉 백엔드 준비 완료!" -ForegroundColor Green
Write-Host ("=" * 60) -ForegroundColor Cyan

Write-Host "`n📡 다음 단계:" -ForegroundColor Cyan
Write-Host "   1. 서버 실행:" -ForegroundColor Yellow
Write-Host "      uvicorn main:app --reload --host 0.0.0.0 --port 8000`n" -ForegroundColor White

Write-Host "   2. API 문서 확인:" -ForegroundColor Yellow
Write-Host "      http://localhost:8000/docs`n" -ForegroundColor White

Write-Host "   3. 기본 가중치 설정 초기화 (서버 실행 후):" -ForegroundColor Yellow
Write-Host "      a. http://localhost:8000/docs 접속" -ForegroundColor Gray
Write-Host "      b. POST /api/v1/auth/login 으로 로그인 (admin/admin123)" -ForegroundColor Gray
Write-Host "      c. 우측 상단 Authorize 버튼 클릭, 토큰 입력" -ForegroundColor Gray
Write-Host "      d. POST /admin/analysis-configs/init-defaults 실행`n" -ForegroundColor Gray

Write-Host "   4. 프론트엔드 CORS 설정:" -ForegroundColor Yellow
Write-Host "      main.py의 origins 배열에 프론트엔드 주소 추가`n" -ForegroundColor Gray

Write-Host "📚 상세 가이드: FRONTEND_SETUP.md" -ForegroundColor Cyan
Write-Host ("=" * 60) -ForegroundColor Cyan

Write-Host "`n💡 서버를 시작하려면 아래 명령어를 입력하세요:" -ForegroundColor Yellow
Write-Host "   uvicorn main:app --reload`n" -ForegroundColor White
