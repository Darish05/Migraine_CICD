# Docker Deployment Script - Clean Version
# Deploys the Migraine ML Pipeline to Docker

$ErrorActionPreference = "Continue"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  DOCKER DEPLOYMENT - MIGRAINE ML" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Check Docker installed
Write-Host "[1/10] Checking Docker installation..." -ForegroundColor Yellow
$dockerCmd = Get-Command docker -ErrorAction SilentlyContinue
if (-not $dockerCmd) {
    Write-Host "   ERROR: Docker not installed!" -ForegroundColor Red
    Write-Host "   Download from: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}
Write-Host "   OK - Docker found" -ForegroundColor Green

# Check Docker running
Write-Host "`n[2/10] Checking if Docker is running..." -ForegroundColor Yellow
docker info 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "   ERROR: Docker Desktop is not running!" -ForegroundColor Red
    Write-Host "`n   Please:" -ForegroundColor Yellow
    Write-Host "   1. Open Docker Desktop application" -ForegroundColor White
    Write-Host "   2. Wait for it to fully start (30-60 seconds)" -ForegroundColor White
    Write-Host "   3. Look for solid Docker icon in system tray" -ForegroundColor White
    Write-Host "   4. Run this script again`n" -ForegroundColor White
    exit 1
}
Write-Host "   OK - Docker is running" -ForegroundColor Green

# Check models exist
Write-Host "`n[3/10] Checking for trained models..." -ForegroundColor Yellow
if (-not (Test-Path "classification_model_top1.pkl")) {
    Write-Host "   ERROR: Models not found!" -ForegroundColor Red
    Write-Host "   Run: .\run.ps1 first to train models`n" -ForegroundColor Yellow
    exit 1
}
Write-Host "   OK - Models found" -ForegroundColor Green

# Check app.py
Write-Host "`n[4/10] Checking application files..." -ForegroundColor Yellow
if (-not (Test-Path "app.py")) {
    Write-Host "   ERROR: app.py not found!" -ForegroundColor Red
    exit 1
}
Write-Host "   OK - Application files present" -ForegroundColor Green

# Check Dockerfile
Write-Host "`n[5/10] Checking Docker files..." -ForegroundColor Yellow
if (-not (Test-Path "Dockerfile")) {
    Write-Host "   ERROR: Dockerfile not found!" -ForegroundColor Red
    exit 1
}
if (-not (Test-Path "docker-compose.yml")) {
    Write-Host "   ERROR: docker-compose.yml not found!" -ForegroundColor Red
    exit 1
}
Write-Host "   OK - Docker files present" -ForegroundColor Green

# Stop existing containers
Write-Host "`n[6/10] Cleaning up old containers..." -ForegroundColor Yellow
docker-compose down 2>&1 | Out-Null
Write-Host "   OK - Cleanup complete" -ForegroundColor Green

# Build Docker image
Write-Host "`n[7/10] Building Docker image..." -ForegroundColor Yellow
Write-Host "   (This may take 5-10 minutes on first build)" -ForegroundColor Cyan
docker build -t migraine-ml-api:latest . 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "   ERROR: Docker build failed!" -ForegroundColor Red
    Write-Host "   Check the error messages above" -ForegroundColor Yellow
    exit 1
}
Write-Host "   OK - Image built successfully" -ForegroundColor Green

# Start containers
Write-Host "`n[8/10] Starting Docker services..." -ForegroundColor Yellow
docker-compose up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "   ERROR: Failed to start services!" -ForegroundColor Red
    Write-Host "   Run: docker-compose logs" -ForegroundColor Yellow
    exit 1
}
Write-Host "   OK - Services started" -ForegroundColor Green

# Wait for services
Write-Host "`n[9/10] Waiting for services to be ready..." -ForegroundColor Yellow
Write-Host "   Waiting 15 seconds..." -ForegroundColor Cyan
Start-Sleep -Seconds 15
Write-Host "   OK - Wait complete" -ForegroundColor Green

# Test API
Write-Host "`n[10/10] Testing API health..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -ErrorAction Stop
    Write-Host "   OK - API is healthy!" -ForegroundColor Green
    Write-Host "   Status: $($response.status)" -ForegroundColor Green
} catch {
    Write-Host "   WARNING - API not responding yet" -ForegroundColor Yellow
    Write-Host "   Wait a few more seconds and check: http://localhost:8000/health" -ForegroundColor Cyan
}

# Success message
Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  DEPLOYMENT SUCCESSFUL!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green

Write-Host "Access your services:" -ForegroundColor Cyan
Write-Host "  API Docs:    http://localhost:8000/docs" -ForegroundColor White
Write-Host "  Health:      http://localhost:8000/health" -ForegroundColor White
Write-Host "  MLflow UI:   http://localhost:5000`n" -ForegroundColor White

Write-Host "Useful commands:" -ForegroundColor Cyan
Write-Host "  View logs:   docker-compose logs -f" -ForegroundColor White
Write-Host "  Stop:        docker-compose down" -ForegroundColor White
Write-Host "  Restart:     docker-compose restart`n" -ForegroundColor White

Write-Host "Your ML API is now running in Docker!" -ForegroundColor Green
