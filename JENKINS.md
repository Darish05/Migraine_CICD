# 🔧 Jenkins CI/CD Pipeline for Migraine Prediction System

## 📋 Overview

This document explains how to set up Jenkins for automated CI/CD deployment of the Migraine Prediction System with Streamlit UI.

## 🏗️ Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     JENKINS PIPELINE                         │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
   ┌─────────┐        ┌─────────┐        ┌─────────┐
   │  Build  │        │  Test   │        │  Scan   │
   │ Images  │        │  Code   │        │Security │
   └─────────┘        └─────────┘        └─────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            ▼
                    ┌───────────────┐
                    │ Push Registry │
                    └───────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
   ┌──────────┐      ┌──────────┐      ┌──────────┐
   │  Deploy  │      │  Deploy  │      │  Health  │
   │  Docker  │      │Streamlit │      │  Check   │
   │   Host   │      │  Cloud   │      │          │
   └──────────┘      └──────────┘      └──────────┘
```

## 🚀 Quick Start

### Prerequisites

1. **Jenkins Server** (2.400+)
   - Java 11 or 17
   - Docker installed on Jenkins agent
   - Docker Compose installed

2. **Required Plugins**:
   - Pipeline
   - Docker Pipeline
   - Git
   - Credentials Binding
   - Pipeline Utility Steps
   - Timestamper

3. **Access**:
   - Docker registry credentials
   - Deployment server SSH access
   - Streamlit Cloud token (optional)

### Installation Steps

#### 1. Install Jenkins

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y openjdk-11-jdk
wget -q -O - https://pkg.jenkins.io/debian-stable/jenkins.io.key | sudo apt-key add -
sudo sh -c 'echo deb https://pkg.jenkins.io/debian-stable binary/ > /etc/apt/sources.list.d/jenkins.list'
sudo apt update
sudo apt install -y jenkins

# Start Jenkins
sudo systemctl start jenkins
sudo systemctl enable jenkins

# Get initial admin password
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
```

Access Jenkins at: `http://your-server:8080`

#### 2. Install Required Plugins

Navigate to: **Manage Jenkins** → **Manage Plugins** → **Available**

Install:
- ✅ Pipeline
- ✅ Docker Pipeline
- ✅ Git plugin
- ✅ Credentials Binding Plugin
- ✅ Pipeline Utility Steps
- ✅ Timestamper
- ✅ JUnit Plugin (for test results)
- ✅ Slack Notification (optional)
- ✅ Email Extension (optional)

#### 3. Configure Docker on Jenkins Agent

```bash
# Add Jenkins user to docker group
sudo usermod -aG docker jenkins

# Restart Jenkins
sudo systemctl restart jenkins

# Verify Docker access
sudo su - jenkins
docker ps
exit
```

## 🔑 Configure Credentials

Navigate to: **Manage Jenkins** → **Manage Credentials** → **Global**

### Required Credentials

#### 1. Docker Hub / Registry Credentials
- **ID**: `docker-hub-credentials`
- **Type**: Username with password
- **Username**: Your Docker Hub username
- **Password**: Your Docker Hub token/password

#### 2. Docker Registry URL
- **ID**: `docker-registry-url`
- **Type**: Secret text
- **Secret**: `docker.io` (or your private registry URL)

#### 3. Deployment Host (Optional)
- **ID**: `deploy-host`
- **Type**: Secret text
- **Secret**: `user@your-deployment-server.com`

#### 4. SSH Credentials (for remote deployment)
- **ID**: `deploy-ssh-key`
- **Type**: SSH Username with private key
- **Username**: Deployment server user
- **Private Key**: Your SSH private key

#### 5. Streamlit Cloud Token (Optional)
- **ID**: `streamlit-cloud-token`
- **Type**: Secret text
- **Secret**: Your Streamlit Cloud API token

## 📝 Create Jenkins Pipeline Job

### Step 1: New Item
1. Click **New Item**
2. Enter name: `Migraine-ML-Pipeline`
3. Select **Pipeline**
4. Click **OK**

### Step 2: Configure Pipeline

#### General Settings
- ✅ Discard old builds: Keep last 10 builds
- ✅ GitHub project: `https://github.com/Darish05/Migraine_CICD`

#### Build Triggers
Choose one:
- **GitHub hook trigger for GITScm polling** (recommended for auto-deploy on push)
- **Poll SCM**: `H/5 * * * *` (check every 5 minutes)
- **Manual trigger only**

#### Pipeline Definition
- **Definition**: Pipeline script from SCM
- **SCM**: Git
- **Repository URL**: `https://github.com/Darish05/Migraine_CICD.git`
- **Credentials**: (Add GitHub credentials if private repo)
- **Branch**: `*/main`
- **Script Path**: `Jenkinsfile`

