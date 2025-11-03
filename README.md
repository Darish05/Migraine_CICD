# 🏥 Migraine Prediction MLOps Pipeline
## Complete Production-Grade ML System

![MLOps](https://img.shields.io/badge/MLOps-Production-green)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)
![Kubernetes](https://img.shields.io/badge/Kubernetes-Ready-blue)
![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-orange)

## 📋 Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Quick Start](#quick-start)
- [Pipeline Components](#pipeline-components)
- [Deployment](#deployment)
- [Monitoring](#monitoring)
- [MLSecOps](#mlsecops)

## 🎯 Overview

A complete MLOps pipeline for migraine prediction with automated data validation, continuous model training, drift detection, and production deployment on Kubernetes.

### Key Capabilities
- ✅ **Automated Data Pipeline** - Validation, versioning, and daily pattern analysis
- ✅ **Continuous Model Training** - 8 models with hyperparameter tuning
- ✅ **Experiment Tracking** - MLflow integration for all experiments
- ✅ **Model Evaluation** - Overfitting/underfitting detection
- ✅ **Drift Detection** - Data and model performance drift monitoring
- ✅ **CI/CD Pipeline** - Automated testing and deployment
- ✅ **Docker & Kubernetes** - Production-ready containerization
- ✅ **Monitoring & Alerts** - Prometheus metrics and alerting
- ✅ **MLSecOps** - Security scanning and input validation

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    DATA PIPELINE                              │
│  Raw Data → Validation → Preprocessing → Feature Engineering │
│      ↓           ↓             ↓                ↓             │
│    DVC      Reports      Scaling          Selection          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                 MODEL TRAINING (MLflow)                       │
│  8 Models: RF, XGBoost, LightGBM, GB, LR, SVM, KNN, AdaBoost│
│  → Hyperparameter Tuning → Cross-Validation → Best Model    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              EVALUATION & VALIDATION                          │
│  Metrics → Confusion Matrix → ROC Curve → Drift Detection   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   CI/CD PIPELINE                              │
│  Tests → Docker Build → Push Registry → Deploy K8s          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│            PRODUCTION DEPLOYMENT                              │
│  FastAPI → Docker → Kubernetes → Monitoring → Alerts        │
└─────────────────────────────────────────────────────────────┘
```

## ⚡ Features

### 1. Data Pipeline Automation
- **Validation**: Schema validation, data quality checks, anomaly detection
- **Preprocessing**: Missing value imputation, outlier handling, feature scaling
- **Feature Engineering**: Interaction features, polynomial features, health indices
- **Versioning**: DVC for data and model versioning

### 2. Model Training
```python
Models Implemented:
├── Classification (Migraine Occurrence)
│   ├── Random Forest
│   ├── XGBoost
│   ├── LightGBM
│   ├── Gradient Boosting
│   ├── Logistic Regression
│   ├── SVM
│   ├── KNN
│   └── AdaBoost
│
└── Regression (Migraine Severity)
    ├── Random Forest Regressor
    ├── XGBoost Regressor
    ├── LightGBM Regressor
    ├── Gradient Boosting Regressor
    ├── Ridge Regression
    ├── SVR
    ├── KNN Regressor
    └── AdaBoost Regressor
```

### 3. Evaluation Metrics
- **Classification**: Accuracy, Precision, Recall, F1-Score, ROC-AUC
- **Regression**: MSE, RMSE, MAE, R²
- **Overfitting Detection**: Automatic detection with recommendations
- **Confusion Matrix**: Visual representation
- **ROC Curves**: Performance visualization

### 4. Drift Detection
- **Feature Drift**: Population Stability Index (PSI)
- **Statistical Drift**: Kolmogorov-Smirnov test
- **Target Drift**: Distribution shift detection
- **Performance Drift**: Model degradation monitoring

### 5. Monitoring
- **Prometheus Metrics**: Real-time metrics collection
- **Alerts**: Automated alerting for drift and performance issues
- **Health Checks**: System health monitoring
- **Logging**: Comprehensive logging system

## 🚀 Quick Start

### Prerequisites
```bash
- Python 3.8+
- Docker Desktop
- Kubernetes (Docker Desktop or Minikube)
- Git
```

### Installation

1. **Clone Repository**
```bash
git clone https://github.com/Darish05/Migraine-Prediction.git
cd migraine-ml
```

2. **Create Virtual Environment**
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Initialize DVC**
```bash
dvc init
dvc remote add -d local_storage .dvc/cache
```

### Running the Pipeline

#### Phase 1: Data Pipeline
```bash
# Step 1: Validate data
python scripts/validate_data.py

# Step 2: Preprocess data
python scripts/preprocess_data.py

# Step 3: Feature engineering
python scripts/feature_engineering.py
```

#### Phase 2: Model Training
```bash
# Train all models with MLflow tracking
python migraine_models_enhanced.py

# View MLflow UI
mlflow ui
# Access at: http://localhost:5000
```

#### Phase 3: Evaluation
```bash
# Evaluate models
python scripts/evaluate_models.py

# Check for drift
python scripts/check_model_drift.py
```

#### Phase 4: Run with DVC
```bash
# Run entire pipeline
dvc repro

# View pipeline DAG
dvc dag
```

## 🐳 Docker Deployment

### Build and Run
```bash
# Build Docker image
docker build -t migraine-ml-api .

# Run with docker-compose
docker-compose up -d

# Access services
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- MLflow: http://localhost:5000
```

### Test API
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "age": 35,
    "gender": 1,
    "sleep_hours": 6,
    "stress_level": 8,
    "hydration": 4
  }'
```

## ☸️ Kubernetes Deployment

### Enable Kubernetes
```bash
# In Docker Desktop: Settings → Kubernetes → Enable Kubernetes
```

### Deploy to Kubernetes
```bash
# Apply configurations
kubectl apply -f kubernetes/

# Check deployment
kubectl get pods -n migraine-ml
kubectl get services -n migraine-ml

# Access application
kubectl port-forward svc/migraine-api 8000:8000 -n migraine-ml
```

### Scale Deployment
```bash
# Scale up
kubectl scale deployment migraine-api --replicas=5 -n migraine-ml

# Auto-scaling
kubectl autoscale deployment migraine-api \
  --min=2 --max=10 --cpu-percent=80 -n migraine-ml
```

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow
The pipeline automatically:
1. ✅ Runs unit tests
2. ✅ Validates data
3. ✅ Trains models
4. ✅ Builds Docker image
5. ✅ Pushes to registry
6. ✅ Deploys to Kubernetes
7. ✅ Runs integration tests

### Setup
```bash
# Configure GitHub Secrets
- DOCKER_USERNAME
- DOCKER_PASSWORD
- KUBECONFIG

# Push to trigger pipeline
git add .
git commit -m "Update pipeline"
git push origin main
```

## 📊 Monitoring

### Prometheus Metrics
```bash
# Start monitoring
python scripts/monitor_deployment.py

# Access metrics
http://localhost:9090/metrics
```

### Available Metrics
- `migraine_predictions_total` - Total predictions
- `migraine_prediction_latency_seconds` - Prediction latency
- `migraine_model_accuracy` - Current accuracy
- `migraine_data_drift_score` - Drift scores
- `migraine_performance_degradation` - Performance degradation

### Alerts
- **Drift Alert**: PSI > 0.2
- **Performance Alert**: Degradation > 10%
- **Latency Alert**: Response time > 1s

## 🔒 MLSecOps

### Security Features
- Input validation
- Rate limiting
- Authentication (optional)
- Model encryption (optional)
- Audit logging
- Security event monitoring

### Security Checks
```bash
# Run security scan
python scripts/security_scan.py

# View security logs
cat reports/security/security_*.jsonl
```

## 📁 Project Structure
```
migraine-ml/
├── .github/workflows/      # CI/CD pipelines
├── data/
│   ├── raw/               # Raw datasets
│   ├── processed/         # Processed data
│   └── features/          # Engineered features
├── scripts/               # Pipeline scripts
│   ├── validate_data.py
│   ├── preprocess_data.py
│   ├── feature_engineering.py
│   ├── evaluate_models.py
│   ├── check_model_drift.py
│   └── monitor_deployment.py
├── models/                # Trained models
├── reports/               # Evaluation reports
├── kubernetes/            # K8s manifests
├── tests/                 # Unit & integration tests
├── migraine_models_enhanced.py  # Main training script
├── app.py                 # FastAPI application
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose setup
├── dvc.yaml              # DVC pipeline
├── params.yaml           # Hyperparameters
└── requirements.txt      # Dependencies
```

## 📈 Results

### Model Performance
| Model | Accuracy | F1-Score | R² (Severity) |
|-------|----------|----------|---------------|
| XGBoost | 0.89 | 0.88 | 0.82 |
| LightGBM | 0.88 | 0.87 | 0.81 |
| Random Forest | 0.87 | 0.86 | 0.80 |

### Pipeline Metrics
- **Data Validation**: < 1 minute
- **Preprocessing**: ~ 2 minutes
- **Model Training**: ~ 15 minutes (8 models)
- **Deployment**: < 5 minutes

## 🛠️ Development

### Run Tests
```bash
# Unit tests
pytest tests/test_models.py -v

# Integration tests
pytest tests/test_api.py -v

# Coverage report
pytest --cov=. --cov-report=html
```

### Code Quality
```bash
# Linting
pylint scripts/ *.py

# Format code
black scripts/ *.py
```

## 📝 Configuration

### params.yaml
All hyperparameters and configurations are centralized in `params.yaml`:
- Data preprocessing settings
- Feature engineering parameters
- Model hyperparameters
- Evaluation thresholds
- Deployment configurations

## 🤝 Contributing
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License
This project is licensed under the MIT License.

## 👥 Authors
- **Darish** - [GitHub](https://github.com/Darish05)

## 🙏 Acknowledgments
- MLflow for experiment tracking
- Prometheus for monitoring
- FastAPI for API framework
- Kubernetes for orchestration

## 📞 Support
For issues and questions:
- GitHub Issues: [Report Issue](https://github.com/Darish05/Migraine-Prediction/issues)
- Email: support@migraineml.com

---
Made with ❤️ for Healthcare AI
