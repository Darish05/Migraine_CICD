# Docker Image Build Script
# Builds the Migraine ML Docker image with error handling

$ErrorActionPreference = "Continue"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  DOCKER IMAGE BUILD - MIGRAINE ML" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Navigate to project directory
Set-Location "D:\Mlops\migraine-ml"

# Step 1: Check Docker
Write-Host "[1/8] Checking Docker..." -ForegroundColor Yellow
$dockerCmd = Get-Command docker -ErrorAction SilentlyContinue
if (-not $dockerCmd) {
    Write-Host "   ERROR: Docker not installed!" -ForegroundColor Red
    exit 1
}
Write-Host "   OK" -ForegroundColor Green

# Step 2: Check Docker running
Write-Host "`n[2/8] Checking if Docker is running..." -ForegroundColor Yellow
docker info 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "   ERROR: Docker Desktop is not running!" -ForegroundColor Red
    Write-Host "`n   Please start Docker Desktop and try again.`n" -ForegroundColor Yellow
    exit 1
}
Write-Host "   OK - Docker is running" -ForegroundColor Green

# Step 3: Check Dockerfile
Write-Host "`n[3/8] Checking Dockerfile..." -ForegroundColor Yellow
if (-not (Test-Path "Dockerfile")) {
    Write-Host "   ERROR: Dockerfile not found!" -ForegroundColor Red
    exit 1
}
Write-Host "   OK" -ForegroundColor Green

# Step 4: Check app.py
Write-Host "`n[4/8] Checking app.py..." -ForegroundColor Yellow
if (-not (Test-Path "app.py")) {
    Write-Host "   ERROR: app.py not found!" -ForegroundColor Red
    exit 1
}
Write-Host "   OK" -ForegroundColor Green

# Step 5: Check requirements.txt
Write-Host "`n[5/8] Checking requirements.txt..." -ForegroundColor Yellow
if (-not (Test-Path "requirements.txt")) {
    Write-Host "   ERROR: requirements.txt not found!" -ForegroundColor Red
    exit 1
}
Write-Host "   OK" -ForegroundColor Green

# Step 6: Check models
Write-Host "`n[6/8] Checking model files..." -ForegroundColor Yellow
$models = Get-ChildItem -Filter "*.pkl" -ErrorAction SilentlyContinue
if ($models.Count -eq 0) {
    Write-Host "   WARNING: No .pkl model files found!" -ForegroundColor Yellow
    Write-Host "   Run: .\run.ps1 first to train models" -ForegroundColor Yellow
    $continue = Read-Host "   Continue anyway? (yes/no)"
    if ($continue -ne "yes") {
        exit 1
    }
} else {
    Write-Host "   OK - Found $($models.Count) model files" -ForegroundColor Green
}

# Step 7: Clean old images (optional)
Write-Host "`n[7/8] Cleaning old images..." -ForegroundColor Yellow
docker rmi migraine-ml-api:latest 2>&1 | Out-Null
docker rmi darish05/migraine-ml:latest 2>&1 | Out-Null
Write-Host "   OK" -ForegroundColor Green

# Step 8: Build image
Write-Host "`n[8/8] Building Docker image..." -ForegroundColor Yellow
Write-Host "   This may take 5-10 minutes..." -ForegroundColor Cyan
Write-Host "   Image: darish05/migraine-ml:latest`n" -ForegroundColor Cyan

# Build with proper error handling
docker build -t darish05/migraine-ml:latest -t migraine-ml-api:latest . 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host "  BUILD SUCCESSFUL!" -ForegroundColor Green
    Write-Host "========================================`n" -ForegroundColor Green
    
    Write-Host "Image created:" -ForegroundColor Cyan
    docker images darish05/migraine-ml:latest
    
    Write-Host "`nNext steps:" -ForegroundColor Cyan
    Write-Host "  1. Test locally:  docker run -p 8000:8000 darish05/migraine-ml:latest" -ForegroundColor White
    Write-Host "  2. Start compose: docker-compose up -d" -ForegroundColor White
    Write-Host "  3. Push to hub:   docker push darish05/migraine-ml:latest" -ForegroundColor White
    Write-Host "  4. Deploy to K8s: kubectl apply -f kubernetes/deployment.yaml`n" -ForegroundColor White
} else {
    Write-Host "`n========================================" -ForegroundColor Red
    Write-Host "  BUILD FAILED!" -ForegroundColor Red
    Write-Host "========================================`n" -ForegroundColor Red
    
    Write-Host "Common issues:" -ForegroundColor Yellow
    Write-Host "  1. Docker Desktop not running" -ForegroundColor White
    Write-Host "  2. Missing files (app.py, requirements.txt)" -ForegroundColor White
    Write-Host "  3. Syntax errors in Dockerfile" -ForegroundColor White
    Write-Host "  4. Network issues during pip install" -ForegroundColor White
    Write-Host "`nCheck the error messages above for details.`n" -ForegroundColor Yellow
    
    exit 1
}
