# Migraine ML Pipeline - Automated Execution Script
# This script runs the complete MLOps pipeline end-to-end

param(
    [switch]$SkipTests,
    [switch]$SkipDocker,
    [switch]$SkipKubernetes,
    [switch]$QuickMode
)

$ErrorActionPreference = "Stop"

# Color functions
function Write-Success { param($msg) Write-Host "✅ $msg" -ForegroundColor Green }
function Write-Info { param($msg) Write-Host "ℹ️  $msg" -ForegroundColor Cyan }
function Write-Warning { param($msg) Write-Host "⚠️  $msg" -ForegroundColor Yellow }
function Write-Error { param($msg) Write-Host "❌ $msg" -ForegroundColor Red }
function Write-Step { param($msg) Write-Host "`n🔹 $msg" -ForegroundColor Blue -BackgroundColor Black }

$startTime = Get-Date
Write-Host @"

╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        🧠 MIGRAINE ML PIPELINE - AUTOMATED EXECUTION 🚀       ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Magenta

# Check prerequisites
Write-Step "PHASE 0: Checking Prerequisites"

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Success "Python installed: $pythonVersion"
} catch {
    Write-Error "Python not found! Please install Python 3.9+"
    exit 1
}

# Check virtual environment
if (-not (Test-Path "venv\Scripts\activate.ps1")) {
    Write-Warning "Virtual environment not found. Creating..."
    python -m venv venv
    Write-Success "Virtual environment created"
}

# Activate virtual environment
Write-Info "Activating virtual environment..."
& .\venv\Scripts\Activate.ps1

# Install/upgrade dependencies
Write-Info "Installing dependencies..."
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
Write-Success "All dependencies installed"

# Check data file
if (-not (Test-Path "data\raw\migraine_dataset.csv")) {
    Write-Error "Dataset not found at data\raw\migraine_dataset.csv"
    Write-Info "Please ensure the dataset is in the correct location"
    exit 1
}
Write-Success "Dataset found"

# ============================================================
# PHASE 1: DATA VALIDATION
# ============================================================
Write-Step "PHASE 1: Data Validation"

try {
    python scripts\validate_data.py
    Write-Success "Data validation completed"
    
    # Check validation report
    $validationFiles = Get-ChildItem "reports\validation\" -Filter "validation_*.json" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($validationFiles) {
        $validation = Get-Content $validationFiles.FullName | ConvertFrom-Json
        Write-Info "Validation Status: $($validation.validation_status)"
        Write-Info "Issues Found: $($validation.issues_found)"
    }
} catch {
    Write-Error "Data validation failed: $_"
    exit 1
}

# ============================================================
# PHASE 2: DATA PREPROCESSING
# ============================================================
Write-Step "PHASE 2: Data Preprocessing"

try {
    python scripts\preprocess_data.py
    Write-Success "Data preprocessing completed"
    
    # Check processed files
    if (Test-Path "data\processed\classification_data.csv") {
        $lineCount = (Get-Content "data\processed\classification_data.csv" | Measure-Object -Line).Lines
        Write-Info "Processed data: $lineCount rows"
    }
} catch {
    Write-Error "Data preprocessing failed: $_"
    exit 1
}

# ============================================================
# PHASE 3: FEATURE ENGINEERING
# ============================================================
Write-Step "PHASE 3: Feature Engineering"

try {
    python scripts\feature_engineering.py
    Write-Success "Feature engineering completed"
    
    # Check feature metadata
    if (Test-Path "models\metadata\feature_metadata.json") {
        $metadata = Get-Content "models\metadata\feature_metadata.json" | ConvertFrom-Json
        Write-Info "Total features: $($metadata.n_features)"
        Write-Info "Selected features: $($metadata.selected_features.Count)"
    }
} catch {
    Write-Error "Feature engineering failed: $_"
    exit 1
}

# ============================================================
# PHASE 4: MODEL TRAINING
# ============================================================
Write-Step "PHASE 4: Model Training (This may take 15-20 minutes)"

try {
    # Start MLflow UI in background
    Write-Info "Starting MLflow UI..."
    $mlflowJob = Start-Job -ScriptBlock { mlflow ui --port 5000 }
    Start-Sleep -Seconds 3
    Write-Success "MLflow UI available at: http://localhost:5000"
    
    # Train models
    python migraine_models_enhanced.py
    Write-Success "Model training completed"
    
    # Check model files
    $models = Get-ChildItem -Filter "*.pkl" | Where-Object { $_.Name -like "*model*" }
    Write-Info "Models created: $($models.Count)"
    foreach ($model in $models) {
        Write-Info "  - $($model.Name) ($([math]::Round($model.Length/1MB, 2)) MB)"
    }
} catch {
    Write-Error "Model training failed: $_"
    exit 1
}

# ============================================================
# PHASE 5: MODEL EVALUATION
# ============================================================
Write-Step "PHASE 5: Model Evaluation"

try {
    python scripts\evaluate_models.py
    Write-Success "Model evaluation completed"
    
    # Check evaluation reports
    if (Test-Path "reports\evaluation\model_evaluation_report.html") {
        Write-Info "Evaluation report: reports\evaluation\model_evaluation_report.html"
    }
} catch {
    Write-Error "Model evaluation failed: $_"
    exit 1
}

# ============================================================
# PHASE 6: DRIFT DETECTION
# ============================================================
Write-Step "PHASE 6: Drift Detection"

try {
    python scripts\check_model_drift.py
    Write-Success "Drift detection completed"
} catch {
    Write-Warning "Drift detection failed (this is normal for first run): $_"
}

