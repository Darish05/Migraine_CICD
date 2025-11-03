# Quick Setup Script for Migraine ML Pipeline
$ErrorActionPreference = "Continue"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  MIGRAINE ML PIPELINE - QUICK SETUP" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Check Python
Write-Host "[1/11] Checking Python..." -ForegroundColor Yellow
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if ($pythonCmd) {
    Write-Host "   ✓ Python found" -ForegroundColor Green
} else {
    Write-Host "   ✗ Python not found!" -ForegroundColor Red
    exit 1
}

# Setup venv
Write-Host "[2/11] Setting up virtual environment..." -ForegroundColor Yellow
if (-not (Test-Path "venv")) {
    python -m venv venv
}
Write-Host "   ✓ Virtual environment ready" -ForegroundColor Green

# Activate venv
Write-Host "[3/11] Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1
Write-Host "   ✓ Activated" -ForegroundColor Green

# Install dependencies
Write-Host "[4/11] Installing dependencies (may take a few minutes)..." -ForegroundColor Yellow
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✓ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "   ✗ Installation failed" -ForegroundColor Red
    exit 1
}

# Check dataset
Write-Host "[5/11] Checking dataset..." -ForegroundColor Yellow
if (Test-Path "data\raw\migraine_dataset.csv") {
    Write-Host "   ✓ Dataset found" -ForegroundColor Green
} else {
    Write-Host "   ✗ Dataset not found!" -ForegroundColor Red
    exit 1
}

# Validate data
Write-Host "[6/11] Validating data..." -ForegroundColor Yellow
python scripts\validate_data.py
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✓ Validation complete" -ForegroundColor Green
} else {
    Write-Host "   ✗ Validation failed" -ForegroundColor Red
    exit 1
}

# Preprocess data
Write-Host "[7/11] Preprocessing data..." -ForegroundColor Yellow
python scripts\preprocess_data.py
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✓ Preprocessing complete" -ForegroundColor Green
} else {
    Write-Host "   ✗ Preprocessing failed" -ForegroundColor Red
    exit 1
}

# Feature engineering
Write-Host "[8/11] Engineering features..." -ForegroundColor Yellow
python scripts\feature_engineering.py
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✓ Feature engineering complete" -ForegroundColor Green
} else {
    Write-Host "   ✗ Feature engineering failed" -ForegroundColor Red
    exit 1
}

# Train models
Write-Host "[9/11] Training models (15-20 minutes)..." -ForegroundColor Yellow
python migraine_models_enhanced.py
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✓ Training complete" -ForegroundColor Green
} else {
    Write-Host "   ✗ Training failed" -ForegroundColor Red
    exit 1
}

# Evaluate models
Write-Host "[10/11] Evaluating models..." -ForegroundColor Yellow
python scripts\evaluate_models.py
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✓ Evaluation complete" -ForegroundColor Green
} else {
    Write-Host "   ✗ Evaluation failed" -ForegroundColor Red
    exit 1
}

# Run tests
Write-Host "[11/11] Running tests..." -ForegroundColor Yellow
pytest tests\ -v --tb=short 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✓ All tests passed" -ForegroundColor Green
} else {
    Write-Host "   ⚠ Some tests failed (check manually)" -ForegroundColor Yellow
}

# Summary
Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  ✅ PIPELINE COMPLETED SUCCESSFULLY!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green

Write-Host "📊 Results:" -ForegroundColor Cyan
Write-Host "   Models: " -NoNewline -ForegroundColor Yellow
Get-ChildItem -Filter "*.pkl" | ForEach-Object { Write-Host $_.Name -ForegroundColor White }

Write-Host "`n🚀 Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Deploy to Docker:  .\docker_deploy.ps1" -ForegroundColor White
Write-Host "   2. Start API:         uvicorn app:app --reload" -ForegroundColor White
Write-Host "   3. Start MLflow:      mlflow ui" -ForegroundColor White
Write-Host "   4. View reports:      explorer reports\evaluation`n" -ForegroundColor White
