# 🚀 Quick Start Guide - Migraine ML Pipeline

## Complete Step-by-Step Execution Guide

### Prerequisites Checklist
- [ ] Python 3.9+ installed
- [ ] Docker Desktop installed and running
- [ ] Git installed
- [ ] 8GB+ RAM available
- [ ] 10GB+ disk space

---

## 📋 Phase-by-Phase Execution

### **PHASE 1: Setup Environment** (5 minutes)

```powershell
# 1. Navigate to project
cd D:\Mlops\migraine-ml

# 2. Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Verify installation
python -c "import pandas, numpy, sklearn, mlflow; print('✅ All packages installed!')"
```

---

### **PHASE 2: Data Pipeline** (10 minutes)

```powershell
# Step 1: Validate data
Write-Host "`n=== DATA VALIDATION ===" -ForegroundColor Cyan
python scripts\validate_data.py

# Expected output: ✅ ALL VALIDATIONS PASSED
# Reports saved in: reports/validation/

# Step 2: Preprocess data
Write-Host "`n=== DATA PREPROCESSING ===" -ForegroundColor Cyan
python scripts\preprocess_data.py

# Expected output: ✅ Preprocessing Pipeline Completed!
# Data saved in: data/processed/

# Step 3: Feature engineering
Write-Host "`n=== FEATURE ENGINEERING ===" -ForegroundColor Cyan
python scripts\feature_engineering.py

# Expected output: ✅ Feature Engineering Pipeline Completed!
# Features saved in: data/features/
```

**Expected Results:**
- ✅ `reports/validation/validation_*.json` created
- ✅ `data/processed/classification_data.csv` created
- ✅ `data/features/engineered_features.csv` created
- ✅ `models/preprocessors/scaler.pkl` saved

---

### **PHASE 3: Model Training** (15-20 minutes)

```powershell
# Train all 8 models with MLflow tracking
Write-Host "`n=== MODEL TRAINING ===" -ForegroundColor Cyan
python migraine_models_enhanced.py

# This will:
# - Train 8 classification models
# - Train 8 regression models
# - Log everything to MLflow
# - Save best models
```

**Monitor Training:**
```powershell
# In a separate terminal:
mlflow ui

# Access at: http://localhost:5000
```

**Expected Results:**
- ✅ `classification_model_top1.pkl` created
- ✅ `classification_model_top2.pkl` created
- ✅ `regression_model_top1.pkl` created
- ✅ `regression_model_top2.pkl` created
- ✅ `models_info.json` with performance metrics
- ✅ MLflow experiments logged

---

### **PHASE 4: Model Evaluation** (5 minutes)

```powershell
# Evaluate models
Write-Host "`n=== MODEL EVALUATION ===" -ForegroundColor Cyan
python scripts\evaluate_models.py

# Check for drift
Write-Host "`n=== DRIFT DETECTION ===" -ForegroundColor Cyan
python scripts\check_model_drift.py
```

**Expected Results:**
- ✅ `reports/evaluation/model_evaluation_report.html`
- ✅ Confusion matrices saved as images
- ✅ ROC curves generated
- ✅ Drift detection report created

---

### **PHASE 5: Run Tests** (2 minutes)

```powershell
# Run all tests
Write-Host "`n=== RUNNING TESTS ===" -ForegroundColor Cyan
pytest tests/ -v --tb=short

# With coverage
pytest tests/ -v --cov=. --cov-report=html
```

**Expected Results:**
- ✅ All tests pass
- ✅ Coverage report in `htmlcov/index.html`

---

### **PHASE 6: Docker Deployment** (10 minutes)

**Prerequisites:** Ensure Docker Desktop is running!

```powershell
# Verify Docker is running
docker --version
docker ps

# Build Docker image
Write-Host "`n=== BUILDING DOCKER IMAGE ===" -ForegroundColor Cyan
docker build -t migraine-ml-api:latest .

# Start services with docker-compose
Write-Host "`n=== STARTING SERVICES ===" -ForegroundColor Cyan
docker-compose up -d

# Check running containers
docker-compose ps
```

**Access Services:**
- 🌐 API: http://localhost:8000
- 📚 API Docs: http://localhost:8000/docs
- 📊 MLflow UI: http://localhost:5000

**Test the API:**
```powershell
# Test health endpoint
curl http://localhost:8000/health

