# Deployment Workflow - Migraine ML System

## 🚀 Complete Deployment Steps

### Step 1: Run Jenkins Pipeline (Local Deployment)

1. **Start Jenkins** (if not already running):
   ```bash
   # Jenkins should be running at http://localhost:8080
   ```

2. **Run the Pipeline**:
   - Go to http://localhost:8080
   - Select "Migraine-ML-Local" job
   - Click "Build Now"
   - Wait for pipeline to complete (~5-10 minutes)

3. **Verify Services Running**:
   - API: http://localhost:8000/docs
   - Streamlit UI: http://localhost:8501
   - MLflow: http://localhost:5000

### Step 2: Expose API with ngrok (For Streamlit Cloud)

After the Jenkins pipeline completes successfully:

1. **Run the ngrok script**:
   ```bash
   cd /home/rhemi/IA3/Dar_mlops/Migraine_CICD
   ./run_ngrok.sh
   ```

2. **Copy the ngrok URL**:
   - Look for the "Forwarding" line in the ngrok output
   - Copy the HTTPS URL (e.g., `https://abc123.ngrok-free.app`)
   - **Keep this terminal open** - closing it will stop the tunnel

### Step 3: Deploy to Streamlit Cloud

1. **Go to Streamlit Cloud**:
   - Visit https://share.streamlit.io/
   - Sign in with GitHub

2. **Create New App**:
   - Click "New app"
   - Repository: `Darish05/Migraine_CICD`
   - Branch: `main`
   - Main file path: `streamlit_app.py`

3. **Add Secret for API URL**:
   - Click "Advanced settings"
   - Go to "Secrets" section
   - Add:
     ```toml
     API_URL = "https://your-ngrok-url.ngrok-free.app"
     ```
   - Replace with your actual ngrok URL from Step 2

4. **Deploy**:
   - Click "Deploy!"
   - Wait for deployment (~2-3 minutes)

### Step 4: Test the Application

1. **Access Streamlit Cloud App**:
   - Use the URL provided by Streamlit Cloud
   - Example: `https://your-app.streamlit.app`

2. **Test Predictions**:
   - Navigate to "Make Prediction" page
   - Enter patient data
   - Click "Predict"
   - Verify results appear

---

## 🔄 Daily Usage Workflow

### If ngrok tunnel is closed (URL changes):

1. **Restart ngrok**:
   ```bash
   cd /home/rhemi/IA3/Dar_mlops/Migraine_CICD
   ./run_ngrok.sh
   ```

2. **Update Streamlit Cloud Secret**:
   - Go to your app settings on Streamlit Cloud
   - Update the `API_URL` secret with the new ngrok URL
   - Streamlit will auto-reload

### If services need restart:

1. **Run Jenkins Pipeline again**:
   - http://localhost:8080
   - Build "Migraine-ML-Local"
   
2. **Restart ngrok** (after pipeline completes):
   ```bash
   ./run_ngrok.sh
   ```

---

## 📋 Quick Reference Commands

### Check Service Status
```bash
cd /home/rhemi/IA3/Dar_mlops/Migraine_CICD
docker-compose ps
```

### View Logs
```bash
# API logs
docker-compose logs api

# Streamlit logs
docker-compose logs streamlit

# All logs
docker-compose logs -f
```

### Stop Services
```bash
docker-compose down
```

### Restart Services (without Jenkins)
```bash
docker-compose up -d
```

### Stop ngrok
```bash
# Press Ctrl+C in the ngrok terminal
# OR
pkill ngrok
```

---

## 🌐 Service URLs

### Local Access:
- **API (Local)**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Streamlit UI (Local)**: http://localhost:8501
- **MLflow Tracking**: http://localhost:5000

### Public Access:
- **API (via ngrok)**: `https://your-ngrok-url.ngrok-free.app` (changes on restart)
- **Streamlit Cloud**: `https://your-app.streamlit.app` (permanent)

---

## 🛠️ Troubleshooting

### Issue: API not responding in Streamlit Cloud

**Solution**:
1. Check if ngrok is still running (terminal should be open)
2. Verify ngrok URL in Streamlit Cloud secrets matches current tunnel
3. Test API directly: `curl https://your-ngrok-url.ngrok-free.app/health`

### Issue: Services not starting

**Solution**:
1. Check Docker is running: `docker ps`
2. View logs: `docker-compose logs`
3. Restart: `docker-compose down && docker-compose up -d`

### Issue: Jenkins pipeline fails

**Solution**:
1. Check Jenkins console output for errors
2. Verify Docker has enough resources
3. Check if ports 8000, 8501, 5000 are available

### Issue: ngrok connection issues

**Solution**:
1. Verify ngrok authtoken is configured
2. Check if port 8000 is accessible: `curl http://localhost:8000/health`
3. Restart ngrok tunnel: `./run_ngrok.sh`

---

## 📝 Notes

- **ngrok URL changes** every time you restart ngrok (free tier limitation)
- **Keep ngrok terminal open** to maintain the tunnel
- **Streamlit Cloud** will need URL update when ngrok restarts
- **Jenkins pipeline** builds fresh Docker images each time
- **Named volumes** persist ML models and experiments across restarts

---

## 🎯 Architecture Overview

```
┌─────────────────────┐
│  Streamlit Cloud    │  (Public UI - Permanent URL)
│  your-app.streamlit │
└──────────┬──────────┘
           │
           │ HTTPS
           ▼
┌─────────────────────┐
│      ngrok          │  (Public Tunnel - URL changes)
│  xyz.ngrok-free.app │
└──────────┬──────────┘
           │
           │ HTTP
           ▼
┌─────────────────────┐
│   FastAPI Server    │  (Local - localhost:8000)
│   Docker Container  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   ML Models         │  (Local - Named Volume)
│   MLflow Tracking   │
└─────────────────────┘
```

---

**Happy Deploying! 🚀**
