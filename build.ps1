# SIMPLE DOCKER BUILD - Step by Step
Write-Host "`n=== DOCKER BUILD - STEP BY STEP ===" -ForegroundColor Cyan

# Step 1: Check Docker
Write-Host "`n[1/5] Checking Docker..." -ForegroundColor Yellow
docker info 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Docker not running!" -ForegroundColor Red
    Write-Host "Please start Docker Desktop first" -ForegroundColor Yellow
    exit 1
}
Write-Host "OK - Docker is running" -ForegroundColor Green

# Step 2: Check models
Write-Host "`n[2/5] Checking models..." -ForegroundColor Yellow
if (-not (Test-Path "*.pkl")) {
    Write-Host "ERROR: No models found!" -ForegroundColor Red
    Write-Host "Run: .\run.ps1 first" -ForegroundColor Yellow
    exit 1
}
Write-Host "OK - Models found" -ForegroundColor Green

# Step 3: Stop old containers
Write-Host "`n[3/5] Stopping old containers..." -ForegroundColor Yellow
docker-compose down 2>&1 | Out-Null
Write-Host "OK" -ForegroundColor Green

# Step 4: Build image
Write-Host "`n[4/5] Building Docker image (5-10 min)..." -ForegroundColor Yellow
docker build -t migraine-ml-api:latest .
if ($LASTEXITCODE -ne 0) {
    Write-Host "`nERROR: Build failed!" -ForegroundColor Red
    exit 1
}
Write-Host "`nOK - Build successful" -ForegroundColor Green

# Step 5: Start containers
Write-Host "`n[5/5] Starting containers..." -ForegroundColor Yellow
docker-compose up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to start!" -ForegroundColor Red
    exit 1
}
Write-Host "OK - Started" -ForegroundColor Green

Write-Host "`n=== SUCCESS ===" -ForegroundColor Green
Write-Host "API: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "MLflow: http://localhost:5000`n" -ForegroundColor Cyan
