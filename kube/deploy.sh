#!/bin/bash
# Kubernetes LEMP Application - Deployment Script
# Builds images and deploys to Minikube

set -e  # Exit on error

echo "========================================="
echo "Kubernetes LEMP - Deployment"
echo "========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Minikube is running
if ! minikube status &> /dev/null; then
    echo -e "${RED}Error: Minikube is not running${NC}"
    echo "Start it with: minikube start --driver=docker"
    exit 1
fi

# Check if secret has been edited
if grep -q "YOUR_DB_PASSWORD_HERE" kube/k8s/backend-secret.yaml; then
    echo -e "${RED}Error: Database password not configured${NC}"
    echo "Please edit kube/k8s/backend-secret.yaml and replace YOUR_DB_PASSWORD_HERE"
    exit 1
fi

echo ""
echo -e "${YELLOW}Step 1: Switching to Minikube Docker environment...${NC}"
eval $(minikube docker-env)
echo "✓ Using Minikube Docker"

echo ""
echo -e "${YELLOW}Step 2: Building backend image...${NC}"
cd kube/backend
docker build -t kube-backend:latest .
echo "✓ Backend image built"

echo ""
echo -e "${YELLOW}Step 3: Building frontend image...${NC}"
cd ../frontend
docker build -t kube-frontend:latest .
echo "✓ Frontend image built"

echo ""
echo -e "${YELLOW}Step 4: Verifying images...${NC}"
docker images | grep kube

echo ""
echo -e "${YELLOW}Step 5: Deploying to Kubernetes...${NC}"
cd ../k8s

# Create Secret
echo "  → Creating Secret..."
kubectl apply -f backend-secret.yaml

# Create ConfigMap
echo "  → Creating ConfigMap..."
kubectl apply -f backend-configmap.yaml

# Deploy Backend
echo "  → Deploying Backend..."
kubectl apply -f backend-deployment.yaml
kubectl apply -f backend-service.yaml

# Wait for backend
echo "  → Waiting for backend pods..."
kubectl wait --for=condition=ready pod -l app=backend --timeout=120s

# Deploy Frontend
echo "  → Deploying Frontend..."
kubectl apply -f frontend-deployment.yaml
kubectl apply -f frontend-service.yaml

# Wait for frontend
echo "  → Waiting for frontend pods..."
kubectl wait --for=condition=ready pod -l app=frontend --timeout=60s

echo ""
echo -e "${GREEN}✓ Deployment complete!${NC}"
echo ""

echo "========================================="
echo "Deployment Status:"
echo "========================================="
kubectl get pods
echo ""
kubectl get services

echo ""
echo "========================================="
echo "Access Information:"
echo "========================================="
MINIKUBE_IP=$(minikube ip)
echo "Minikube IP: $MINIKUBE_IP"
echo "NodePort: 30080"
echo ""
echo "Direct access: http://$MINIKUBE_IP:30080/kube"
echo ""
echo "Next steps:"
echo "1. Add Nginx reverse proxy configuration from infra/nginx-kube.conf"
echo "2. Reload Nginx: sudo systemctl reload nginx"
echo "3. Access via: http://86.50.23.0/kube"
echo ""

# Return to normal Docker environment
eval $(minikube docker-env -u)
