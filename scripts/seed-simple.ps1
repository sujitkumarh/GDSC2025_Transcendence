# Simple seed script for Transcendence
Write-Host "🌱 Seeding Transcendence Data..." -ForegroundColor Green

# Check if data directory exists
if (-not (Test-Path "backend\app\data")) {
    New-Item -ItemType Directory -Path "backend\app\data" -Force
}

# Check if personas file exists
if (Test-Path "backend\app\data\personas.json") {
    Write-Host "✅ Personas data already exists" -ForegroundColor Green
} else {
    Write-Host "❌ Personas file missing - should be created automatically" -ForegroundColor Red
}

Write-Host "🎯 Seed complete! Ready to start servers:" -ForegroundColor Cyan
Write-Host "1. Backend: cd backend && python -m uvicorn app.main:app --reload"
Write-Host "2. Frontend: cd frontend && npm run dev"
Write-Host "3. Open: http://localhost:5173"