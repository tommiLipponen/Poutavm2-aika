#!/bin/bash
# Kubernetes LEMP Application - Initial Setup Script
# Run this once to install Minikube and kubectl

set -e  # Exit on error

echo "==================================="
echo "Kubernetes Setup - Installing Tools"
echo "==================================="

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
   echo "Please run as normal user (not root)"
   exit 1
fi

echo ""
echo "Step 1: Installing kubectl..."
if command -v kubectl &> /dev/null; then
    echo "✓ kubectl already installed"
    kubectl version --client
else
    curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
    sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
    rm kubectl
    echo "✓ kubectl installed"
    kubectl version --client
fi

echo ""
echo "Step 2: Installing Minikube..."
if command -v minikube &> /dev/null; then
    echo "✓ Minikube already installed"
    minikube version
else
    curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
    sudo install minikube-linux-amd64 /usr/local/bin/minikube
    rm minikube-linux-amd64
    echo "✓ Minikube installed"
    minikube version
fi

echo ""
echo "Step 3: Starting Minikube..."
if minikube status &> /dev/null; then
    echo "✓ Minikube already running"
else
    minikube start --driver=docker
    echo "✓ Minikube started"
fi

echo ""
echo "Step 4: Verifying Kubernetes cluster..."
kubectl get nodes

echo ""
echo "Step 5: Configuring PostgreSQL for Docker network access..."
echo ""
echo "Please edit the following files manually:"
echo ""
echo "1. Edit /etc/postgresql/16/main/pg_hba.conf"
echo "   sudo nano /etc/postgresql/16/main/pg_hba.conf"
echo "   Add this line at the end:"
echo "   host    lempdb          lempuser        172.17.0.0/16           md5"
echo ""
echo "2. Edit /etc/postgresql/16/main/postgresql.conf"
echo "   sudo nano /etc/postgresql/16/main/postgresql.conf"
echo "   Change:"
echo "   #listen_addresses = 'localhost'"
echo "   to:"
echo "   listen_addresses = '*'"
echo ""
echo "3. Restart PostgreSQL:"
echo "   sudo systemctl restart postgresql"
echo ""

read -p "Have you configured PostgreSQL? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Please configure PostgreSQL before proceeding with deployment."
    exit 1
fi

echo ""
echo "==================================="
echo "✓ Setup Complete!"
echo "==================================="
echo ""
echo "Next steps:"
echo "1. Edit kube/k8s/backend-secret.yaml with your database password"
echo "2. Run: ./kube/deploy.sh"
echo ""
