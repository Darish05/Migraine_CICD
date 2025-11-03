# Cleanup Script - Reset the environment
param(
    [switch]$All,
    [switch]$Models,
    [switch]$Data,
    [switch]$Docker,
    [switch]$Kubernetes,
    [switch]$Reports
)

$ErrorActionPreference = "Stop"

function Write-Success { param($msg) Write-Host "✅ $msg" -ForegroundColor Green }
function Write-Info { param($msg) Write-Host "ℹ️  $msg" -ForegroundColor Cyan }
function Write-Warning { param($msg) Write-Host "⚠️  $msg" -ForegroundColor Yellow }

Write-Host @"

╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           🧹 MIGRAINE ML PIPELINE - CLEANUP SCRIPT           ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Yellow

if (-not ($All -or $Models -or $Data -or $Docker -or $Kubernetes -or $Reports)) {
    Write-Warning "No cleanup options specified!"
    Write-Host @"

Usage:
  .\cleanup.ps1 -All           # Clean everything
  .\cleanup.ps1 -Models        # Remove trained models
  .\cleanup.ps1 -Data          # Remove processed data
  .\cleanup.ps1 -Docker        # Stop and remove Docker containers
  .\cleanup.ps1 -Kubernetes    # Remove Kubernetes deployment
  .\cleanup.ps1 -Reports       # Remove generated reports

Examples:
  .\cleanup.ps1 -Models -Reports    # Clean models and reports
  .\cleanup.ps1 -All                # Complete cleanup

"@
    exit 0
}

# Confirm action
if ($All) {
    Write-Warning "This will DELETE all generated files, Docker containers, and Kubernetes deployments!"
    $confirm = Read-Host "Are you sure? (yes/no)"
    if ($confirm -ne "yes") {
        Write-Info "Cleanup cancelled"
        exit 0
    }
}

# ============================================================
# CLEANUP MODELS
# ============================================================
if ($All -or $Models) {
    Write-Info "Cleaning models..."
    
    # Remove model files
    if (Test-Path "*.pkl") {
        Remove-Item "*.pkl" -Force
        Write-Success "Removed .pkl model files"
    }
    
    # Remove model metadata
    if (Test-Path "models\metadata") {
        Remove-Item "models\metadata\*" -Recurse -Force -ErrorAction SilentlyContinue
        Write-Success "Removed model metadata"
    }
    
    # Remove preprocessors
    if (Test-Path "models\preprocessors") {
        Remove-Item "models\preprocessors\*" -Recurse -Force -ErrorAction SilentlyContinue
        Write-Success "Removed preprocessors"
    }
    
    # Remove models_info.json
    if (Test-Path "models_info.json") {
        Remove-Item "models_info.json" -Force
        Write-Success "Removed models_info.json"
    }
}

# ============================================================
# CLEANUP DATA
# ============================================================
if ($All -or $Data) {
    Write-Info "Cleaning processed data..."
    
    # Remove processed data (keep raw data!)
    if (Test-Path "data\processed") {
        Remove-Item "data\processed\*" -Recurse -Force -ErrorAction SilentlyContinue
        Write-Success "Removed processed data"
    }
    
    # Remove feature data
    if (Test-Path "data\features") {
        Remove-Item "data\features\*" -Recurse -Force -ErrorAction SilentlyContinue
        Write-Success "Removed feature data"
    }
    
    # Remove DVC cache
    if (Test-Path ".dvc\cache") {
        Remove-Item ".dvc\cache\*" -Recurse -Force -ErrorAction SilentlyContinue
        Write-Success "Removed DVC cache"
    }
}

