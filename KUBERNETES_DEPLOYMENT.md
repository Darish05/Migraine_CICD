# Kubernetes Deployment Guide

## ⚠️ RUN THIS ONLY AFTER DOCKER WORKS LOCALLY!

---

## Prerequisites Checklist

Before running deployment.yaml, ensure:

- [x] Docker image built successfully
- [x] Docker containers running locally
- [x] API tested at http://localhost:8000
- [ ] Kubernetes cluster running (minikube/kind/cloud)
- [ ] kubectl installed and configured
- [ ] Docker image pushed to registry (if using cloud K8s)

---

## Step 1: Verify Kubernetes is Ready

```bash
# Check kubectl is installed
kubectl version --client

# Check cluster connection
kubectl cluster-info

# Check nodes are ready
kubectl get nodes
```

---

## Step 2: (Optional) Push Image to Docker Hub

If using cloud Kubernetes, push your image:

```bash
# Login to Docker Hub
docker login

# Tag your image
docker tag migraine-ml-api:latest darish05/migraine-ml:latest

# Push to registry
docker push darish05/migraine-ml:latest
```

---

## Step 3: Deploy to Kubernetes

```bash
# Apply the deployment
kubectl apply -f kubernetes/deployment.yaml

# This creates:
# - Namespace: migraine-ml
# - ConfigMaps and Secrets
# - Persistent Volume Claims
# - Deployments (API + MLflow)
# - Services (LoadBalancer)
# - Horizontal Pod Autoscaler
# - Ingress
# - Network Policies
```

---

## Step 4: Check Deployment Status

```bash
# Check all resources
kubectl get all -n migraine-ml

# Check pods are running
kubectl get pods -n migraine-ml

# Check services
kubectl get svc -n migraine-ml

# View pod logs
kubectl logs -n migraine-ml -l app=migraine-api --tail=100

# Describe pod for issues
kubectl describe pod -n migraine-ml <pod-name>
```

---

## Step 5: Access Your API

### Option A: Using LoadBalancer (Cloud K8s)

```bash
# Get external IP
kubectl get svc migraine-api-service -n migraine-ml

# Access at: http://<EXTERNAL-IP>:8000
```

### Option B: Using Port Forward (Local K8s)

```bash
# Forward port 8000
kubectl port-forward -n migraine-ml svc/migraine-api-service 8000:8000

# Access at: http://localhost:8000
```

### Option C: Using NodePort (Minikube)

```bash
# Get URL
minikube service migraine-api-service -n migraine-ml --url
```

---

## Step 6: Test the API

```bash
# Health check
curl http://localhost:8000/health

# Make prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "age": 35,
    "duration": 120,
    "frequency": 5,
    "location": "Forehead",
    "character": "Pulsating",
    "intensity": 7,
    "nausea": 1,
    "vomit": 0,
    "phonophobia": 1,
    "photophobia": 1,
    "visual": 1,
    "sensory": 0,
    "dpf": 30.5
  }'
```

---

## Troubleshooting

### Pods not starting?

```bash
# Check events
kubectl get events -n migraine-ml --sort-by='.lastTimestamp'

# Check pod details
kubectl describe pod -n migraine-ml <pod-name>

# Check logs
kubectl logs -n migraine-ml <pod-name>
```

### Image pull errors?

- Ensure image exists: `docker images | grep migraine-ml`
- For cloud K8s: Push image to Docker Hub first
- For local K8s (minikube): Load image with `minikube image load migraine-ml-api:latest`

### Persistent volume issues?

```bash
# Check PVCs
kubectl get pvc -n migraine-ml

# If using minikube, enable storage addon
minikube addons enable storage-provisioner
```

---

## Scaling

### Manual scaling:

```bash
kubectl scale deployment migraine-api -n migraine-ml --replicas=5
```

### Auto-scaling is already configured:

- Min replicas: 2
- Max replicas: 10
- CPU target: 70%
- Memory target: 80%

---

## Cleanup

```bash
# Delete all resources
kubectl delete -f kubernetes/deployment.yaml

# Or delete namespace (removes everything)
kubectl delete namespace migraine-ml
```

---

## Monitoring

### View HPA status:

```bash
kubectl get hpa -n migraine-ml
```

### View resource usage:

```bash
kubectl top pods -n migraine-ml
kubectl top nodes
```

---

## Summary: What deployment.yaml Creates

✅ **Namespace**: Isolated environment
✅ **API Deployment**: 3 replicas (scales 2-10)
✅ **MLflow Server**: Experiment tracking
✅ **Services**: LoadBalancer for external access
✅ **HPA**: Auto-scaling based on load
✅ **PVCs**: 10GB for MLflow, 5GB for models
✅ **Security**: Network policies, non-root containers
✅ **Health Checks**: Liveness & readiness probes
✅ **Ingress**: Optional external DNS access

---

## Next Steps After Deployment

1. ✅ Set up monitoring (Prometheus/Grafana)
2. ✅ Configure CI/CD pipeline
3. ✅ Set up backup for PVCs
4. ✅ Configure SSL/TLS certificates
5. ✅ Set up logging (ELK/Loki)

---

**Remember: Build and test Docker locally FIRST, then deploy to Kubernetes!**