# ============================================================
# PHASE 7: TESTING
# ============================================================
if (-not $SkipTests) {
    Write-Step "PHASE 7: Running Tests"
    
    try {
        Write-Info "Running unit tests..."
        pytest tests\ -v --tb=short --color=yes
        Write-Success "All tests passed"
        
        # Generate coverage report
        if (-not $QuickMode) {
            Write-Info "Generating coverage report..."
            pytest tests\ --cov=. --cov-report=html --cov-report=term --quiet
            Write-Success "Coverage report: htmlcov\index.html"
        }
    } catch {
        Write-Warning "Some tests failed: $_"
    }
} else {
    Write-Warning "Skipping tests (--SkipTests flag)"
}

# ============================================================
# PHASE 8: DOCKER DEPLOYMENT
# ============================================================
if (-not $SkipDocker) {
    Write-Step "PHASE 8: Docker Deployment"
    
    # Check if Docker is running
    try {
        docker info | Out-Null
        Write-Success "Docker is running"
        
        # Build image
        Write-Info "Building Docker image..."
        docker build -t migraine-ml-api:latest . --quiet
        Write-Success "Docker image built"
        
        # Start services
        Write-Info "Starting Docker services..."
        docker-compose up -d
        Write-Success "Docker services started"
        
        # Wait for services to be ready
        Write-Info "Waiting for services to be ready..."
        Start-Sleep -Seconds 10
        
        # Test API
        try {
            $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
            Write-Success "API is healthy: $($health.status)"
            Write-Info "API Documentation: http://localhost:8000/docs"
            Write-Info "MLflow UI: http://localhost:5000"
        } catch {
            Write-Warning "API health check failed (may still be starting)"
        }
    } catch {
        Write-Warning "Docker is not running. Skipping Docker deployment."
        Write-Info "Start Docker Desktop and run: docker-compose up -d"
    }
} else {
    Write-Warning "Skipping Docker deployment (--SkipDocker flag)"
}

# ============================================================
# PHASE 9: KUBERNETES DEPLOYMENT
# ============================================================
if (-not $SkipKubernetes) {
    Write-Step "PHASE 9: Kubernetes Deployment"
    
    # Check if Kubernetes is available
    try {
        kubectl version --client | Out-Null
        Write-Success "Kubernetes CLI available"
        
        # Check if cluster is running
        try {
            kubectl cluster-info | Out-Null
            Write-Success "Kubernetes cluster is running"
            
            # Deploy to Kubernetes
            Write-Info "Deploying to Kubernetes..."
            kubectl apply -f kubernetes\deployment.yaml
            
            # Wait for deployment
            Write-Info "Waiting for pods to be ready..."
            kubectl wait --for=condition=ready pod -l app=migraine-api -n migraine-ml --timeout=300s
            
            Write-Success "Kubernetes deployment completed"
            
            # Show deployment status
            Write-Info "`nDeployment Status:"
            kubectl get all -n migraine-ml
            
            Write-Info "`nTo access the API, run:"
            Write-Info "kubectl port-forward svc/migraine-api-service 8000:8000 -n migraine-ml"
        } catch {
            Write-Warning "Kubernetes cluster not available. Enable Kubernetes in Docker Desktop."
        }
    } catch {
        Write-Warning "Kubernetes CLI not found. Skipping Kubernetes deployment."
    }
} else {
    Write-Warning "Skipping Kubernetes deployment (--SkipKubernetes flag)"
}

# ============================================================
# FINAL SUMMARY
# ============================================================
$endTime = Get-Date
$duration = $endTime - $startTime

Write-Host @"

╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║                  ✅ PIPELINE COMPLETED! 🎉                    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Green

Write-Host "⏱️  Total Execution Time: $($duration.ToString('hh\:mm\:ss'))" -ForegroundColor Cyan

Write-Host "`n📊 Summary:" -ForegroundColor Yellow
Write-Host "  ✅ Data validated and preprocessed"
Write-Host "  ✅ Features engineered"
Write-Host "  ✅ Models trained and evaluated"
Write-Host "  ✅ Tests executed"
if (-not $SkipDocker) { Write-Host "  ✅ Docker services running" }
if (-not $SkipKubernetes) { Write-Host "  ✅ Kubernetes deployment ready" }

Write-Host "`n🔗 Quick Links:" -ForegroundColor Yellow
Write-Host "  📚 API Documentation:    http://localhost:8000/docs"
Write-Host "  📊 MLflow UI:            http://localhost:5000"
Write-Host "  📈 Prometheus Metrics:   http://localhost:9090/metrics"
Write-Host "  📑 Evaluation Report:    reports\evaluation\model_evaluation_report.html"
Write-Host "  📈 Coverage Report:      htmlcov\index.html"

Write-Host "`n📋 Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Review model performance in MLflow UI"
Write-Host "  2. Test API endpoints at http://localhost:8000/docs"
Write-Host "  3. Check evaluation reports in reports\ folder"
Write-Host "  4. Monitor application with Prometheus metrics"
Write-Host "  5. Deploy to production Kubernetes cluster"

Write-Host "`n🚀 To redeploy:" -ForegroundColor Yellow
Write-Host "  .\run_pipeline.ps1                    # Full pipeline"
Write-Host "  .\run_pipeline.ps1 -SkipTests         # Skip tests"
Write-Host "  .\run_pipeline.ps1 -QuickMode         # Skip coverage"
Write-Host "  .\run_pipeline.ps1 -SkipDocker        # Skip Docker"

Write-Host "`n✨ Pipeline execution completed successfully!" -ForegroundColor Green
