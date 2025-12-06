#!/bin/bash
# Kubernetes LEMP Application - Update Script
# Rebuilds images and restarts deployments

set -e

echo "========================================="
echo "Kubernetes LEMP - Update"
echo "========================================="

YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

echo ""
echo -e "${YELLOW}Switching to Minikube Docker environment...${NC}"
eval $(minikube docker-env)

echo ""
echo -e "${YELLOW}Rebuilding backend image...${NC}"
cd kube/backend
docker build -t kube-backend:latest .

echo ""
echo -e "${YELLOW}Rebuilding frontend image...${NC}"
cd ../frontend
docker build -t kube-frontend:latest .

echo ""
echo -e "${YELLOW}Restarting deployments...${NC}"
kubectl rollout restart deployment backend
kubectl rollout restart deployment frontend

echo ""
echo -e "${YELLOW}Waiting for rollout to complete...${NC}"
kubectl rollout status deployment backend
kubectl rollout status deployment frontend

echo ""
echo -e "${GREEN}✓ Update complete!${NC}"
echo ""

kubectl get pods

eval $(minikube docker-env -u)
