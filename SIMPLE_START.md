# 🚀 SIMPLE START GUIDE - NO DOCKER REQUIRED

## If Docker is not working, follow these steps:

### ⚡ Quick Start (Recommended)

**Run this ONE command:**

```powershell
.\setup_and_run.ps1
```

This will automatically:

- ✅ Check Python
- ✅ Create virtual environment
- ✅ Install all dependencies
- ✅ Validate data
- ✅ Preprocess data
- ✅ Engineer features
- ✅ Train 16 models
- ✅ Evaluate models
- ✅ Run tests

**Time**: 20-30 minutes

---

### 📝 Manual Steps (If script doesn't work)

#### 1. Setup Environment (5 minutes)

```powershell
# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

#### 2. Run Data Pipeline (5 minutes)

```powershell
# Validate data
python scripts\validate_data.py

# Preprocess data
python scripts\preprocess_data.py

# Engineer features
python scripts\feature_engineering.py
```

#### 3. Train Models (15-20 minutes)

```powershell
# Train all 16 models
python migraine_models_enhanced.py
```

#### 4. Evaluate Models (3 minutes)

```powershell
# Evaluate and generate reports
python scripts\evaluate_models.py
```

#### 5. Run Tests (Optional, 2 minutes)

```powershell
# Run all tests
pytest tests\ -v
```

---

### 🎯 Start the API (Without Docker)

#### Option A: Simple Start

```powershell
# Start the API server
uvicorn app:app --reload
```

Then visit:

- API: http://localhost:8000
- Docs: http://localhost:8000/docs

#### Option B: With MLflow

```powershell
# Terminal 1: Start MLflow
mlflow ui

# Terminal 2: Start API
uvicorn app:app --reload
```

Then visit:

- API: http://localhost:8000
- MLflow: http://localhost:5000

---

### ✅ Verify Everything Works

```powershell
# Check if models were created
ls *.pkl

# Check if data was processed
ls data\processed\

# Check if reports were generated
ls reports\evaluation\

# Test the API
curl http://localhost:8000/health
```

---

### 🐛 Troubleshooting

#### Problem: "Python not found"

**Solution:**

```powershell
# Check if Python is installed
python --version

# If not, download from: https://www.python.org/downloads/
```

#### Problem: "Module not found"

**Solution:**

```powershell
# Make sure virtual environment is activated
.\venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt
```

#### Problem: "Dataset not found"

**Solution:**

```powershell
# Check if file exists
Test-Path data\raw\migraine_dataset.csv

# If False, ensure the CSV file is in data/raw/ folder
```

#### Problem: "Script execution disabled"

**Solution:**

```powershell
# Run as Administrator, then:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then try again
.\setup_and_run.ps1
```

---

### 📊 Expected Results

After running successfully, you should see:

```
migraine-ml/
├── classification_model_top1.pkl     ← Best classification model
├── classification_model_top2.pkl     ← 2nd best classification model
├── regression_model_top1.pkl         ← Best regression model
├── regression_model_top2.pkl         ← 2nd best regression model
├── models_info.json                  ← Model metadata
│
├── data/
│   ├── processed/
│   │   ├── classification_data.csv   ← Processed data
│   │   └── regression_data.csv
│   └── features/
│       └── engineered_features.csv   ← Features
│
└── reports/
    ├── validation/
    │   ├── validation_*.json         ← Validation reports
    │   └── validation_*.html
    └── evaluation/
        ├── model_evaluation_report.html  ← Main report
        ├── confusion_matrix_*.png
        └── roc_curve_*.png
```

---

### 🎉 Success Indicators

You'll know it worked when:

1. ✅ No error messages in terminal
2. ✅ `.pkl` files created in root folder
3. ✅ `reports/evaluation/model_evaluation_report.html` exists
4. ✅ `python -c "import pickle; print(pickle.load(open('classification_model_top1.pkl', 'rb')))"` shows model info
5. ✅ API starts without errors

---

### 🚀 Test the API

```powershell
# Make a test prediction
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

Invoke-RestMethod -Uri "http://localhost:8000/predict" -Method Post -Headers @{"Content-Type"="application/json"} -Body $body
```

---

## 💡 Pro Tips

1. **First time?** Just run `.\setup_and_run.ps1`
2. **Retraining?** Just run `python migraine_models_enhanced.py`
3. **Testing API?** Use http://localhost:8000/docs for interactive testing
4. **View results?** Open `reports\evaluation\model_evaluation_report.html` in browser

---

## ⏱️ Time Estimates

- Setup: 5 minutes
- Data Pipeline: 5 minutes
- Model Training: 15-20 minutes
- Evaluation: 3 minutes
- **Total: ~30 minutes**

---

## 🎯 Bottom Line

**Forget Docker for now. Just run:**

```powershell
.\setup_and_run.ps1
```

**Wait 30 minutes. Done! 🎉**
