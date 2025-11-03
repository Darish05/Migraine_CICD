# 🚀 Jenkins Setup Guide for Migraine ML Pipeline
## Jenkins running at: http://localhost:9090

---

## ✅ Step-by-Step Setup

### Step 1: Access Jenkins
Open your browser and go to:
```
http://localhost:9090
```

### Step 2: Configure Jenkins User (if needed)
If this is first time, you may need the initial admin password:
```bash
sudo docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

### Step 3: Install Required Plugins

Go to: **Manage Jenkins** → **Manage Plugins** → **Available**

Search and install:
- ✅ **Pipeline** (should be already installed)
- ✅ **Docker Pipeline**
- ✅ **Git plugin**
- ✅ **Credentials Binding Plugin**

After installation, restart Jenkins if prompted.

---

## 🔑 Step 4: Add Docker Credentials

### 4.1 Add Docker Hub Credentials
1. Go to: **Manage Jenkins** → **Manage Credentials**
2. Click **(global)** domain
3. Click **Add Credentials**
4. Configure:
   - **Kind**: Username with password
   - **Username**: your-dockerhub-username
   - **Password**: your-dockerhub-token
   - **ID**: `docker-hub-credentials`
   - **Description**: Docker Hub Credentials
5. Click **Create**

### 4.2 Add Docker Registry URL
1. Click **Add Credentials** again
2. Configure:
   - **Kind**: Secret text
   - **Secret**: `docker.io` (or your registry URL)
   - **ID**: `docker-registry-url`
   - **Description**: Docker Registry URL
3. Click **Create**

---

## 📝 Step 5: Create Pipeline Job

### 5.1 Create New Item
1. Click **New Item** (top left)
2. Enter item name: `Migraine-ML-Pipeline`
3. Select: **Pipeline**
4. Click **OK**

### 5.2 Configure General Settings
- ✅ Check **Discard old builds**
  - Days to keep builds: 7
  - Max # of builds to keep: 10

### 5.3 Configure Build Triggers
Choose one option:

**Option A - Manual Trigger Only:**
- Leave all unchecked
- You'll manually click "Build Now"

**Option B - Poll SCM (Check for changes):**
- ✅ Check **Poll SCM**
- Schedule: `H/5 * * * *` (checks every 5 minutes)

**Option C - GitHub Webhook (Auto-trigger on push):**
- ✅ Check **GitHub hook trigger for GITScm polling**
- (Requires GitHub webhook configuration - see below)

### 5.4 Configure Pipeline

**Pipeline Definition:**
- Select: **Pipeline script from SCM**

**SCM:**
- Select: **Git**

**Repository URL:**
```
https://github.com/Darish05/Migraine_CICD.git
```

**Credentials:**
- If public repo: None
- If private: Add GitHub credentials

**Branch Specifier:**
```
*/main
```

**Script Path:**
```
Jenkinsfile
```

### 5.5 Save Configuration
Click **Save** at the bottom

---

## 🔧 Step 6: Configure Docker Access in Jenkins Container

The Jenkins container needs to access Docker on the host:

```bash
# Option 1: Give Jenkins container access to host Docker socket
sudo docker exec -u root jenkins chmod 666 /var/run/docker.sock

# OR Option 2: Add jenkins user to docker group (more permanent)
sudo docker exec -u root jenkins usermod -aG docker jenkins
sudo docker restart jenkins
```

### Verify Docker access:
```bash
sudo docker exec jenkins docker ps
```
This should show running containers without errors.

---

## 🏃 Step 7: Run Your First Build

### 7.1 Trigger Build
1. Go to your `Migraine-ML-Pipeline` job
2. Click **Build Now** (left sidebar)

### 7.2 Monitor Build
- Click on the build number (e.g., #1)
- Click **Console Output** to see logs
- Or use **Blue Ocean** view for better visualization

### 7.3 Expected Pipeline Stages
Your build should go through these stages:
1. ✅ Checkout
2. ✅ Environment Setup
3. ✅ Run Tests
4. ✅ Lint & Code Quality
5. ✅ Build Docker Images (API + Streamlit in parallel)
6. ✅ Security Scan
7. ⏭️ Push to Registry (only on main branch)
8. ✅ Deploy to Docker Host
9. ⏭️ Deploy to Streamlit Cloud (if token configured)
10. ✅ Health Check
11. ✅ Smoke Tests

---

## 🌐 Step 8: Access Deployed Services

After successful build, access:

- **Streamlit UI**: http://localhost:8501
- **FastAPI**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **MLflow**: http://localhost:5000

---

## 🔔 Step 9: Optional - Setup GitHub Webhook (Auto-Deploy)

### 9.1 Get Jenkins Webhook URL
Your webhook URL is:
```
http://your-server-ip:9090/github-webhook/
```

### 9.2 Configure in GitHub
1. Go to your GitHub repo: https://github.com/Darish05/Migraine_CICD
2. Click **Settings** → **Webhooks** → **Add webhook**
3. Configure:
   - **Payload URL**: `http://your-server-ip:9090/github-webhook/`
   - **Content type**: `application/json`
   - **Which events**: Just the push event
   - **Active**: ✅
