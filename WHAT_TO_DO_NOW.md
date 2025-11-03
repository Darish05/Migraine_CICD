# 🚀 QUICK START GUIDE

## RIGHT NOW - Build Docker First

### ✅ Step 1: Build Docker (5-10 minutes)

Double-click this file:

```
D:\Mlops\migraine-ml\START_DOCKER.bat
```

Or run in terminal:

```bash
cd D:\Mlops\migraine-ml
docker build -t migraine-ml-api:latest .
docker-compose up -d
```

### ✅ Step 2: Test Locally

```bash
curl http://localhost:8000/health
```

---

## LATER - Deploy to Kubernetes

### ✅ Step 3: Setup Kubernetes Cluster

Choose one:

**Option A: Local (Minikube)**

```bash
minikube start
minikube image load migraine-ml-api:latest
```

**Option B: Cloud (Push to Docker Hub)**

```bash
docker tag migraine-ml-api:latest darish05/migraine-ml:latest
docker push darish05/migraine-ml:latest
```

### ✅ Step 4: Deploy

```bash
kubectl apply -f kubernetes/deployment.yaml
```

### ✅ Step 5: Access API

```bash
kubectl port-forward -n migraine-ml svc/migraine-api-service 8000:8000
```

---

## Files Created for You

| File                       | Purpose              | When to Use            |
| -------------------------- | -------------------- | ---------------------- |
| `START_DOCKER.bat`         | Build & start Docker | **NOW**                |
| `KUBERNETES_DEPLOYMENT.md` | K8s deployment guide | **AFTER Docker works** |
| `deployment.yaml`          | K8s configuration    | **AFTER Docker works** |

---

## Timeline

1. **Now (5-10 min)**: Build Docker image
2. **Now (1 min)**: Test locally
3. **Later**: Deploy to Kubernetes

---

## Current Status

- [x] Models trained (5 .pkl files)
- [x] Models moved to correct folder
- [x] Dockerfile ready
- [x] docker-compose.yml ready
- [x] deployment.yaml ready
- [ ] **Docker build** ⬅️ **DO THIS NOW**
- [ ] **K8s deployment** ⬅️ **DO THIS LATER**

---

## What to Do RIGHT NOW

1. Double-click: `START_DOCKER.bat`
2. Wait 5-10 minutes
3. Test: http://localhost:8000/health
4. ✅ Done!

**THEN** you can do Kubernetes deployment using `KUBERNETES_DEPLOYMENT.md`
