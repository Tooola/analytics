Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Starting Open Analytics AI Stack" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 1. Start FastAPI Backend in background job
Write-Host "`n[1/2] Launching Backend on http://127.0.0.1:8000..." -ForegroundColor Yellow
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:PSScriptRoot\backend
    & .\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
}

# 2. Wait for backend to be ready
Start-Sleep -Seconds 3

# 3. Start Vite React Frontend
Write-Host "[2/2] Launching React Dashboard on http://localhost:5173..." -ForegroundColor Green
Set-Location "$PSScriptRoot\frontend"
npm run dev
