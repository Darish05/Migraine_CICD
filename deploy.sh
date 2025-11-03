#!/bin/bash
# deploy.sh - Complete deployment automation script

set -e

echo "🚀 Starting Migraine ML System Deployment"
echo "========================================"

# Configuration
PROJECT_NAME="migraine-ml"
DOCKER_REGISTRY=${DOCKER_REGISTRY:-"your-registry"}
ENV=${ENV:-"production"}

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    echo ""
    echo "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker not found. Please install Docker."
        exit 1
    fi
    print_status "Docker found"
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        print_warning "kubectl not found. Kubernetes deployment will be skipped."
    else
        print_status "kubectl found"
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 not found."
        exit 1
    fi
    print_status "Python 3 found"
}

# Setup DVC
setup_dvc() {
    echo ""
    echo "Setting up DVC..."
    
    pip install dvc[s3] -q
    
    # Initialize DVC if not already initialized
    if [ ! -d ".dvc" ]; then
        dvc init
        print_status "DVC initialized"
    fi
    
    # Configure remote storage
    if [ ! -z "$DVC_REMOTE_URL" ]; then
        dvc remote add -d myremote $DVC_REMOTE_URL
        print_status "DVC remote configured"
    fi
    
    # Pull data
    if [ -f "data/migraine_dataset.csv.dvc" ]; then
        dvc pull
        print_status "Data pulled from DVC"
    fi
}

# Train models
train_models() {
    echo ""
    echo "Training models..."
    
    # Install dependencies
    pip install -r requirements.txt -q
    
    # Run data validation
    python scripts/validate_data.py
    
    # Train models
    python migraine_models_enhanced.py
    
    print_status "Models trained successfully"
}

# Run tests
run_tests() {
    echo ""
    echo "Running tests..."
    
    pip install pytest pytest-cov -q
    
    # Unit tests
    pytest tests/test_models.py -v
    
    # Integration tests
    if [ -d "tests/integration" ]; then
        pytest tests/integration/ -v
    fi
    
    print_status "All tests passed"
}

# Build Docker images
build_docker() {
    echo ""
    echo "Building Docker images..."
    
    # Build ML API
    docker build -t ${DOCKER_REGISTRY}/${PROJECT_NAME}:${ENV} .
    docker build -t ${DOCKER_REGISTRY}/${PROJECT_NAME}:latest .
    
    print_status "Docker images built"
}

# Push Docker images
push_docker() {
    echo ""
    echo "Pushing Docker images..."
    
    docker push ${DOCKER_REGISTRY}/${PROJECT_NAME}:${ENV}
    docker push ${DOCKER_REGISTRY}/${PROJECT_NAME}:latest
    
    print_status "Docker images pushed"
}

# Deploy with Docker Compose
deploy_docker_compose() {
    echo ""
    echo "Deploying with Docker Compose..."
    
    # Stop existing containers
    docker-compose down
    
    # Start new containers
    docker-compose up -d
    
    # Wait for services to be healthy
    sleep 10
    
    # Check health
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        print_status "ML API is healthy"
    else
        print_error "ML API health check failed"
        exit 1
    fi
    
    print_status "Docker Compose deployment complete"
    echo ""
    echo "Services running at:"
    echo "  - ML API: http://localhost:8000"
    echo "  - MLflow UI: http://localhost:5000"
    echo "  - Frontend: http://localhost:3000"
}

# Deploy to Kubernetes
deploy_kubernetes() {
    echo ""
    echo "Deploying to Kubernetes..."
    
    # Apply configurations
    kubectl apply -f kubernetes/deployment.yaml
    
    # Wait for rollout
    kubectl rollout status deployment/ml-api-deployment -n ${PROJECT_NAME}
    
    # Get service endpoints
    kubectl get services -n ${PROJECT_NAME}
    
    print_status "Kubernetes deployment complete"
}

# Setup monitoring
setup_monitoring() {
    echo ""
    echo "Setting up monitoring..."
    
    # Install Prometheus and Grafana (if using Kubernetes)
    if command -v helm &> /dev/null; then
        helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
        helm repo update
        
        helm install prometheus prometheus-community/kube-prometheus-stack \
            --namespace monitoring --create-namespace
        
        print_status "Monitoring stack installed"
    fi
}

# Verify deployment
verify_deployment() {
    echo ""
    echo "Verifying deployment..."
    
    # Run smoke tests
    if [ -f "tests/smoke_tests.py" ]; then
        python tests/smoke_tests.py --env ${ENV}
        print_status "Smoke tests passed"
    fi
    
    # Check MLflow
    if curl -f http://localhost:5000 > /dev/null 2>&1; then
        print_status "MLflow UI is accessible"
    fi
}

