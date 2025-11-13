# Start both frontend and backend servers

Write-Host "Starting Backend Server..." -ForegroundColor Green
$backendJob = Start-Job -ScriptBlock {
    $ErrorActionPreference = "Continue"
    Push-Location C:\GitHub\AI-killer\Back
    & C:\GitHub\AI-killer\.venv\Scripts\python.exe -m uvicorn Web.main:app --reload --host 0.0.0.0 --port 8000
}

Write-Host "Starting Frontend Server..." -ForegroundColor Green
$frontendJob = Start-Job -ScriptBlock {
    $ErrorActionPreference = "Continue"
    Push-Location C:\GitHub\AI-killer\Front
    & .\node_modules\.bin\vue-cli-service.cmd serve
}

Write-Host "Both servers are starting in background jobs..." -ForegroundColor Cyan
Write-Host "Backend Job ID: $($backendJob.Id)" -ForegroundColor Yellow
Write-Host "Frontend Job ID: $($frontendJob.Id)" -ForegroundColor Yellow
Write-Host ""
Write-Host "To check backend output: Receive-Job -Id $($backendJob.Id) -Keep" -ForegroundColor Magenta
Write-Host "To check frontend output: Receive-Job -Id $($frontendJob.Id) -Keep" -ForegroundColor Magenta
Write-Host "To stop servers: Stop-Job -Id $($backendJob.Id),$($frontendJob.Id)" -ForegroundColor Red

# Wait a bit for servers to start
Start-Sleep -Seconds 5

# Show initial output
Write-Host "`n=== Backend Output ===" -ForegroundColor Green
Receive-Job -Id $backendJob.Id -Keep | Select-Object -Last 10

Write-Host "`n=== Frontend Output ===" -ForegroundColor Green
Receive-Job -Id $frontendJob.Id -Keep | Select-Object -Last 10

Write-Host "`nServers are running. Access at:" -ForegroundColor Cyan
Write-Host "  Frontend: http://localhost:8080" -ForegroundColor Yellow
Write-Host "  Backend:  http://localhost:8000/docs" -ForegroundColor Yellow
