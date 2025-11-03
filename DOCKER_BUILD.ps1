Write-Host "`n======================================" -ForegroundColor Cyan
Write-Host "  DOCKER BUILD - MIGRAINE ML API" -ForegroundColor Cyan
Write-Host "======================================`n" -ForegroundColor Cyan

Set-Location D:\Mlops\migraine-ml

Write-Host "[1/5] Checking Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version
    Write-Host $dockerVersion -ForegroundColor Green
} catch {
    Write-Host "ERROR: Docker is not running!" -ForegroundColor Red
    Write-Host "Please start Docker Desktop and try again." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "`n[2/5] Checking required files..." -ForegroundColor Yellow
if (!(Test-Path Dockerfile)) {
    Write-Host "ERROR: Dockerfile not found!" -ForegroundColor Red
    exit 1
}
if (!(Test-Path docker-compose.yml)) {
    Write-Host "ERROR: docker-compose.yml not found!" -ForegroundColor Red
    exit 1
}
if (!(Test-Path models\classification_model_top1.pkl)) {
    Write-Host "ERROR: Models not found!" -ForegroundColor Red
    exit 1
}
Write-Host "All files present!" -ForegroundColor Green

Write-Host "`n[3/5] Cleaning old containers..." -ForegroundColor Yellow
docker-compose down 2>$null
Write-Host "Cleanup complete!" -ForegroundColor Green

Write-Host "`n[4/5] Building Docker image..." -ForegroundColor Yellow
Write-Host "This will take 5-10 minutes. Please wait...`n" -ForegroundColor Cyan
docker build -t migraine-ml-api:latest .

if ($LASTEXITCODE -ne 0) {
    Write-Host "`nERROR: Docker build failed!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "`n[5/5] Starting containers..." -ForegroundColor Yellow
docker-compose up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "`nERROR: Failed to start containers!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "`n======================================" -ForegroundColor Green
Write-Host "  SUCCESS!" -ForegroundColor Green
Write-Host "======================================`n" -ForegroundColor Green

Write-Host "Your API is now running at:" -ForegroundColor Cyan
Write-Host "  http://localhost:8000`n" -ForegroundColor Yellow

Write-Host "Test it with:" -ForegroundColor Cyan
Write-Host "  curl http://localhost:8000/health`n" -ForegroundColor White

Write-Host "View logs with:" -ForegroundColor Cyan
Write-Host "  docker-compose logs -f`n" -ForegroundColor White

Write-Host "Stop containers with:" -ForegroundColor Cyan
Write-Host "  docker-compose down`n" -ForegroundColor White

Read-Host "Press Enter to exit"
