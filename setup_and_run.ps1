# Simple Setup and Run Script for Migraine ML Pipeline
# This script sets up the environment and runs the pipeline step by step

$ErrorActionPreference = "Continue"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "MIGRAINE ML PIPELINE - SETUP & RUN" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Step 1: Check Python
Write-Host "Step 1: Checking Python..." -ForegroundColor Yellow
$pythonCheck = Get-Command python -ErrorAction SilentlyContinue
if ($pythonCheck) {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python installed: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "✗ Python not found! Please install Python 3.9+" -ForegroundColor Red
    exit 1
}

# Step 2: Create virtual environment
Write-Host "`nStep 2: Setting up virtual environment..." -ForegroundColor Yellow
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Cyan
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✓ Virtual environment already exists" -ForegroundColor Green
}

# Step 3: Activate virtual environment
Write-Host "`nStep 3: Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1
Write-Host "✓ Virtual environment activated" -ForegroundColor Green

# Step 4: Install dependencies
Write-Host "`nStep 4: Installing dependencies..." -ForegroundColor Yellow
Write-Host "(This may take a few minutes...)" -ForegroundColor Cyan
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Dependencies installed successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Step 5: Check if dataset exists
Write-Host "`nStep 5: Checking dataset..." -ForegroundColor Yellow
if (Test-Path "data\raw\migraine_dataset.csv") {
    Write-Host "✓ Dataset found" -ForegroundColor Green
} else {
    Write-Host "✗ Dataset not found at data\raw\migraine_dataset.csv" -ForegroundColor Red
    Write-Host "Please ensure the dataset is in the correct location" -ForegroundColor Yellow
    exit 1
}

# Step 6: Run data validation
Write-Host "`nStep 6: Running data validation..." -ForegroundColor Yellow
python scripts\validate_data.py
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Data validation completed" -ForegroundColor Green
} else {
    Write-Host "✗ Data validation failed" -ForegroundColor Red
    exit 1
}

# Step 7: Run data preprocessing
Write-Host "`nStep 7: Running data preprocessing..." -ForegroundColor Yellow
python scripts\preprocess_data.py
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Data preprocessing completed" -ForegroundColor Green
} else {
    Write-Host "✗ Data preprocessing failed" -ForegroundColor Red
    exit 1
}

# Step 8: Run feature engineering
Write-Host "`nStep 8: Running feature engineering..." -ForegroundColor Yellow
python scripts\feature_engineering.py
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Feature engineering completed" -ForegroundColor Green
} else {
    Write-Host "✗ Feature engineering failed" -ForegroundColor Red
    exit 1
}

# Step 9: Train models
Write-Host "`nStep 9: Training models..." -ForegroundColor Yellow
Write-Host "(This will take 15-20 minutes...)" -ForegroundColor Cyan
python migraine_models_enhanced.py
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Model training completed" -ForegroundColor Green
} else {
    Write-Host "✗ Model training failed" -ForegroundColor Red
    exit 1
}

# Step 10: Evaluate models
Write-Host "`nStep 10: Evaluating models..." -ForegroundColor Yellow
python scripts\evaluate_models.py
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Model evaluation completed" -ForegroundColor Green
} else {
    Write-Host "✗ Model evaluation failed" -ForegroundColor Red
    exit 1
}

# Step 11: Run tests (optional)
Write-Host "`nStep 11: Running tests..." -ForegroundColor Yellow
pytest tests\ -v --tb=short
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ All tests passed" -ForegroundColor Green
} else {
    Write-Host "⚠ Some tests failed (continuing...)" -ForegroundColor Yellow
}

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "PIPELINE COMPLETED SUCCESSFULLY!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Check model files: ls *.pkl" -ForegroundColor White
Write-Host "2. View reports: explorer reports\evaluation" -ForegroundColor White
Write-Host "3. Start MLflow UI: mlflow ui" -ForegroundColor White
Write-Host "4. Start API: uvicorn app:app --reload`n" -ForegroundColor White