### Step 3: Save and Build

Click **Save**, then **Build Now**

## 🔄 Pipeline Stages Explained

### 1. **Checkout**
```groovy
stage('Checkout') {
    // Clones the Git repository
    checkout scm
}
```
- Pulls latest code from GitHub
- Displays latest commit info

### 2. **Environment Setup**
```groovy
stage('Environment Setup') {
    // Verifies build environment
    sh 'docker --version'
}
```
- Checks Docker and Docker Compose availability
- Displays build metadata

### 3. **Run Tests**
```groovy
stage('Run Tests') {
    // Runs Python unit tests
    pytest tests/ -v
}
```
- Creates virtual environment
- Installs dependencies
- Runs pytest (if tests exist)

### 4. **Lint & Code Quality**
```groovy
stage('Lint & Code Quality') {
    // Python syntax and style checks
    python3 -m py_compile
}
```
- Validates Python syntax
- Optional: pylint, flake8, black

### 5. **Build Docker Images**
```groovy
stage('Build Docker Images') {
    parallel {
        // Builds API and Streamlit images in parallel
    }
}
```
- Builds both images simultaneously
- Tags with build number and 'latest'

### 6. **Security Scan**
```groovy
stage('Security Scan') {
    // Scans for vulnerabilities
    trivy image $IMAGE_NAME
}
```
- Optional security scanning
- Can integrate Trivy, Snyk, Anchore

### 7. **Push to Registry**
```groovy
stage('Push to Registry') {
    when { branch 'main' }
    // Pushes to Docker registry
}
```
- Only runs on main branch
- Pushes versioned and latest tags
- Uses Docker Pipeline plugin

### 8. **Deploy to Docker Host**
```groovy
stage('Deploy to Docker Host') {
    when { branch 'main' }
    // Deploys via docker-compose
}
```
- Stops old containers
- Starts new containers
- Runs on main branch only

### 9. **Deploy to Streamlit Cloud**
```groovy
stage('Deploy to Streamlit Cloud') {
    when { 
        branch 'main'
        expression { env.STREAMLIT_CLOUD_TOKEN != null }
    }
}
```
- Optional cloud deployment
- Auto-deploys on main push
- Requires Streamlit Cloud token

### 10. **Health Check**
```groovy
stage('Health Check') {
    // Verifies services are running
    curl http://localhost:8000/health
}
```
- Checks API health endpoint
- Verifies Streamlit UI
- Checks MLflow server

### 11. **Smoke Tests**
```groovy
stage('Smoke Tests') {
    // Basic functionality tests
    curl -X POST /predict
}
```
- Tests API prediction endpoint
- Validates response format

## 🌐 GitHub Webhook Setup (Optional)

### Configure GitHub Webhook for Auto-Deploy

1. **In Jenkins**:
   - Navigate to: **Manage Jenkins** → **Configure System**
   - Find **GitHub** section
   - Add GitHub Server
   - Configure credentials

2. **In GitHub Repository**:
   - Go to: **Settings** → **Webhooks** → **Add webhook**
   - **Payload URL**: `http://your-jenkins-server:8080/github-webhook/`
   - **Content type**: `application/json`
   - **Secret**: (optional, configure in Jenkins)
   - **Events**: `Just the push event`
   - **Active**: ✅
   - Click **Add webhook**

3. **Test Webhook**:
   - Push a commit to main branch
   - Jenkins should auto-trigger the pipeline

## 📊 Monitoring & Notifications

### Slack Integration

1. **Install Slack Notification Plugin**
2. **Configure Slack**:
   - Get Slack webhook URL
   - Add to Jenkins credentials as secret text
3. **Add to Jenkinsfile**:
```groovy
post {
    success {
        slackSend(
            color: 'good',
            message: "Deploy Success: ${env.JOB_NAME} #${env.BUILD_NUMBER}"
        )
    }
    failure {
        slackSend(
            color: 'danger',
            message: "Deploy Failed: ${env.JOB_NAME} #${env.BUILD_NUMBER}"
        )
    }
}
```

### Email Notifications

Add to `post` section in Jenkinsfile:
```groovy
post {
    success {
        emailext(
            subject: "✅ Deploy Success: ${env.JOB_NAME}",
            body: "Build #${env.BUILD_NUMBER} succeeded",
            to: "team@example.com"
        )
    }
    failure {
        emailext(
            subject: "❌ Deploy Failed: ${env.JOB_NAME}",
            body: "Build #${env.BUILD_NUMBER} failed",
            to: "team@example.com"
        )
    }
}
```

## 🐳 Streamlit Cloud Deployment

