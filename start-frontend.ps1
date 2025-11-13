# Start Frontend Server
Write-Host "Starting Frontend Server on port 8080..." -ForegroundColor Green
Push-Location "$PSScriptRoot\Front"
& ".\node_modules\.bin\vue-cli-service.cmd" serve
Pop-Location
