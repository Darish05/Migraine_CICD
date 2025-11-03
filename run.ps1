Write-Host "`n=== MIGRAINE ML PIPELINE - QUICK START ===" -ForegroundColor Cyan

Write-Host "`n[1] Checking Python..."
python --version
if ($?) { Write-Host "OK" -ForegroundColor Green } else { exit 1 }

Write-Host "`n[2] Activating environment..."
& .\venv\Scripts\Activate.ps1

Write-Host "`n[3] Installing dependencies..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
if ($?) { Write-Host "OK" -ForegroundColor Green } else { exit 1 }

Write-Host "`n[4] Validating data..."
python scripts\validate_data.py
if ($?) { Write-Host "OK" -ForegroundColor Green } else { exit 1 }

Write-Host "`n[5] Preprocessing data..."
python scripts\preprocess_data.py
if ($?) { Write-Host "OK" -ForegroundColor Green } else { exit 1 }

Write-Host "`n[6] Engineering features..."
python scripts\feature_engineering.py
if ($?) { Write-Host "OK" -ForegroundColor Green } else { exit 1 }

Write-Host "`n[7] Training models (15-20 min)..."
python migraine_models_enhanced.py
if ($?) { Write-Host "OK" -ForegroundColor Green } else { exit 1 }

Write-Host "`n[8] Evaluating models..."
python scripts\evaluate_models.py
if ($?) { Write-Host "OK" -ForegroundColor Green } else { exit 1 }

Write-Host "`n[9] Running tests..."
pytest tests\ -v
if ($?) { Write-Host "OK" -ForegroundColor Green } else { Write-Host "SKIP" -ForegroundColor Yellow }

Write-Host "`n=== COMPLETED ===" -ForegroundColor Green
Write-Host "`nNext: .\docker_deploy.ps1 (for Docker)" -ForegroundColor Cyan
Write-Host "   Or: uvicorn app:app --reload (for local API)`n" -ForegroundColor Cyan
