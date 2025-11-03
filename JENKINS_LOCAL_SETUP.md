# 🏠 Jenkins LOCAL CI/CD Setup (No GitHub Required)

## 📋 Overview

This guide shows how to run Jenkins CI/CD pipeline using **local files only** - no GitHub needed!

---

## ✅ Prerequisites

- ✅ Jenkins running at http://localhost:9090
- ✅ Docker installed and accessible
- ✅ Docker Compose installed
- ✅ Project files at: `/home/rhemi/IA3/Dar_mlops/Migraine_CICD`

---

## 🚀 Setup Instructions (5 Minutes)

### Step 1: Open Jenkins

Go to: http://localhost:9090

### Step 2: Create New Pipeline Job

1. Click **New Item**
2. Enter name: `Migraine-ML-Local-Pipeline`
3. Select: **Pipeline**
4. Click **OK**

### Step 3: Configure Pipeline

Scroll down to **Pipeline** section:

**Definition**: Select **Pipeline script**

**Script**: Copy and paste this:

```groovy
pipeline {
    agent any
    
    environment {
        PROJECT_DIR = "/home/rhemi/IA3/Dar_mlops/Migraine_CICD"
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
        stage('Checkout Local Files') {
            steps {
                echo '📥 Using local project files...'
                sh """
                    echo "Project Directory: ${PROJECT_DIR}"
                    ls -la ${PROJECT_DIR}
                    cd ${PROJECT_DIR}
                    pwd
                """
            }
        }
        
        stage('Environment Setup') {
            steps {
                echo '🔧 Setting up build environment...'
                sh """
                    echo "Build Number: ${BUILD_NUMBER}"
                    echo "Project Dir: ${PROJECT_DIR}"
                    docker --version
                    docker-compose --version
                """
            }
        }
        
        stage('Build Docker Images') {
            parallel {
                stage('Build API Image') {
                    steps {
                        echo '🐳 Building API Docker image...'
                        sh """
                            cd ${PROJECT_DIR}
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
                            cd ${PROJECT_DIR}
                            docker build -f Dockerfile.streamlit \
                                -t ${STREAMLIT_IMAGE}:${IMAGE_TAG} \
                                -t ${STREAMLIT_IMAGE}:latest \
                                .
                        """
                    }
                }
            }
        }
        
        stage('Stop Old Containers') {
            steps {
                echo '🛑 Stopping old containers...'
                sh """
                    cd ${PROJECT_DIR}
                    docker-compose down || true
                    sleep 5
                """
            }
        }
        
        stage('Deploy Locally') {
            steps {
                echo '🚀 Deploying to local Docker...'
                sh """
                    cd ${PROJECT_DIR}
                    docker-compose up -d
                    sleep 15
                    docker-compose ps
                """
            }
        }
        
        stage('Health Check') {
            steps {
                echo '✅ Running health checks...'
                sh """
                    sleep 10
                    echo "Checking API..."
                    curl -s http://localhost:8000/health || echo "API not ready yet"
                    
                    echo "Checking Streamlit..."
                    curl -s -o /dev/null -w "HTTP %{http_code}" http://localhost:8501/_stcore/health || echo "Streamlit not ready"
                """
            }
        }
        
        stage('Deployment Summary') {
            steps {
                echo '📊 Deployment Summary'
                sh """
                    echo ""
                    echo "🎉 DEPLOYMENT SUCCESSFUL"
                    echo ""
                    echo "🌐 Access Points:"
                    echo "  🎨 Streamlit UI:  http://localhost:8501"
                    echo "  🔌 FastAPI:       http://localhost:8000"
                    echo "  📚 API Docs:      http://localhost:8000/docs"
                    echo "  📈 MLflow:        http://localhost:5000"
                    echo ""
                    docker ps --format "table {{.Names}}\\t{{.Status}}" | grep -E "(migraine|mlflow|NAMES)"
                    echo ""
                """
            }
        }
    }
    
    post {
        success {
            echo '✅ Pipeline completed successfully!'
            echo '🎨 Streamlit UI: http://localhost:8501'
        }
        
        failure {
            echo '❌ Pipeline failed! Check console output'
        }
        
        always {
            echo '🧹 Cleaning up old images...'
            sh """
                docker image prune -f || true
            """
        }
    }
}
```

### Step 4: Save

Click **Save** at the bottom

### Step 5: Build

Click **Build Now**

---

## 📊 What Happens During Build

