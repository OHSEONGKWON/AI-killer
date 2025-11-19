# Start Backend Server
Write-Host "Starting Backend Server on port 8001..." -ForegroundColor Green
Push-Location "$PSScriptRoot\Back"
& "$PSScriptRoot\.venv\Scripts\python.exe" -m uvicorn Web.main:app --reload --host 127.0.0.1 --port 8001
Pop-Location
