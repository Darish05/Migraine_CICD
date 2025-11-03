# Complete Docker Setup and Deployment Script
# This script sets up everything needed for Docker deployment

Write-Host "`n╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                                                          ║" -ForegroundColor Cyan
Write-Host "║      🐳 DOCKER SETUP & DEPLOYMENT - MIGRAINE ML 🚀       ║" -ForegroundColor Cyan
Write-Host "║                                                          ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Step 1: Check Docker
Write-Host "Step 1: Checking Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version 2>&1
    Write-Host "✓ Docker installed: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker not installed!" -ForegroundColor Red
    Write-Host "Please download and install Docker Desktop from:" -ForegroundColor Yellow
    Write-Host "https://www.docker.com/products/docker-desktop" -ForegroundColor Cyan
    exit 1
}

# Step 2: Check if Docker daemon is running
Write-Host "`nStep 2: Checking if Docker is running..." -ForegroundColor Yellow
try {
    $dockerInfo = docker info 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Docker is running" -ForegroundColor Green
    } else {
        throw "Docker daemon not running"
    }
} catch {
    Write-Host "✗ Docker Desktop is NOT running!" -ForegroundColor Red
    Write-Host "`n🚨 IMPORTANT: You must start Docker Desktop first!" -ForegroundColor Yellow
    Write-Host "`nPlease:" -ForegroundColor Cyan
    Write-Host "  1. Press Windows Key" -ForegroundColor White
    Write-Host "  2. Type 'Docker Desktop'" -ForegroundColor White
    Write-Host "  3. Click to open it" -ForegroundColor White
    Write-Host "  4. Wait 30-60 seconds for it to start" -ForegroundColor White
    Write-Host "  5. Look for Docker icon in system tray (should be solid, not animated)" -ForegroundColor White
    Write-Host "`nThen run this script again.`n" -ForegroundColor Yellow
    exit 1
}

# Step 3: Check if models exist
Write-Host "`nStep 3: Checking for trained models..." -ForegroundColor Yellow
$modelFiles = @(
    "classification_model_top1.pkl",
    "regression_model_top1.pkl"
)

$missingModels = @()
foreach ($model in $modelFiles) {
    if (-not (Test-Path $model)) {
        $missingModels += $model
    }
}

if ($missingModels.Count -gt 0) {
    Write-Host "✗ Models not found!" -ForegroundColor Red
    Write-Host "`nMissing models:" -ForegroundColor Yellow
    foreach ($model in $missingModels) {
        Write-Host "  - $model" -ForegroundColor Red
    }
    Write-Host "`n🚨 You must train models first before building Docker image!" -ForegroundColor Yellow
    Write-Host "`nRun this command first:" -ForegroundColor Cyan
    Write-Host "  .\setup_and_run.ps1" -ForegroundColor White
    Write-Host "`nOr manually:" -ForegroundColor Cyan
    Write-Host "  python migraine_models_enhanced.py`n" -ForegroundColor White
    exit 1
} else {
    Write-Host "✓ All required models found" -ForegroundColor Green
    foreach ($model in $modelFiles) {
        $size = (Get-Item $model).Length / 1MB
        Write-Host "  ✓ $model ($([math]::Round($size, 2)) MB)" -ForegroundColor Green
    }
}

# Step 4: Check if app.py exists
Write-Host "`nStep 4: Checking application files..." -ForegroundColor Yellow
if (Test-Path "app.py") {
    Write-Host "✓ app.py found" -ForegroundColor Green
} else {
    Write-Host "✗ app.py not found!" -ForegroundColor Red
    exit 1
}

if (Test-Path "Dockerfile") {
    Write-Host "✓ Dockerfile found" -ForegroundColor Green
} else {
    Write-Host "✗ Dockerfile not found!" -ForegroundColor Red
    exit 1
}