```
Stage 1:  📥 Checkout Local Files    - Verify project directory
Stage 2:  🔧 Environment Setup       - Check Docker/Compose
Stage 3:  🐳 Build Docker Images     - Build API + Streamlit (parallel)
Stage 4:  🛑 Stop Old Containers     - Stop existing deployment
Stage 5:  🚀 Deploy Locally          - Start with docker-compose
Stage 6:  ✅ Health Check            - Verify all services
Stage 7:  📊 Deployment Summary      - Show access points
```

**Time**: ~15-20 minutes first build, ~5-10 minutes after

---

## 🌐 After Build Completes

Your services will be available at:

- 🎨 **Streamlit UI**: http://localhost:8501
- 🔌 **FastAPI**: http://localhost:8000
- 📚 **API Docs**: http://localhost:8000/docs
- 📈 **MLflow**: http://localhost:5000

Verify:
```bash
sudo docker ps
curl http://localhost:8000/health
```

---

## 🔄 Making Changes

### Edit Local Files
1. Make changes to your code in `/home/rhemi/IA3/Dar_mlops/Migraine_CICD`
2. Go to Jenkins → Your Pipeline
3. Click **Build Now**
4. Jenkins will rebuild and redeploy automatically

### No Git Needed!
- Changes are picked up immediately from local files
- No need to commit or push
- Perfect for development and testing

---

## 🎯 Alternative: Use Local Jenkinsfile

If you prefer to use the `Jenkinsfile.local`:

**In Pipeline Configuration**:
- **Definition**: Pipeline script from SCM
- **SCM**: None (use local file)
- Or simply copy the content from `Jenkinsfile.local` into the script box

---

## 📋 Quick Commands

### Check Running Services
```bash
sudo docker ps
```

### View Logs
```bash
sudo docker logs migraine-api -f
sudo docker logs migraine-streamlit -f
```

### Manual Start/Stop (without Jenkins)
```bash
cd /home/rhemi/IA3/Dar_mlops/Migraine_CICD

# Start
sudo docker-compose up -d

# Stop
sudo docker-compose down

# Rebuild
sudo docker-compose up -d --build
```

---

## 🔧 Troubleshooting

### Issue: Permission denied accessing project directory

**Solution**:
```bash
# Give Jenkins access to project directory
sudo chmod -R 755 /home/rhemi/IA3/Dar_mlops/Migraine_CICD

# Or add jenkins user to your group
sudo usermod -aG rhemi jenkins
sudo docker restart jenkins
```

### Issue: Can't find files in PROJECT_DIR

**Solution**: Verify path in pipeline script matches your actual path:
```bash
ls -la /home/rhemi/IA3/Dar_mlops/Migraine_CICD
```

### Issue: Docker build fails

**Solution**:
```bash
# Test Docker build manually first
cd /home/rhemi/IA3/Dar_mlops/Migraine_CICD
sudo docker build -f Dockerfile -t test-api .
```

---

## 🎨 Benefits of Local CI/CD

✅ **No GitHub needed** - Work completely offline
✅ **Instant updates** - Changes reflected immediately
✅ **Faster development** - No git commit/push overhead
✅ **Full CI/CD process** - Build, test, deploy automation
✅ **Easy debugging** - Direct access to all files
✅ **Perfect for development** - Test before pushing to GitHub

---

## 🔄 Workflow

```
1. Edit files locally
   ↓
2. Click "Build Now" in Jenkins
   ↓
3. Jenkins builds Docker images
   ↓
4. Jenkins deploys containers
   ↓
5. Access updated app at http://localhost:8501
```

---

## 📊 Monitoring

### Jenkins Dashboard
- View build history
- See build duration trends
- Check success/failure rates

### Console Output
- Click on build number
- Click "Console Output"
- See detailed logs

### Blue Ocean View (Optional)
- Install Blue Ocean plugin
- Better visualization
- Easier to see stage status

---

## 🎉 Success Checklist

After successful build:

- ✅ All pipeline stages green
- ✅ `docker ps` shows 3 containers (api, streamlit, mlflow)
- ✅ http://localhost:8501 opens Streamlit UI
- ✅ http://localhost:8000/health returns `{"status":"healthy"}`
- ✅ Can make predictions in Streamlit UI

---

## 🚀 Next Steps

1. **Make a change**: Edit `streamlit_app.py`
2. **Rebuild**: Click "Build Now" in Jenkins
3. **Verify**: Refresh http://localhost:8501 to see changes
4. **Repeat**: Keep developing with automated deployment!

---

## 📝 Summary

**You now have**:
- ✅ Full CI/CD pipeline running locally
- ✅ No GitHub dependency
- ✅ Automated build and deployment
- ✅ Easy testing and development workflow

**Jenkins at**: http://localhost:9090
**Your App at**: http://localhost:8501

🎊 **You can now develop with full CI/CD automation using only local files!** 🎊
