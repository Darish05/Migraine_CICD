# 🐳 DOCKER SETUP & TROUBLESHOOTING GUIDE

## 🚨 STEP 1: Start Docker Desktop

### **YOU MUST DO THIS FIRST!**

1. **Open Docker Desktop Application**

   - Press `Windows Key`
   - Type "Docker Desktop"
   - Click to open it
   - Wait for it to fully start (usually 30-60 seconds)

2. **Verify Docker is Running**

   - Look for Docker icon in system tray (bottom-right)
   - Icon should be **solid** (not flashing/animated)
   - Click icon → Should show "Docker Desktop is running"

3. **Test Docker in Terminal**

```powershell
docker --version
docker ps
```

If both commands work without errors, Docker is ready! ✅

---

## 🔧 Common Docker Issues & Fixes

### Issue 1: "Cannot connect to Docker daemon"

**Solution:**

1. Open Docker Desktop
2. Wait until it says "Docker Desktop is running"
3. Try command again

### Issue 2: Docker Desktop won't start

**Solution A - Restart Docker:**

```powershell
# Stop Docker (Run as Administrator)
Stop-Service -Name "com.docker.service" -Force

# Start Docker Desktop from Start Menu
# Wait 60 seconds
```

**Solution B - Restart Computer:**
Sometimes Windows needs a reboot for Docker to work properly.

### Issue 3: "WSL 2 installation is incomplete"

**Solution:**

```powershell
# Run as Administrator
wsl --update
wsl --set-default-version 2

# Then restart Docker Desktop
```

### Issue 4: "Hardware assisted virtualization" error

**Solution:**

1. Restart computer
2. Enter BIOS (usually F2, F10, or Delete key during boot)
3. Enable "Intel VT-x" or "AMD-V"
4. Save and restart

---

## ✅ Once Docker is Running - Build & Deploy

### Option 1: Docker Compose (Easiest)

```powershell
# Build and start services
docker-compose up -d

# Check if running
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Option 2: Docker Only

```powershell
# Build the image
docker build -t migraine-ml-api:latest .

# Run the container
docker run -d -p 8000:8000 --name migraine-api migraine-ml-api:latest

# Check if running
docker ps

# View logs
docker logs migraine-api -f

# Stop container
docker stop migraine-api
docker rm migraine-api
```

---

## 🎯 Complete Docker Workflow

### **1. Ensure Models are Trained First**

```powershell
# You MUST have trained models before building Docker image
# If you haven't trained models yet:
.\setup_and_run.ps1
```

This creates the `.pkl` model files that Docker needs.

### **2. Build Docker Image**

```powershell
# Build the image (takes 5-10 minutes first time)
docker build -t migraine-ml-api:latest .

# Verify image was created
docker images | Select-String migraine
```

### **3. Start with Docker Compose**

```powershell
# Start all services (API + MLflow)
docker-compose up -d

# Wait 10-15 seconds for services to start
Start-Sleep -Seconds 15

# Check status
docker-compose ps
```

### **4. Verify Services are Running**

```powershell
# Check containers
docker ps

# Test API health
curl http://localhost:8000/health

# Test API prediction endpoint
curl http://localhost:8000/docs
```

### **5. View Logs**

```powershell
# View all logs
docker-compose logs

# View API logs only
docker-compose logs api

# Follow logs in real-time
docker-compose logs -f api
```

---

## 🧪 Test Docker Deployment

### Test 1: Health Check

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/health"
# Expected: {"status":"healthy"}
```

### Test 2: Prediction

```powershell
$headers = @{"Content-Type"="application/json"}
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

Invoke-RestMethod -Uri "http://localhost:8000/predict" -Method Post -Headers $headers -Body $body
```

### Test 3: Access Services

- **API Documentation**: http://localhost:8000/docs
- **MLflow UI**: http://localhost:5000

---

## 📋 Docker Compose Services

Your `docker-compose.yml` includes:

1. **api** (Port 8000)

   - FastAPI application
   - Serves predictions
   - Health checks enabled

2. **mlflow** (Port 5000)
   - MLflow tracking server
   - Experiment visualization
   - Model registry

Both services are connected via a custom network.

---