# Test prediction (PowerShell)
$headers = @{"Content-Type"="application/json"}
$body = @{
    age = 35
    gender = 1
    sleep_hours = 7.0
    stress_level = 7
    hydration = 6
    exercise = 3
    screen_time = 8.0
    caffeine_intake = 3
    alcohol_intake = 1
    weather_changes = 1
    menstrual_cycle = 1
    dehydration = 0
    bright_light = 1
    loud_noises = 0
    strong_smells = 1
    missed_meals = 1
    specific_foods = 0
    physical_activity = 1
    neck_pain = 1
    weather_pressure = 1013.25
    humidity = 65.0
    temperature_change = 5.0
    sleep_quality = 6
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/predict" -Method Post -Headers $headers -Body $body
```

---

### **PHASE 7: Kubernetes Deployment** (15 minutes)

**Prerequisites:** Enable Kubernetes in Docker Desktop
- Open Docker Desktop → Settings → Kubernetes → Enable Kubernetes

```powershell
# Verify Kubernetes is running
kubectl version --client
kubectl cluster-info

# Create namespace and deploy
Write-Host "`n=== DEPLOYING TO KUBERNETES ===" -ForegroundColor Cyan
kubectl apply -f kubernetes/deployment.yaml

# Wait for deployment
kubectl wait --for=condition=ready pod -l app=migraine-api -n migraine-ml --timeout=300s

# Check deployment status
kubectl get all -n migraine-ml

# Get service URL
kubectl get svc migraine-api-service -n migraine-ml

# Port forward to access locally
kubectl port-forward svc/migraine-api-service 8000:8000 -n migraine-ml
```

**Scale the deployment:**
```powershell
# Scale to 5 replicas
kubectl scale deployment migraine-api --replicas=5 -n migraine-ml

# Check scaling
kubectl get pods -n migraine-ml -w
```

---

### **PHASE 8: Monitoring** (5 minutes)

```powershell
# Start monitoring server (separate terminal)
Write-Host "`n=== STARTING MONITORING ===" -ForegroundColor Cyan
python scripts\monitor_deployment.py

# Access metrics at: http://localhost:9090/metrics
```

**View Prometheus Metrics:**
```powershell
# In browser, visit:
# http://localhost:9090/metrics
```

---

## 🎯 Complete Pipeline with DVC

```powershell
# Initialize DVC (one-time)
dvc init
dvc remote add -d local .dvc/cache

# Track data
dvc add data/raw/migraine_dataset.csv

# Run complete pipeline
dvc repro

# View pipeline DAG
dvc dag
```

---

## 📊 Verification Checklist

After completing all phases, verify:

```powershell
# 1. Check files created
ls *.pkl  # Should show 4-6 model files
ls data/processed/*.csv  # Processed data
ls reports/evaluation/*.png  # Plots

# 2. Verify Docker containers
docker-compose ps  # Should show 2 running services

# 3. Verify Kubernetes pods
kubectl get pods -n migraine-ml  # Should show 3 running pods

# 4. Test API endpoints
curl http://localhost:8000/health
curl http://localhost:8000/docs

# 5. Check MLflow
# Visit: http://localhost:5000
```

---

## 🚨 Troubleshooting

### Issue: Docker not starting
```powershell
# Solution: Start Docker Desktop
# Check status
docker info
```

### Issue: Port already in use
```powershell
# Solution: Stop conflicting services
docker-compose down
# Or change port in docker-compose.yml
```

### Issue: Models not training
```powershell
# Solution: Check data exists
ls data/raw/migraine_dataset.csv

# Re-run preprocessing
python scripts/preprocess_data.py
```

### Issue: Kubernetes pods not starting
```powershell
# Check pod logs
kubectl logs -l app=migraine-api -n migraine-ml

# Check events
kubectl get events -n migraine-ml --sort-by='.lastTimestamp'

# Delete and recreate
kubectl delete namespace migraine-ml
kubectl apply -f kubernetes/deployment.yaml
```

---

## 📈 Performance Benchmarks

Expected execution times:
- Data Validation: < 1 minute
- Data Preprocessing: ~ 2 minutes
- Feature Engineering: ~ 2 minutes
- Model Training: 15-20 minutes (8 models)
- Model Evaluation: ~ 3 minutes
- Docker Build: 5-10 minutes
- Kubernetes Deploy: 2-5 minutes

**Total: ~30-45 minutes** for complete pipeline

---

## 🎓 Next Steps

1. **Customize Models**: Edit `params.yaml` to tune hyperparameters
2. **Add Data**: Place new data in `data/raw/`
3. **Retrain**: Run `python migraine_models_enhanced.py`
4. **Deploy**: Push to GitHub → CI/CD triggers automatically
5. **Monitor**: Check drift and performance metrics

---

## 📞 Support

If you encounter issues:
1. Check logs: `docker-compose logs`
2. Check Kubernetes logs: `kubectl logs -l app=migraine-api -n migraine-ml`
3. Review error messages in terminal
4. Check GitHub Issues: https://github.com/Darish05/Migraine-Prediction/issues

---

## ✅ Success Indicators

You're ready for production when you see:
- ✅ All tests passing
- ✅ Models trained with >85% accuracy
- ✅ Docker containers running
- ✅ Kubernetes pods in Ready state
- ✅ API responding to requests
- ✅ Monitoring metrics available

---

**Happy ML Engineering! 🚀**