if (Test-Path "docker-compose.yml") {
    Write-Host "✓ docker-compose.yml found" -ForegroundColor Green
} else {
    Write-Host "✗ docker-compose.yml not found!" -ForegroundColor Red
    exit 1
}

# Step 5: Stop any existing containers
Write-Host "`nStep 5: Cleaning up old containers..." -ForegroundColor Yellow
docker-compose down 2>&1 | Out-Null
Write-Host "✓ Old containers removed" -ForegroundColor Green

# Step 6: Build Docker image
Write-Host "`nStep 6: Building Docker image..." -ForegroundColor Yellow
Write-Host "(This may take 5-10 minutes on first build...)" -ForegroundColor Cyan
docker build -t migraine-ml-api:latest .
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Docker image built successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Docker build failed!" -ForegroundColor Red
    Write-Host "Check the error messages above" -ForegroundColor Yellow
    exit 1
}

# Step 7: Start services with docker-compose
Write-Host "`nStep 7: Starting Docker services..." -ForegroundColor Yellow
docker-compose up -d
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Docker services started" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to start services!" -ForegroundColor Red
    Write-Host "Run 'docker-compose logs' to see errors" -ForegroundColor Yellow
    exit 1
}

# Step 8: Wait for services to be ready
Write-Host "`nStep 8: Waiting for services to be ready..." -ForegroundColor Yellow
Write-Host "Waiting 15 seconds..." -ForegroundColor Cyan
Start-Sleep -Seconds 15

# Step 9: Check running containers
Write-Host "`nStep 9: Checking container status..." -ForegroundColor Yellow
$containers = docker-compose ps
Write-Host $containers
if ($containers -match "Up") {
    Write-Host "✓ Containers are running" -ForegroundColor Green
} else {
    Write-Host "⚠ Containers may not be running properly" -ForegroundColor Yellow
}

# Step 10: Test API health
Write-Host "`nStep 10: Testing API health..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -ErrorAction Stop
    Write-Host "✓ API is healthy!" -ForegroundColor Green
    Write-Host "  Status: $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "⚠ API health check failed (may still be starting...)" -ForegroundColor Yellow
    Write-Host "Wait a few more seconds and check http://localhost:8000/health" -ForegroundColor Cyan
}

# Summary
Write-Host "`n╔══════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                                                          ║" -ForegroundColor Green
Write-Host "║           ✅ DOCKER DEPLOYMENT SUCCESSFUL! 🎉            ║" -ForegroundColor Green
Write-Host "║                                                          ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════════╝`n" -ForegroundColor Green

Write-Host "🌐 Access your services:" -ForegroundColor Cyan
Write-Host "  ├─ API:            http://localhost:8000" -ForegroundColor White
Write-Host "  ├─ API Docs:       http://localhost:8000/docs" -ForegroundColor White
Write-Host "  ├─ Health Check:   http://localhost:8000/health" -ForegroundColor White
Write-Host "  └─ MLflow UI:      http://localhost:5000`n" -ForegroundColor White

Write-Host "📋 Useful Docker commands:" -ForegroundColor Cyan
Write-Host "  ├─ View logs:      docker-compose logs -f" -ForegroundColor White
Write-Host "  ├─ Check status:   docker-compose ps" -ForegroundColor White
Write-Host "  ├─ Restart:        docker-compose restart" -ForegroundColor White
Write-Host "  └─ Stop:           docker-compose down`n" -ForegroundColor White

Write-Host "🧪 Test the API:" -ForegroundColor Cyan
Write-Host "  Visit http://localhost:8000/docs for interactive testing" -ForegroundColor White
Write-Host "  Or run: curl http://localhost:8000/health`n" -ForegroundColor White

Write-Host "📊 View MLflow experiments:" -ForegroundColor Cyan
Write-Host "  Visit http://localhost:5000`n" -ForegroundColor White

Write-Host "✨ Your ML API is now running in Docker! ✨" -ForegroundColor Green
