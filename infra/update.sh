#!/bin/bash
# Update script for TimeApp
# Usage: sudo ./infra/update.sh (run from repository directory)

# Fix CRLF line endings if present (Windows compatibility)
dos2unix "$0" 2>/dev/null || true

set -e  # Exit on error

# Configuration
APP_NAME="timeapp"
APP_USER="timeapp"
APP_DIR="/opt/timeapp"
REPO_DIR="$(pwd)"
VENV_DIR="$APP_DIR/venv"

echo "========================================="
echo "TimeApp Update Script"
echo "========================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Error: Please run as root (use sudo)"
    exit 1
fi

# Check if running from repository directory
if [ ! -f "timeapp/app.py" ]; then
    echo "Error: Please run this script from the repository directory"
    echo "Usage: cd /path/to/Poutavm2-aika && sudo ./infra/update.sh"
    exit 1
fi

# Check if application is deployed
if [ ! -d "$APP_DIR" ]; then
    echo "Error: Application not deployed. Run deploy.sh first."
    exit 1
fi

echo "Stopping application..."
systemctl stop timeapp

echo "Clearing Python bytecode cache..."
find "$APP_DIR" -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
find "$APP_DIR" -type f -name '*.pyc' -delete 2>/dev/null || true
find "$APP_DIR" -type f -name '*.pyo' -delete 2>/dev/null || true

echo "Updating application files..."
rsync -av --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' --exclude='.venv' --exclude='.env' \
    "$REPO_DIR/" "$APP_DIR/"

# Set ownership
chown -R "$APP_USER:$APP_USER" "$APP_DIR"

echo "Updating Python dependencies..."
sudo -u "$APP_USER" "$VENV_DIR/bin/pip" install --upgrade pip
sudo -u "$APP_USER" "$VENV_DIR/bin/pip" install -r "$APP_DIR/requirements.txt"

echo "Restarting application..."
systemctl start timeapp

# Wait for service to start
sleep 2

# Check service status
if systemctl is-active --quiet timeapp; then
    echo "✓ TimeApp service is running"
else
    echo "✗ TimeApp service failed to start"
    systemctl status timeapp --no-pager
    exit 1
fi

echo ""
echo "========================================="
echo "Update Complete!"
echo "========================================="
echo "Service status:"
systemctl status timeapp --no-pager -l
echo ""
echo "View logs with: sudo journalctl -u timeapp -f"
echo ""
