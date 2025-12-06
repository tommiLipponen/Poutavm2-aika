# Kubernetes LEMP Application

Multi-container application running on Kubernetes with:
- **Frontend**: Nginx serving static HTML
- **Backend**: Python Flask API
- **Database**: PostgreSQL (on host machine)

## Architecture

```
Internet → Host Nginx (:80) → /kube → Minikube (:30080) → Frontend Pod (Nginx)
                                                              ↓
                                                         Backend Pod (Flask)
                                                              ↓
                                                    Host PostgreSQL (:5432)
```

## Prerequisites (Already Installed ✅)

- ✅ Ubuntu 24.04 LTS
- ✅ Docker
- ✅ kubectl
- ✅ Minikube
- ✅ PostgreSQL 16 configured for Docker network access

## Deployment Steps

### 1. Configure Database Secret

Edit `k8s/backend-secret.yaml` and replace `YOUR_DB_PASSWORD_HERE` with your actual `lempuser` password:

```bash
nano kube/k8s/backend-secret.yaml
```

### 2. Build Docker Images in Minikube

Minikube has its own Docker environment. Build images inside it:

```bash
# Switch to Minikube's Docker environment
eval $(minikube docker-env)

# Build backend image
cd /opt/timeapp/kube/backend
docker build -t kube-backend:latest .

# Build frontend image
cd /opt/timeapp/kube/frontend
docker build -t kube-frontend:latest .

# Verify images exist
docker images | grep kube

# Return to normal Docker environment (optional)
eval $(minikube docker-env -u)
```

### 3. Deploy to Kubernetes

```bash
cd /opt/timeapp/kube/k8s

# Create Secret (with your DB password)
kubectl apply -f backend-secret.yaml

# Create ConfigMap
kubectl apply -f backend-configmap.yaml

# Deploy Backend
kubectl apply -f backend-deployment.yaml
kubectl apply -f backend-service.yaml

# Wait for backend to be ready
kubectl wait --for=condition=ready pod -l app=backend --timeout=120s

# Deploy Frontend
kubectl apply -f frontend-deployment.yaml
kubectl apply -f frontend-service.yaml

# Wait for frontend to be ready
kubectl wait --for=condition=ready pod -l app=frontend --timeout=60s
```

### 4. Verify Deployment

```bash
# Check all pods are running
kubectl get pods

# Check services
kubectl get services

# Check logs
kubectl logs -l app=backend --tail=50
kubectl logs -l app=frontend --tail=50

# Test backend directly
kubectl port-forward service/backend 5000:5000
# Then in another terminal: curl http://localhost:5000/api/health

# Test frontend service
kubectl port-forward service/frontend 8080:80
# Then in browser: http://localhost:8080/kube
```

### 5. Configure Host Nginx Reverse Proxy

Add this to your Nginx config (`/etc/nginx/sites-available/timeapp`):

```nginx
# Kubernetes application at /kube
location /kube/ {
    proxy_pass http://192.168.49.2:30080/kube/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;
}
```

Then reload Nginx:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

### 6. Access the Application

Open in browser: `http://86.50.23.0/kube`

## Useful Commands

### View Resources

```bash
# All resources
kubectl get all

# Pods with details
kubectl get pods -o wide

# Services
kubectl get svc

# Deployments
kubectl get deployments

# ConfigMaps and Secrets
kubectl get configmap
kubectl get secrets
```

### Logs and Debugging

```bash
# Pod logs
kubectl logs <pod-name>
kubectl logs -f <pod-name>  # Follow logs

# Logs from all pods with label
kubectl logs -l app=backend --tail=100

# Describe resource (shows events)
kubectl describe pod <pod-name>
kubectl describe deployment backend

# Execute command in pod
kubectl exec -it <pod-name> -- /bin/sh

# Test database connection from backend pod
kubectl exec -it <backend-pod-name> -- python3 -c "
import psycopg2
conn = psycopg2.connect(host='host.minikube.internal', database='lempdb', user='lempuser', password='YOUR_PASSWORD')
print('Connected!')
"
```

### Scaling

```bash
# Scale backend replicas
kubectl scale deployment backend --replicas=3

# Scale frontend replicas
kubectl scale deployment frontend --replicas=3

# Check status
kubectl get pods
```

### Updates

```bash
# After changing code, rebuild images
eval $(minikube docker-env)
cd /opt/timeapp/kube/backend
docker build -t kube-backend:latest .

# Restart deployment to use new image
kubectl rollout restart deployment backend

# Check rollout status
kubectl rollout status deployment backend

# View rollout history
kubectl rollout history deployment backend

# Rollback if needed
kubectl rollout undo deployment backend
```

### Cleanup

```bash
# Delete all resources
kubectl delete -f k8s/

# Or delete individually
kubectl delete deployment frontend backend
kubectl delete service frontend backend
kubectl delete configmap backend-config
kubectl delete secret db-secret

# Stop Minikube
minikube stop

# Delete Minikube cluster
minikube delete
```

## Troubleshooting

### Pods not starting

```bash
kubectl describe pod <pod-name>
kubectl logs <pod-name>
```

### Database connection issues

1. Check PostgreSQL is listening on all interfaces:
   ```bash
   sudo ss -tlnp | grep 5432
   # Should show 0.0.0.0:5432
   ```

2. Check pg_hba.conf allows Docker network:
   ```bash
   sudo cat /etc/postgresql/16/main/pg_hba.conf | grep 172.17
   # Should show: host lempdb lempuser 172.17.0.0/16 md5
   ```

3. Test from Minikube node:
   ```bash
   minikube ssh
   # Inside Minikube:
   nc -zv host.minikube.internal 5432
   ```

### NodePort not accessible

```bash
# Check Minikube IP
minikube ip

# Check service
kubectl get svc frontend
# Should show NodePort 30080

# Test directly
curl http://$(minikube ip):30080/kube
```

### 502 Bad Gateway from Host Nginx

1. Check Minikube is running:
   ```bash
   minikube status
   ```

2. Check frontend pods are ready:
   ```bash
   kubectl get pods -l app=frontend
   ```

3. Test NodePort directly:
   ```bash
   curl http://192.168.49.2:30080/kube
   ```

4. Check Nginx error logs:
   ```bash
   sudo tail -f /var/log/nginx/error.log
   ```

## Project Structure

```
kube/
├── backend/
│   ├── app.py              # Flask application
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile          # Backend container image
├── frontend/
│   ├── index.html         # Static web page
│   ├── nginx.conf         # Nginx configuration
│   └── Dockerfile         # Frontend container image
└── k8s/
    ├── backend-secret.yaml      # Database credentials
    ├── backend-configmap.yaml   # Backend configuration
    ├── backend-deployment.yaml  # Backend pods
    ├── backend-service.yaml     # Backend service
    ├── frontend-deployment.yaml # Frontend pods
    └── frontend-service.yaml    # Frontend service (NodePort)
```

## Key Features Demonstrated

- ✅ **Multi-container orchestration** with Kubernetes
- ✅ **Service discovery** (frontend → backend via DNS)
- ✅ **ConfigMaps** for configuration
- ✅ **Secrets** for sensitive data
- ✅ **Deployments** with multiple replicas
- ✅ **Services** (ClusterIP and NodePort)
- ✅ **Health checks** (liveness and readiness probes)
- ✅ **Resource limits** (CPU and memory)
- ✅ **Hybrid architecture** (Kubernetes pods + host PostgreSQL)
- ✅ **Reverse proxy** integration with host Nginx