4. Click **Add webhook**

Now every push to main will auto-trigger the pipeline!

---

## 📊 Step 10: Monitor Pipeline

### View Build Status
- **Dashboard**: Main Jenkins page shows recent builds
- **Blue Ocean**: Better visualization (install Blue Ocean plugin)
- **Console Output**: Detailed logs for debugging

### Check Deployment
```bash
# Check running containers
sudo docker ps

# Check API health
curl http://localhost:8000/health

# Check Streamlit
curl http://localhost:8501/_stcore/health
```

---

## 🐛 Troubleshooting

### Issue: Docker permission denied in Jenkins

**Error**: `permission denied while trying to connect to Docker daemon socket`

**Solution**:
```bash
# Give Jenkins access to Docker socket
sudo docker exec -u root jenkins chmod 666 /var/run/docker.sock

# Or permanently add to docker group
sudo docker exec -u root jenkins usermod -aG docker jenkins
sudo docker restart jenkins
```

### Issue: Git not found

**Solution**:
```bash
# Install git in Jenkins container
sudo docker exec -u root jenkins apt-get update
sudo docker exec -u root jenkins apt-get install -y git
```

### Issue: Docker Compose not found

**Solution**:
```bash
# Install docker-compose in Jenkins container
sudo docker exec -u root jenkins curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo docker exec -u root jenkins chmod +x /usr/local/bin/docker-compose
```

### Issue: Pipeline fails at "Push to Registry"

**Solution**:
- This stage only runs on `main` branch
- Ensure Docker Hub credentials are configured correctly
- Or comment out this stage if not needed

### Issue: Build stuck or taking too long

**Common Causes**:
- Building Docker images for first time (can take 15-20 minutes)
- Installing Python dependencies
- Training models

**Solution**: Be patient on first build, subsequent builds use cache and are much faster

---

## 🎯 Quick Start Commands

### Start Jenkins (if stopped)
```bash
sudo docker start jenkins
```

### Stop Jenkins
```bash
sudo docker stop jenkins
```

### View Jenkins Logs
```bash
sudo docker logs jenkins -f
```

### Access Jenkins Container
```bash
sudo docker exec -it jenkins bash
```

### Restart Jenkins
```bash
sudo docker restart jenkins
```

---

## 📋 Checklist

Before running your first build:

- ✅ Jenkins accessible at http://localhost:9090
- ✅ Docker Pipeline plugin installed
- ✅ Docker credentials configured
- ✅ Pipeline job created pointing to GitHub repo
- ✅ Jenkins has Docker access (verify with `docker ps`)
- ✅ Git and docker-compose available in Jenkins

---

## 🎉 Success Criteria

Your first build is successful when:

1. ✅ All pipeline stages complete (green checkmarks)
2. ✅ Docker images are built
3. ✅ Containers are running: `sudo docker ps` shows api, streamlit, mlflow
4. ✅ Services respond:
   - `curl http://localhost:8000/health` returns `{"status":"healthy"}`
   - `curl http://localhost:8501` returns HTTP 200
5. ✅ You can access Streamlit UI in browser at http://localhost:8501

---

## 📞 Next Steps

After successful first build:

1. **Test the UI**: Open http://localhost:8501 and make a prediction
2. **Setup Webhook**: Configure GitHub webhook for auto-deploy
3. **Configure Notifications**: Add Slack/Email notifications to Jenkinsfile
4. **Deploy to Production**: Configure production credentials and deployment
5. **Monitor**: Set up monitoring and alerts

---

## 📚 Additional Resources

- **Jenkinsfile**: `/home/rhemi/IA3/Dar_mlops/Migraine_CICD/Jenkinsfile`
- **Full Documentation**: `JENKINS.md`
- **Quick Reference**: `QUICK_REFERENCE.txt`
- **Jenkins Dashboard**: http://localhost:9090

---

**Your Jenkins is ready! Create the pipeline job and click "Build Now" to deploy! 🚀**
