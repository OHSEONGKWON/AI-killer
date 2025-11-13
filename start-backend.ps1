# Start Backend Server
Write-Host "Starting Backend Server on port 8000..." -ForegroundColor Green
Push-Location "$PSScriptRoot\Back"
& "$PSScriptRoot\.venv\Scripts\python.exe" -m uvicorn Web.main:app --reload --host 0.0.0.0 --port 8000
Pop-Location