## 🔍 Debugging Docker Issues

### Check Container Status

```powershell
# List running containers
docker ps

# List all containers (including stopped)
docker ps -a

# Inspect specific container
docker inspect migraine-api
```

### View Container Logs

```powershell
# View logs
docker logs migraine-api

# Follow logs in real-time
docker logs -f migraine-api

# View last 50 lines
docker logs --tail 50 migraine-api
```

### Execute Commands Inside Container

```powershell
# Open bash shell
docker exec -it migraine-api /bin/bash

# Check Python version
docker exec migraine-api python --version

# List files
docker exec migraine-api ls -la
```

### Check Resource Usage

```powershell
# View resource usage
docker stats

# View specific container
docker stats migraine-api
```

---

## 🧹 Clean Up Docker

### Remove Containers

```powershell
# Stop all services
docker-compose down

# Remove containers
docker rm -f migraine-api mlflow

# Remove all stopped containers
docker container prune -f
```

### Remove Images

```powershell
# Remove specific image
docker rmi migraine-ml-api:latest

# Remove unused images
docker image prune -a -f
```

### Complete Cleanup

```powershell
# Stop everything
docker-compose down -v

# Remove all containers, images, volumes, networks
docker system prune -a --volumes -f
```

---

## 🚀 Complete Docker Setup Checklist

- [ ] Step 1: Start Docker Desktop
- [ ] Step 2: Verify Docker is running (`docker ps`)
- [ ] Step 3: Train models first (`.\setup_and_run.ps1`)
- [ ] Step 4: Build Docker image (`docker build -t migraine-ml-api:latest .`)
- [ ] Step 5: Start services (`docker-compose up -d`)
- [ ] Step 6: Wait 15 seconds for services to start
- [ ] Step 7: Test health endpoint (`curl http://localhost:8000/health`)
- [ ] Step 8: Access API docs (http://localhost:8000/docs)
- [ ] Step 9: Test prediction endpoint
- [ ] Step 10: Access MLflow UI (http://localhost:5000)

---

## ⚡ Quick Commands Reference

```powershell
# Start Docker Desktop (manually open application)

# Build
docker build -t migraine-ml-api:latest .

# Start
docker-compose up -d

# Check
docker-compose ps
docker-compose logs -f

# Test
curl http://localhost:8000/health

# Stop
docker-compose down

# Rebuild
docker-compose up -d --build
```

---

## 🎯 Expected Output When Working

After `docker-compose up -d`:

```
Creating network "migraine-ml_default" with the default driver
Creating migraine-ml_mlflow_1 ... done
Creating migraine-ml_api_1    ... done
```

After `docker-compose ps`:

```
        Name                      Command               State           Ports
----------------------------------------------------------------------------------------
migraine-ml_api_1      /bin/sh -c uvicorn app:ap ...   Up      0.0.0.0:8000->8000/tcp
migraine-ml_mlflow_1   mlflow server --host 0.0. ...   Up      0.0.0.0:5000->5000/tcp
```

---

## 💡 Pro Tips

1. **Always start Docker Desktop FIRST**
2. **Train models BEFORE building Docker image**
3. **Use `docker-compose logs -f` to see real-time logs**
4. **Use `docker-compose down && docker-compose up -d` to restart**
5. **Check `docker ps` to verify containers are running**
6. **Open http://localhost:8000/docs for interactive API testing**

---

## 🆘 Still Not Working?

1. **Restart Docker Desktop**
2. **Restart Computer**
3. **Update Docker Desktop** (download latest from docker.com)
4. **Check Windows version** (Docker requires Windows 10/11 Pro/Enterprise)
5. **Enable WSL 2** (required for Docker Desktop)

---

## 📞 Need Help?

If Docker still doesn't work after trying everything:

1. Share the exact error message
2. Share output of: `docker info`
3. Share output of: `docker-compose logs`
4. Check Docker Desktop settings → Troubleshoot → Reset to factory defaults

---

**Bottom Line:**

1. **Open Docker Desktop** ← MOST IMPORTANT
2. **Wait for it to fully start**
3. **Run: `docker-compose up -d`**
4. **Visit: http://localhost:8000/docs**

That's it! 🎉