# Main deployment flow
main() {
    echo ""
    echo "Deployment Environment: ${ENV}"
    echo "Docker Registry: ${DOCKER_REGISTRY}"
    echo ""
    
    check_prerequisites
    
    # Setup phase
    setup_dvc
    
    # Build phase
    train_models
    run_tests
    build_docker
    
    # Deploy phase
    if [ "${DEPLOY_MODE}" = "kubernetes" ]; then
        push_docker
        deploy_kubernetes
        setup_monitoring
    else
        deploy_docker_compose
    fi
    
    # Verify phase
    verify_deployment
    
    echo ""
    echo "========================================"
    echo -e "${GREEN}✓ Deployment Complete!${NC}"
    echo "========================================"
    echo ""
    
    # Print summary
    echo "Summary:"
    echo "  - Models trained and validated"
    echo "  - Docker images built and deployed"
    echo "  - Services are running and healthy"
    echo "  - MLflow tracking available"
    echo ""
    echo "Next steps:"
    echo "  1. Access ML API at http://localhost:8000"
    echo "  2. View experiments at http://localhost:5000"
    echo "  3. Monitor logs: docker-compose logs -f"
    echo "  4. Run predictions: curl -X POST http://localhost:8000/predict"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --env)
            ENV="$2"
            shift 2
            ;;
        --registry)
            DOCKER_REGISTRY="$2"
            shift 2
            ;;
        --mode)
            DEPLOY_MODE="$2"
            shift 2
            ;;
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --help)
            echo "Usage: ./deploy.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --env ENV              Environment (development/staging/production)"
            echo "  --registry REGISTRY    Docker registry URL"
            echo "  --mode MODE            Deployment mode (docker-compose/kubernetes)"
            echo "  --skip-tests           Skip running tests"
            echo "  --help                 Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Run main deployment
main

---
#!/bin/bash
# build.sh - Build script for CI/CD

set -e

echo "🔨 Building Migraine ML System"

# Install dependencies
pip install -r requirements.txt

# Run data validation
python scripts/validate_data.py

# Train models
python migraine_models_enhanced.py

# Run tests
pytest tests/ -v --cov=.

# Build Docker image
docker build -t migraine-ml:latest .

echo "✅ Build complete!"

---
#!/bin/bash
# test.sh - Run all tests

set -e

echo "🧪 Running Tests"

# Unit tests
echo "Running unit tests..."
pytest tests/test_models.py -v

# Integration tests
if [ -d "tests/integration" ]; then
    echo "Running integration tests..."
    pytest tests/integration/ -v
fi

# API tests
if [ -f "tests/test_api.py" ]; then
    echo "Running API tests..."
    pytest tests/test_api.py -v
fi

# Performance tests
if [ -f "tests/test_performance.py" ]; then
    echo "Running performance tests..."
    pytest tests/test_performance.py -v
fi

echo "✅ All tests passed!"

---
#!/bin/bash
# rollback.sh - Rollback deployment

set -e

echo "⏪ Rolling back deployment"

if [ "${DEPLOY_MODE}" = "kubernetes" ]; then
    # Kubernetes rollback
    kubectl rollout undo deployment/ml-api-deployment -n migraine-ml
    kubectl rollout status deployment/ml-api-deployment -n migraine-ml
else
    # Docker Compose rollback
    docker-compose down
    docker-compose up -d --scale ml-api=0
    # Restore previous version
    docker tag migraine-ml:previous migraine-ml:latest
    docker-compose up -d
fi

echo "✅ Rollback complete!"

---
# Makefile
.PHONY: install train test build deploy clean

install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

setup-dvc:
	dvc init
	dvc remote add -d myremote s3://my-bucket/migraine-ml

train:
	python scripts/validate_data.py
	python migraine_models_enhanced.py

test:
	pytest tests/ -v --cov=. --cov-report=html

build:
	docker build -t migraine-ml:latest .

deploy-local:
	docker-compose up -d

deploy-k8s:
	kubectl apply -f kubernetes/
	kubectl rollout status deployment/ml-api-deployment -n migraine-ml

stop:
	docker-compose down

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf *.pkl

logs:
	docker-compose logs -f ml-api

monitor:
	python scripts/monitor_deployment.py

mlflow-ui:
	mlflow ui --backend-store-uri mlruns

all: install train test build deploy-local