### Option 1: Git-Based Deployment (Recommended)

Streamlit Cloud automatically deploys from your GitHub repository:

1. **Connect Repository**:
   - Go to: https://share.streamlit.io/
   - Sign in with GitHub
   - Click **New app**
   - Select repository: `Darish05/Migraine_CICD`
   - Main file path: `streamlit_app.py`
   - Click **Deploy**

2. **Configure Secrets** (in Streamlit Cloud UI):
   - Add API URL as secret
   - Configure any environment variables

3. **Auto-Deploy**:
   - Streamlit Cloud watches main branch
   - Auto-deploys on every push
   - No Jenkins integration needed for this option

### Option 2: API-Based Deployment

Use Streamlit Cloud API from Jenkins:

1. **Get API Token**:
   - Streamlit Cloud → Settings → API tokens
   - Add to Jenkins credentials

2. **Deploy from Jenkins**:
```groovy
stage('Deploy to Streamlit Cloud') {
    sh '''
        # Example using Streamlit CLI (if available)
        streamlit cloud deploy \
            --token ${STREAMLIT_CLOUD_TOKEN} \
            --app streamlit_app.py
    '''
}
```

## 🔒 Security Best Practices

### 1. Credential Management
- ✅ Never hardcode credentials in Jenkinsfile
- ✅ Use Jenkins Credentials plugin
- ✅ Rotate tokens regularly
- ✅ Use least-privilege access

### 2. Image Security
- ✅ Scan images with Trivy/Snyk
- ✅ Use official base images
- ✅ Run containers as non-root
- ✅ Keep images updated

### 3. Pipeline Security
- ✅ Restrict pipeline to specific branches
- ✅ Require approvals for production deploys
- ✅ Log all deployment activities
- ✅ Use separate credentials for prod/dev

## 🧪 Testing the Pipeline

### Manual Test

1. **Trigger Build**:
   - Go to Jenkins job
   - Click **Build Now**

2. **Monitor Progress**:
   - Watch **Blue Ocean** view (recommended)
   - Or classic **Console Output**

3. **Verify Deployment**:
```bash
# Check containers
docker ps

# Test API
curl http://localhost:8000/health

# Test Streamlit
curl http://localhost:8501/_stcore/health
```

### Automated Test

Push a change to trigger webhook:
```bash
git add .
git commit -m "Test Jenkins pipeline"
git push origin main
```

## 📦 Deployment Environments

### Development Environment
```groovy
environment {
    DEPLOY_ENV = 'development'
    API_URL = 'http://dev-api:8000'
}
```

### Staging Environment
```groovy
environment {
    DEPLOY_ENV = 'staging'
    API_URL = 'http://staging-api:8000'
}
```

### Production Environment
```groovy
when {
    branch 'main'
    environment name: 'DEPLOY_ENV', value: 'production'
}
```

## 🛠️ Troubleshooting

### Issue: Docker permission denied

**Solution**:
```bash
sudo usermod -aG docker jenkins
sudo systemctl restart jenkins
```

### Issue: Pipeline fails at Docker build

**Solution**:
- Check Docker daemon is running
- Verify Dockerfile syntax
- Check available disk space

### Issue: Can't push to Docker registry

**Solution**:
- Verify credentials in Jenkins
- Test manual login: `docker login`
- Check registry URL is correct

### Issue: Deployment fails - containers unhealthy

**Solution**:
```bash
# Check logs
docker-compose logs api

# Verify models exist
docker exec migraine-api ls -la models/

# Restart containers
docker-compose restart
```

### Issue: Streamlit Cloud deployment not working

**Solution**:
- Verify GitHub repository is public or Streamlit Cloud has access
- Check `streamlit_app.py` is in root directory
- Review Streamlit Cloud logs in dashboard

## 📚 Additional Resources

- [Jenkins Documentation](https://www.jenkins.io/doc/)
- [Docker Pipeline Plugin](https://plugins.jenkins.io/docker-workflow/)
- [Streamlit Cloud Docs](https://docs.streamlit.io/streamlit-community-cloud)
- [GitHub Webhooks Guide](https://docs.github.com/en/webhooks)

## 🎯 Next Steps

1. ✅ Set up Jenkins server
2. ✅ Configure credentials
3. ✅ Create pipeline job
4. ✅ Set up GitHub webhook
5. ✅ Test deployment
6. ✅ Configure notifications
7. ✅ Deploy to Streamlit Cloud
8. ✅ Monitor and maintain

## 📧 Support

For issues or questions:
- Check Jenkins logs: `/var/log/jenkins/jenkins.log`
- Review pipeline console output
- Contact: support@example.com

---

**Made with ❤️ for MLOps**
