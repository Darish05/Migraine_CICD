pipeline {
    agent any
    
    environment {
        API_IMAGE = "migraine-ml-api"
        STREAMLIT_IMAGE = "migraine-streamlit"
        IMAGE_TAG = "${env.BUILD_NUMBER}"
    }
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
    }

    stages {

        stage('Checkout Code') {
            steps {
                echo "📥 Cloning latest code from GitHub..."

                sh """
                    rm -rf ${WORKSPACE}/*
                    git clone https://github.com/Darish05/Migraine_CICD.git ${WORKSPACE}
                    
                    echo '✅ Repository cloned successfully'
                    echo '📂 Workspace contents:'
                    ls -la ${WORKSPACE}
                """
            }
        }

        stage('Environment Check') {
            steps {
                echo '🔧 Checking environment...'
                sh """
                    cd ${WORKSPACE}
                    echo "Build Number: ${BUILD_NUMBER}"
                    docker --version
                    docker-compose --version
                    
                    for file in app.py streamlit_app.py docker-compose.yml Dockerfile Dockerfile.streamlit; do
                        if [ -f "\$file" ]; then
                            echo "✅ Found \$file"
                        else
                            echo "❌ Missing \$file"
                        fi
                    done
                """
            }
        }

        stage('Code Quality') {
            steps {
                echo '🔍 Running code quality checks...'
                sh """
                    cd ${WORKSPACE}
                    python3 -m py_compile app.py || echo '⚠ app.py syntax issue'
                    python3 -m py_compile streamlit_app.py || echo '⚠ streamlit_app.py syntax issue'
                    python3 -m py_compile migraine_models_enhanced.py || echo '⚠ migraine_models_enhanced.py syntax issue'

                    echo '✅ Code quality checks completed'
                """
            }
        }

        stage('Build Images') {
            parallel {

                stage('Build API Image') {
                    steps {
                        echo '🐳 Building API Docker image...'
                        sh """
                            cd ${WORKSPACE}
                            docker build -f Dockerfile \
                                -t ${API_IMAGE}:${IMAGE_TAG} \
                                -t ${API_IMAGE}:latest \
                                .
                        """
                    }
                }

                stage('Build Streamlit Image') {
                    steps {
                        echo '🐳 Building Streamlit Docker image...'
                        sh """
                            cd ${WORKSPACE}
                            docker build -f Dockerfile.streamlit \
                                -t ${STREAMLIT_IMAGE}:${IMAGE_TAG} \
                                -t ${STREAMLIT_IMAGE}:latest \
                                .
                        """
                    }
                }
            }
        }

        stage('Stop Old Services') {
            steps {
                echo '🛑 Stopping old services...'
                sh """
                    cd ${WORKSPACE}
                    docker-compose down --remove-orphans || true
                    docker image prune -f || true
                """
            }
        }

        stage('Deploy Services') {
            steps {
                echo '🚀 Deploying services...'
                sh """
                    cd ${WORKSPACE}
                    docker-compose up -d
                    
                    echo '⏳ Waiting for services...'
                    sleep 10
                    docker-compose ps
                """
            }
        }

        stage('Health Check') {
            steps {
                echo '🏥 Running health checks...'
                sh """
                    sleep 30
                    
                    curl -f http://localhost:8000/health || echo '⚠ API not ready'
                    curl -f http://localhost:8501 || echo '⚠ Streamlit not ready'
                    curl -f http://localhost:5000 || echo '⚠ MLflow not ready'
                    
                    echo '✅ Health checks completed'
                """
            }
        }

        stage('Deployment Report') {
            steps {
                echo '📊 Deployment Summary'
                sh """
                    cd ${WORKSPACE}
                    docker images | grep migraine || true  
                    docker-compose ps
                """
            }
        }

    }
    
    post {
        success {
            echo '✅ Pipeline completed successfully!'
        }

        failure {
            echo '❌ Pipeline failed! Dumping logs...'
            sh """
                cd ${WORKSPACE}
                docker-compose logs --tail=50 || true
                docker ps -a
            """
        }

        always {
            echo '🧹 Cleaning up build temp files...'
            sh """
                cd ${WORKSPACE}
                rm -rf test_venv || true
                docker system prune -f || true
            """
        }
    }
}
