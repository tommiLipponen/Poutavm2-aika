#!/bin/bash
# Kubernetes LEMP Application - Cleanup Script
# Removes all Kubernetes resources

set -e

echo "========================================="
echo "Kubernetes LEMP - Cleanup"
echo "========================================="

RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo -e "${YELLOW}Warning: This will delete all Kubernetes resources${NC}"
read -p "Are you sure? (y/n) " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cleanup cancelled"
    exit 0
fi

echo ""
echo "Deleting Kubernetes resources..."
kubectl delete -f kube/k8s/ --ignore-not-found=true

echo ""
echo "Remaining resources:"
kubectl get all

echo ""
echo -e "${RED}Note: Minikube is still running${NC}"
echo "To stop Minikube: minikube stop"
echo "To delete Minikube: minikube delete"
echo ""
