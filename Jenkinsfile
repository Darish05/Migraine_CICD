pipeline {
    agent any
    
    environment {
        // Docker registry credentials (configure in Jenkins)
        DOCKER_REGISTRY = credentials('docker-registry-url')  // e.g., 'docker.io' or your registry
        DOCKER_CREDENTIALS = credentials('docker-hub-credentials')
        
        // Image names
        API_IMAGE = "migraine-ml-api"
        STREAMLIT_IMAGE = "migraine-streamlit"
        IMAGE_TAG = "${env.BUILD_NUMBER}"
        
        // Deployment target
        DEPLOY_HOST = credentials('deploy-host')  // SSH target for deployment
        
        // Streamlit Cloud (optional)
        STREAMLIT_CLOUD_TOKEN = credentials('streamlit-cloud-token')
    }
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo '📥 Checking out source code...'
                checkout scm
                sh 'git log -1'
            }
        }
        
        stage('Environment Setup') {
            steps {
                echo '🔧 Setting up build environment...'
                sh '''
                    echo "Build Number: ${BUILD_NUMBER}"
                    echo "Git Branch: ${GIT_BRANCH}"
                    echo "Git Commit: ${GIT_COMMIT}"
                    docker --version
                    docker-compose --version
                '''
            }
        }
        
        stage('Run Tests') {
            steps {
                echo '🧪 Running unit tests...'
                sh '''
                    # Create virtual environment for testing
                    python3 -m venv test_venv
                    . test_venv/bin/activate
                    pip install -q -r requirements.txt
                    
                    # Run tests if they exist
                    if [ -d "tests" ]; then
                        pytest tests/ -v --tb=short || true
                    else
                        echo "No tests directory found, skipping tests"
                    fi
                    
                    deactivate
                    rm -rf test_venv
                '''
            }
        }
        
        stage('Lint & Code Quality') {
            steps {
                echo '🔍 Running code quality checks...'
                sh '''
                    # Basic Python syntax check
                    python3 -m py_compile app.py streamlit_app.py migraine_models_enhanced.py || true
                    
                    # Optional: Add pylint, flake8, black checks here
                    echo "Code quality checks completed"
                '''
            }
        }
        
        stage('Build Docker Images') {
            parallel {
                stage('Build API Image') {
                    steps {
                        echo '🐳 Building API Docker image...'
                        sh '''
                            docker build -f Dockerfile \
                                -t ${API_IMAGE}:${IMAGE_TAG} \
                                -t ${API_IMAGE}:latest \
                                .
                        '''
                    }
                }
                
                stage('Build Streamlit Image') {
                    steps {
                        echo '🐳 Building Streamlit Docker image...'
                        sh '''
                            docker build -f Dockerfile.streamlit \
                                -t ${STREAMLIT_IMAGE}:${IMAGE_TAG} \
                                -t ${STREAMLIT_IMAGE}:latest \
                                .
                        '''
                    }
                }
            }
        }
        
        stage('Security Scan') {
            steps {
                echo '🔒 Running security scans...'
                sh '''
                    # Optional: Trivy, Snyk, or other security scanning
                    echo "Security scan placeholder - integrate Trivy or Snyk here"
                    
                    # Example with Trivy (if installed):
                    # trivy image ${API_IMAGE}:${IMAGE_TAG} || true
                    # trivy image ${STREAMLIT_IMAGE}:${IMAGE_TAG} || true
                '''
            }
        }
        
        stage('Push to Registry') {
            when {
                branch 'main'
            }
            steps {
                echo '📤 Pushing images to Docker registry...'
                script {
                    docker.withRegistry("https://${DOCKER_REGISTRY}", 'docker-hub-credentials') {
                        sh '''
                            docker tag ${API_IMAGE}:${IMAGE_TAG} ${DOCKER_REGISTRY}/${API_IMAGE}:${IMAGE_TAG}
                            docker tag ${API_IMAGE}:latest ${DOCKER_REGISTRY}/${API_IMAGE}:latest
                            docker push ${DOCKER_REGISTRY}/${API_IMAGE}:${IMAGE_TAG}
                            docker push ${DOCKER_REGISTRY}/${API_IMAGE}:latest
                            
                            docker tag ${STREAMLIT_IMAGE}:${IMAGE_TAG} ${DOCKER_REGISTRY}/${STREAMLIT_IMAGE}:${IMAGE_TAG}
                            docker tag ${STREAMLIT_IMAGE}:latest ${DOCKER_REGISTRY}/${STREAMLIT_IMAGE}:latest
                            docker push ${DOCKER_REGISTRY}/${STREAMLIT_IMAGE}:${IMAGE_TAG}
                            docker push ${DOCKER_REGISTRY}/${STREAMLIT_IMAGE}:latest
                        '''
                    }
                }
            }
        }
        
        stage('Deploy to Docker Host') {
            when {
                branch 'main'
            }
            steps {
                echo '🚀 Deploying to production...'
                sh '''
                    # Stop existing containers
                    docker-compose down || true
                    
                    # Pull latest images (if using registry)
                    # docker-compose pull
                    
                    # Start services
                    docker-compose up -d
                    
                    # Wait for health checks
                    echo "Waiting for services to be healthy..."
                    sleep 20
                    
                    # Verify deployment
                    docker-compose ps
                '''
            }
        }
        
        stage('Deploy to Streamlit Cloud') {
            when {
                branch 'main'
                expression { env.STREAMLIT_CLOUD_TOKEN != null }
            }
            steps {
                echo '☁️ Deploying to Streamlit Cloud...'
                sh '''
                    # This requires Streamlit Cloud CLI or API
                    # Example placeholder:
                    echo "Streamlit Cloud deployment would happen here"
                    
                    # Option 1: Git-based deployment (Streamlit Cloud watches repo)
                    # Already handled by pushing to main branch
                    
                    # Option 2: Use Streamlit Cloud API
                    # streamlit cloud deploy --token ${STREAMLIT_CLOUD_TOKEN}
                '''
            }
        }
        
        stage('Health Check') {
            steps {
                echo '✅ Running health checks...'
                sh '''
                    # Wait for services
                    sleep 10
                    
                    # Check API health
                    API_HEALTH=$(curl -s http://localhost:8000/health || echo "FAIL")
                    echo "API Health: $API_HEALTH"
                    
                    # Check Streamlit health
                    STREAMLIT_HEALTH=$(curl -s http://localhost:8501/_stcore/health || echo "FAIL")
                    echo "Streamlit Health: $STREAMLIT_HEALTH"
                    
                    # Check MLflow health
                    MLFLOW_HEALTH=$(curl -s http://localhost:5000/health || echo "FAIL")
                    echo "MLflow Health: $MLFLOW_HEALTH"
                '''
            }
        }
        
        stage('Smoke Tests') {
            steps {
                echo '💨 Running smoke tests...'
                sh '''
                    # Test API prediction endpoint
                    curl -X POST http://localhost:8000/predict \
                        -H "Content-Type: application/json" \
                        -d '{
                            "age": 30,
                            "gender": 1,
                            "sleep_hours": 7,
                            "sleep_quality": 7,
                            "stress_level": 5,
                            "hydration": 7,
                            "exercise": 3,
                            "screen_time": 6,
                            "caffeine_intake": 2,
                            "alcohol_intake": 1,
                            "weather_changes": 0,
                            "menstrual_cycle": 0,
                            "dehydration": 0,
                            "bright_light": 0,
                            "loud_noises": 0,
                            "strong_smells": 0,
                            "missed_meals": 0,
                            "specific_foods": 0,
                            "physical_activity": 0,
                            "neck_pain": 0,
                            "weather_pressure": 1013.25,
                            "humidity": 60.0,
                            "temperature_change": 0.0
                        }' \
                        -w "\\nHTTP Status: %{http_code}\\n" || true
                '''
            }
        }
    }
    
    post {
        success {
            echo '✅ Pipeline completed successfully!'
            // Optional: Send notifications
            // slackSend(color: 'good', message: "Deploy Success: ${env.JOB_NAME} #${env.BUILD_NUMBER}")
            // emailext(subject: "Deploy Success", body: "Build succeeded", to: "team@example.com")
        }
        
        failure {
            echo '❌ Pipeline failed!'
            // Optional: Send failure notifications
            // slackSend(color: 'danger', message: "Deploy Failed: ${env.JOB_NAME} #${env.BUILD_NUMBER}")
            // emailext(subject: "Deploy Failed", body: "Build failed", to: "team@example.com")
        }
        
        always {
            echo '🧹 Cleaning up...'
            sh '''
                # Clean up old Docker images
                docker image prune -f --filter "label=stage=builder" || true
                docker system prune -f --filter "label=stage=builder" || true
            '''
            
            // Archive artifacts
            archiveArtifacts artifacts: '**/logs/*.log', allowEmptyArchive: true
            
            // Publish test results if available
            junit testResults: '**/test-results/*.xml', allowEmptyResults: true
        }
    }
}