# ============================================================
# CLEANUP REPORTS
# ============================================================
if ($All -or $Reports) {
    Write-Info "Cleaning reports..."
    
    # Remove validation reports
    if (Test-Path "reports\validation") {
        Remove-Item "reports\validation\*" -Recurse -Force -ErrorAction SilentlyContinue
        Write-Success "Removed validation reports"
    }
    
    # Remove evaluation reports
    if (Test-Path "reports\evaluation") {
        Remove-Item "reports\evaluation\*" -Recurse -Force -ErrorAction SilentlyContinue
        Write-Success "Removed evaluation reports"
    }
    
    # Remove drift reports
    if (Test-Path "reports\drift") {
        Remove-Item "reports\drift\*" -Recurse -Force -ErrorAction SilentlyContinue
        Write-Success "Removed drift reports"
    }
    
    # Remove coverage reports
    if (Test-Path "htmlcov") {
        Remove-Item "htmlcov" -Recurse -Force -ErrorAction SilentlyContinue
        Write-Success "Removed coverage reports"
    }
    
    if (Test-Path ".coverage") {
        Remove-Item ".coverage" -Force -ErrorAction SilentlyContinue
    }
    
    # Remove pytest cache
    if (Test-Path ".pytest_cache") {
        Remove-Item ".pytest_cache" -Recurse -Force -ErrorAction SilentlyContinue
        Write-Success "Removed pytest cache"
    }
}

# ============================================================
# CLEANUP DOCKER
# ============================================================
if ($All -or $Docker) {
    Write-Info "Cleaning Docker..."
    
    try {
        docker info | Out-Null
        
        # Stop containers
        Write-Info "Stopping Docker containers..."
        docker-compose down -v 2>$null
        Write-Success "Docker containers stopped and removed"
        
        # Remove images
        $images = docker images -q migraine-ml-api
        if ($images) {
            docker rmi $images -f 2>$null
            Write-Success "Removed Docker images"
        }
        
        # Prune volumes
        docker volume prune -f 2>$null
        Write-Success "Pruned Docker volumes"
        
    } catch {
        Write-Warning "Docker not running or not installed"
    }
}

# ============================================================
# CLEANUP KUBERNETES
# ============================================================
if ($All -or $Kubernetes) {
    Write-Info "Cleaning Kubernetes deployment..."
    
    try {
        kubectl version --client | Out-Null
        
        # Delete namespace (this removes everything)
        kubectl delete namespace migraine-ml --ignore-not-found=true 2>$null
        Write-Success "Kubernetes deployment removed"
        
    } catch {
        Write-Warning "Kubernetes not available"
    }
}

# ============================================================
# CLEANUP MLFLOW
# ============================================================
if ($All) {
    Write-Info "Cleaning MLflow artifacts..."
    
    if (Test-Path "mlruns") {
        Remove-Item "mlruns" -Recurse -Force -ErrorAction SilentlyContinue
        Write-Success "Removed MLflow runs"
    }
    
    if (Test-Path "mlartifacts") {
        Remove-Item "mlartifacts" -Recurse -Force -ErrorAction SilentlyContinue
        Write-Success "Removed MLflow artifacts"
    }
}

# ============================================================
# CLEANUP PYTHON CACHE
# ============================================================
if ($All) {
    Write-Info "Cleaning Python cache..."
    
    Get-ChildItem -Path . -Filter "__pycache__" -Recurse -Directory | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    Get-ChildItem -Path . -Filter "*.pyc" -Recurse -File | Remove-Item -Force -ErrorAction SilentlyContinue
    Write-Success "Removed Python cache files"
}

Write-Host @"

╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║                 ✅ CLEANUP COMPLETED! 🎉                      ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Green

Write-Host "`n📋 What was cleaned:" -ForegroundColor Yellow
if ($All -or $Models) { Write-Host "  ✅ Trained models and metadata" }
if ($All -or $Data) { Write-Host "  ✅ Processed and feature data" }
if ($All -or $Reports) { Write-Host "  ✅ Generated reports" }
if ($All -or $Docker) { Write-Host "  ✅ Docker containers and images" }
if ($All -or $Kubernetes) { Write-Host "  ✅ Kubernetes deployments" }
if ($All) { 
    Write-Host "  ✅ MLflow artifacts"
    Write-Host "  ✅ Python cache files"
}

Write-Host "`n🚀 To rebuild:" -ForegroundColor Yellow
Write-Host "  .\run_pipeline.ps1"

Write-Host "`n✨ Cleanup completed successfully!" -ForegroundColor Green
