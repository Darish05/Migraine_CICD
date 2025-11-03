# MLOps Pipeline Workflow Diagrams

This document contains visual representations of the complete MLOps pipeline workflow.

## Table of Contents

1. [Complete Pipeline Flow](#complete-pipeline-flow)
2. [Data Pipeline](#data-pipeline)
3. [Model Training Flow](#model-training-flow)
4. [Deployment Architecture](#deployment-architecture)
5. [CI/CD Pipeline](#cicd-pipeline)
6. [Monitoring Flow](#monitoring-flow)

---

## Complete Pipeline Flow

```mermaid
graph TB
    A[Raw Data] --> B[Data Validation]
    B --> C{Validation Pass?}
    C -->|No| D[Alert & Fix]
    C -->|Yes| E[Data Preprocessing]
    E --> F[Feature Engineering]
    F --> G[Model Training]
    G --> H[MLflow Tracking]
    H --> I[Model Evaluation]
    I --> J{Performance OK?}
    J -->|No| K[Tune & Retrain]
    K --> G
    J -->|Yes| L[Save Best Models]
    L --> M[Docker Build]
    M --> N[Security Scan]
    N --> O{Scan Pass?}
    O -->|No| P[Fix Vulnerabilities]
    P --> M
    O -->|Yes| Q[Push to Registry]
    Q --> R[Deploy to K8s]
    R --> S[Health Checks]
    S --> T[Production]
    T --> U[Monitor]
    U --> V{Drift Detected?}
    V -->|Yes| W[Retrain Pipeline]
    W --> G
    V -->|No| U
```

---

## Data Pipeline

```mermaid
graph LR
    A[migraine_dataset.csv] --> B[validate_data.py]
    B --> C{Schema Valid?}
    B --> D{Missing < 10%?}
    B --> E{No Outliers?}
    B --> F{Class Balanced?}

    C -->|Yes| G[preprocess_data.py]
    D -->|Yes| G
    E -->|Yes| G
    F -->|Yes| G

    C -->|No| H[Generate Report]
    D -->|No| H
    E -->|No| H
    F -->|No| H

    G --> I[Impute Missing]
    I --> J[Remove Duplicates]
    J --> K[Handle Outliers]
    K --> L[Scale Features]
    L --> M[feature_engineering.py]

    M --> N[Create Interactions]
    M --> O[Create Polynomial]
    M --> P[Create Health Indices]
    M --> Q[Create Binning]

    N --> R[Feature Selection]
    O --> R
    P --> R
    Q --> R

    R --> S[Top 20 Features]
    S --> T[engineered_features.csv]
```

---

## Model Training Flow

```mermaid
graph TB
    A[Engineered Features] --> B{Task Type}

    B -->|Classification| C[8 Classification Models]
    B -->|Regression| D[8 Regression Models]

    C --> C1[Logistic Regression]
    C --> C2[Random Forest]
    C --> C3[Gradient Boosting]
    C --> C4[XGBoost]
    C --> C5[LightGBM]
    C --> C6[SVM]
    C --> C7[KNN]
    C --> C8[Naive Bayes]

    D --> D1[Linear Regression]
    D --> D2[Ridge]
    D --> D3[Lasso]
    D --> D4[ElasticNet]
    D --> D5[RF Regressor]
    D --> D6[GB Regressor]
    D --> D7[XGB Regressor]
    D --> D8[LGBM Regressor]

    C1 --> E[MLflow Logging]
    C2 --> E
    C3 --> E
    C4 --> E
    C5 --> E
    C6 --> E
    C7 --> E
    C8 --> E

    D1 --> E
    D2 --> E
    D3 --> E
    D4 --> E
    D5 --> E
    D6 --> E
    D7 --> E
    D8 --> E

    E --> F[Compare Performance]
    F --> G[Select Top 2]
    G --> H[Save Models]
    H --> I[Model Registry]
```

---

## Deployment Architecture

```mermaid
graph TB
    subgraph "Docker Layer"
        A[Docker Image]
        B[MLflow Container]
        C[API Container]
    end

    subgraph "Kubernetes Cluster"
        D[Namespace: migraine-ml]
        E[ConfigMap]
        F[Secret]
        G[PVC: mlflow-data]
        H[PVC: models]

        I[Deployment: API]
        J[Deployment: MLflow]

        K[Service: API]
        L[Service: MLflow]

        M[HPA: Auto-Scaler]
        N[Ingress: TLS]
    end

    subgraph "Monitoring"
        O[Prometheus]
        P[Grafana]
        Q[Alertmanager]
    end

    A --> C
    C --> I
    B --> J

    E --> I
    F --> I
    G --> J
    H --> I

    I --> K
    J --> L

    M --> I
    N --> K

    K --> O
    O --> P
    O --> Q

    R[Users] --> N
    N --> K
```

---

## CI/CD Pipeline

```mermaid
graph TB
    A[Git Push] --> B[GitHub Actions]

    B --> C[Stage 1: Code Quality]
    C --> C1[Black]
    C --> C2[Flake8]
    C --> C3[Pylint]

    C1 --> D{Pass?}
    C2 --> D
    C3 --> D

    D -->|No| E[Fail Build]
    D -->|Yes| F[Stage 2: Data Validation]

    F --> G[validate_data.py]
    G --> H{Valid?}
    H -->|No| E
    H -->|Yes| I[Stage 3: Unit Tests]

    I --> J[Run Pytest]
    J --> K{Coverage > 80%?}
    K -->|No| E
    K -->|Yes| L[Stage 4: Model Training]

    L --> M[preprocess_data.py]
    M --> N[feature_engineering.py]
    N --> O[migraine_models_enhanced.py]
    O --> P[evaluate_models.py]

    P --> Q{Accuracy > 80%?}
    Q -->|No| E
    Q -->|Yes| R[Stage 5: Docker Build]

    R --> S[Build Image]
    S --> T[Trivy Scan]
    T --> U{Vulnerabilities?}
    U -->|Critical| E
    U -->|None/Low| V[Push to Registry]

    V --> W[Stage 6: K8s Deploy]
    W --> X[kubectl apply]
    X --> Y[Wait for Rollout]
    Y --> Z[Stage 7: API Tests]

    Z --> AA[Integration Tests]
    AA --> AB{Tests Pass?}
    AB -->|No| AC[Rollback]
    AB -->|Yes| AD[Stage 8: Monitoring]

    AD --> AE[Deploy Prometheus]
    AE --> AF[Configure Alerts]
    AF --> AG[Stage 9: Notify]

    AG --> AH[Slack Notification]
    AH --> AI[Deployment Summary]
    AI --> AJ[Success!]
```

---

## Monitoring Flow

```mermaid
graph TB
    A[API Request] --> B[FastAPI]
    B --> C[Predict Endpoint]

    C --> D[Input Validation]
    D --> E{Valid?}
    E -->|No| F[Return 400 Error]
    E -->|Yes| G[Load Model]

    G --> H[Preprocess Input]
    H --> I[Make Prediction]
    I --> J[Return Response]

    C --> K[Prometheus Metrics]
    K --> K1[prediction_count++]
    K --> K2[latency_histogram]
    K --> K3[accuracy_gauge]
    K --> K4[error_count++]

    J --> L[Drift Detection]
    L --> M{PSI > 0.2?}
    M -->|Yes| N[Trigger Alert]
    M -->|No| O[Continue]

    N --> P[Log Drift Event]
    P --> Q[Slack Alert]
    Q --> R[Email Alert]

    K --> S[Prometheus Server]
    S --> T[Grafana Dashboard]

    T --> U[Real-time Metrics]
    U --> V{Threshold Exceeded?}
    V -->|Yes| W[Send Alert]
    V -->|No| X[Normal Operation]

    W --> Y[Alertmanager]
    Y --> Z[Notify Team]
```

---

## Drift Detection Flow

```mermaid
graph TB
    A[New Prediction Data] --> B[Store in Buffer]
    B --> C{Buffer Full?}
    C -->|No| A
    C -->|Yes| D[Run Drift Detection]

    D --> E[Calculate PSI]
    D --> F[Run KS Test]
    D --> G[Check Performance]

    E --> H{PSI > 0.2?}
    F --> I{p-value < 0.05?}
    G --> J{Accuracy Drop > 5%?}

    H -->|Yes| K[Data Drift Detected]
    I -->|Yes| K
    J -->|Yes| L[Performance Drift]

    K --> M[Generate Drift Report]
    L --> M

    M --> N[Send Alerts]
    N --> O[Slack]
    N --> P[Email]
    N --> Q[Log File]

    M --> R{Auto-Retrain?}
    R -->|Yes| S[Trigger Training Pipeline]
    R -->|No| T[Manual Review]

    S --> U[Data Preprocessing]
    U --> V[Feature Engineering]
    V --> W[Model Training]
    W --> X[Evaluation]
    X --> Y{Better Performance?}
    Y -->|Yes| Z[Deploy New Model]
    Y -->|No| AA[Keep Current Model]
```

---

## Model Evaluation Flow

```mermaid
graph TB
    A[Trained Models] --> B[Load Test Data]
    B --> C[Make Predictions]

    C --> D[Calculate Metrics]
    D --> D1[Accuracy]
    D --> D2[Precision]
    D --> D3[Recall]
    D --> D4[F1 Score]
    D --> D5[ROC-AUC]

    D1 --> E[Check Overfitting]
    D2 --> E
    D3 --> E
    D4 --> E
    D5 --> E

    E --> F{Train-Test Gap > 10%?}
    F -->|Yes| G[OVERFITTING]
    F -->|No| H[Check Underfitting]

    H --> I{Performance < 70%?}
    I -->|Yes| J[UNDERFITTING]
    I -->|No| K[Model is Good]

    G --> L[Recommendations]
    L --> L1[Reduce model complexity]
    L --> L2[Add regularization]
    L --> L3[Get more data]
    L --> L4[Feature selection]

    J --> M[Recommendations]
    M --> M1[Increase complexity]
    M --> M2[More features]
    M --> M3[Longer training]
    M --> M4[Better features]

    K --> N[Generate Report]
    N --> O[Confusion Matrix]
    N --> P[ROC Curve]
    N --> Q[Feature Importance]
    N --> R[HTML Report]
```

---

## Security Flow

```mermaid
graph TB
    A[Code Commit] --> B[GitHub Actions]

    B --> C[SAST Scan]
    C --> C1[Pylint]
    C --> C2[Bandit]

    C1 --> D{Issues?}
    C2 --> D
    D -->|Yes| E[Fail Build]
    D -->|No| F[Build Docker Image]

    F --> G[Trivy Scan]
    G --> H{Vulnerabilities?}
    H -->|Critical/High| E
    H -->|None/Low| I[Push to Registry]

    I --> J[Deploy to K8s]
    J --> K[Security Context]
    K --> K1[Non-root User]
    K --> K2[Read-only FS]
    K --> K3[Drop Capabilities]

    K1 --> L[Network Policy]
    K2 --> L
    K3 --> L

    L --> M[Runtime Security]
    M --> N[Input Validation]
    M --> O[Rate Limiting]
    M --> P[Authentication]

    N --> Q[Production]
    O --> Q
    P --> Q

    Q --> R[Continuous Monitoring]
    R --> S{Anomaly Detected?}
    S -->|Yes| T[Security Alert]
    S -->|No| Q

    T --> U[Incident Response]
    U --> V[Investigate]
    V --> W[Patch/Fix]
    W --> A
```

---

## End-to-End Request Flow

```mermaid
sequenceDiagram
    participant User
    participant Ingress
    participant Service
    participant Pod
    participant Model
    participant Prometheus
    participant DriftDetector

    User->>Ingress: POST /predict
    Ingress->>Service: Route Request
    Service->>Pod: Load Balance

    Pod->>Pod: Validate Input
    Pod->>Model: Load Model
    Model->>Model: Preprocess
    Model->>Model: Predict
    Model->>Pod: Return Prediction

    Pod->>Prometheus: Log Metrics
    Pod->>DriftDetector: Check Drift

    DriftDetector->>DriftDetector: Calculate PSI
    alt Drift Detected
        DriftDetector->>Pod: Drift Alert
        Pod->>User: Prediction + Warning
    else No Drift
        Pod->>User: Prediction
    end

    Prometheus->>Prometheus: Update Dashboard
```

---

## Resource Scaling Flow

```mermaid
graph TB
    A[Kubernetes HPA] --> B[Monitor Metrics]
    B --> C{CPU > 70%?}
    B --> D{Memory > 80%?}
    B --> E{Requests > Threshold?}

    C -->|Yes| F[Scale Decision]
    D -->|Yes| F
    E -->|Yes| F

    F --> G{Current Replicas < Max?}
    G -->|Yes| H[Scale Up]
    G -->|No| I[At Max Capacity]

    H --> J[Create New Pod]
    J --> K[Wait for Ready]
    K --> L[Add to Service]
    L --> M[Load Balance]

    C -->|No| N[Check Scale Down]
    D -->|No| N
    E -->|No| N

    N --> O{CPU < 30% AND Memory < 40%?}
    O -->|Yes| P{Current > Min?}
    P -->|Yes| Q[Scale Down]
    P -->|No| R[At Min Capacity]

    Q --> S[Remove Pod]
    S --> T[Graceful Shutdown]
    T --> U[Drain Connections]
    U --> M

    I --> V[Alert: Max Capacity]
    R --> W[Normal Operation]
```

---

## Notes

### Diagram Tools

These diagrams are written in Mermaid syntax and can be rendered using:

- GitHub (native support)
- Mermaid Live Editor: https://mermaid.live/
- VS Code extensions
- Documentation sites

### Color Legend

- **Green**: Success path
- **Red**: Error/failure path
- **Yellow**: Warning/alert
- **Blue**: Normal operation
- **Gray**: Decision point

### Updating Diagrams

When modifying the pipeline, update these diagrams to reflect:

1. New stages in CI/CD
2. Additional monitoring metrics
3. New security checks
4. Modified deployment strategy
5. Updated scaling policies

---

**Last Updated**: 2024
**Version**: 1.0.0
