#!/bin/bash
# Force clear Python cache and restart TimeApp
# Run on VM: sudo bash force_restart.sh

echo "Stopping TimeApp..."
sudo systemctl stop timeapp

echo "Clearing ALL Python bytecode cache..."
sudo find /opt/timeapp -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
sudo find /opt/timeapp -type f -name '*.pyc' -delete 2>/dev/null || true
sudo find /opt/timeapp -type f -name '*.pyo' -delete 2>/dev/null || true

echo "Verifying current code version..."
if grep -q "url_prefix='/time'" /opt/timeapp/timeapp/time_endpoint.py; then
    echo "⚠️  WARNING: OLD CODE DETECTED - url_prefix='/time' found!"
    echo "Run: cd ~/Poutavm2-aika && git pull"
else
    echo "✓ Code appears up to date (no url_prefix on time_bp)"
fi

if grep -q "@time_bp.route('/time/api')" /opt/timeapp/timeapp/time_endpoint.py; then
    echo "✓ Time API route is /time/api (correct)"
elif grep -q "@time_bp.route('/api')" /opt/timeapp/timeapp/time_endpoint.py; then
    echo "⚠️  WARNING: Time API route is /api (should be /time/api)"
else
    echo "⚠️  WARNING: Could not find time API route"
fi

echo ""
echo "Starting TimeApp..."
sudo systemctl start timeapp

sleep 2

echo ""
echo "Service status:"
sudo systemctl status timeapp --no-pager -l

echo ""
echo "Testing routes with Python..."
sudo -u timeapp /opt/timeapp/venv/bin/python3 << 'PYEOF'
import sys
sys.path.insert(0, '/opt/timeapp')
from timeapp import create_app
app = create_app()
print("\nRegistered routes:")
for rule in sorted(app.url_map.iter_rules(), key=lambda r: str(r)):
    if rule.endpoint != 'static':
        print(f"  {str(rule):30} -> {rule.endpoint}")
PYEOF
