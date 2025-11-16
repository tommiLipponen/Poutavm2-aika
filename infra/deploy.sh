#!/bin/bash
# Deployment script for TimeApp
# Usage: sudo ./infra/deploy.sh (run from repository directory)

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
echo "TimeApp Deployment Script"
echo "========================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Error: Please run as root (use sudo)"
    exit 1
fi

# Check if running from repository directory
if [ ! -f "timeapp/app.py" ]; then
    echo "Error: Please run this script from the repository directory"
    echo "Usage: cd /path/to/Poutavm2-aika && sudo ./infra/deploy.sh"
    exit 1
fi

# Install dos2unix for line ending conversion
if ! command -v dos2unix &> /dev/null; then
    echo "Installing dos2unix..."
    apt-get update
    apt-get install -y dos2unix
fi

# Create application user if doesn't exist
if ! id "$APP_USER" &>/dev/null; then
    echo "Creating user $APP_USER..."
    useradd -r -s /bin/bash -d "$APP_DIR" -m "$APP_USER"
else
    echo "✓ User $APP_USER already exists"
fi

# Install system dependencies
echo "Installing system dependencies..."
apt-get update
apt-get install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx git

# Setup application directory
echo "Setting up application directory..."
if [ ! -d "$APP_DIR" ]; then
    mkdir -p "$APP_DIR"
    echo "Created $APP_DIR"
else
    echo "✓ $APP_DIR already exists"
fi

if [ ! -d "/var/log/timeapp" ]; then
    mkdir -p /var/log/timeapp
    echo "Created /var/log/timeapp"
else
    echo "✓ /var/log/timeapp already exists"
fi

# Copy application files
echo "Copying application files..."
rsync -av --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' --exclude='.venv' \
    "$REPO_DIR/" "$APP_DIR/"

# Set ownership
chown -R "$APP_USER:$APP_USER" "$APP_DIR"
chown -R "$APP_USER:$APP_USER" /var/log/timeapp

# Setup Python virtual environment
echo "Setting up Python virtual environment..."
if [ ! -d "$VENV_DIR" ]; then
    sudo -u "$APP_USER" python3 -m venv "$VENV_DIR"
    echo "Created virtual environment"
else
    echo "✓ Virtual environment already exists"
fi

# Install Python dependencies
echo "Installing Python dependencies..."
sudo -u "$APP_USER" "$VENV_DIR/bin/pip" install --upgrade pip
sudo -u "$APP_USER" "$VENV_DIR/bin/pip" install -r "$APP_DIR/requirements.txt"

# Configure PostgreSQL
echo ""
echo "========================================="
echo "PostgreSQL Configuration"
echo "========================================="
read -p "Enter password for lempuser: " db_password

# Check if user exists
if sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='lempuser'" | grep -q 1; then
    echo "✓ Database user lempuser already exists"
else
    echo "Creating database user..."
    sudo -u postgres psql -c "CREATE USER lempuser WITH PASSWORD '$db_password';"
fi

# Check if database exists
if sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='lempdb'" | grep -q 1; then
    echo "✓ Database lempdb already exists"
else
    echo "Creating database..."
    sudo -u postgres psql -c "CREATE DATABASE lempdb OWNER lempuser;"
fi

# Grant privileges
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE lempdb TO lempuser;"

# Configure PostgreSQL to allow password authentication
PG_HBA="/etc/postgresql/$(ls /etc/postgresql | head -1)/main/pg_hba.conf"
if ! grep -q "host.*lempdb.*lempuser.*127.0.0.1/32.*md5" "$PG_HBA"; then
    echo "Configuring PostgreSQL authentication..."
    echo "host    lempdb          lempuser        127.0.0.1/32            md5" >> "$PG_HBA"
    systemctl reload postgresql
else
    echo "✓ PostgreSQL authentication already configured"
fi

# Create environment file
echo "Creating environment configuration..."
cat > "$APP_DIR/.env" <<EOF
DATABASE_URL=postgresql://lempuser:$db_password@localhost/lempdb
SECRET_KEY=$(openssl rand -hex 32)
FLASK_ENV=production
EOF
chown "$APP_USER:$APP_USER" "$APP_DIR/.env"
chmod 600 "$APP_DIR/.env"

# Setup systemd service
echo "Setting up systemd service..."
cat > /etc/systemd/system/timeapp.service <<EOF
[Unit]
Description=TimeApp Gunicorn Service
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=notify
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_DIR
Environment="PATH=$VENV_DIR/bin"
EnvironmentFile=$APP_DIR/.env
ExecStart=$VENV_DIR/bin/gunicorn --workers 4 --bind 127.0.0.1:8000 --access-logfile /var/log/timeapp/access.log --error-logfile /var/log/timeapp/error.log 'timeapp:create_app()'
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

# Setup Nginx
echo "Setting up Nginx..."
read -p "Enter your domain name (or press Enter to use server IP): " domain_name
if [ -z "$domain_name" ]; then
    domain_name="_"
fi

cat > /etc/nginx/sites-available/timeapp <<EOF
server {
    listen 80;
    server_name $domain_name;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static {
        alias $APP_DIR/timeapp/static;
        expires 30d;
    }
}
EOF

# Enable Nginx site
if [ ! -L /etc/nginx/sites-enabled/timeapp ]; then
    ln -s /etc/nginx/sites-available/timeapp /etc/nginx/sites-enabled/
    echo "Enabled Nginx site"
else
    echo "✓ Nginx site already enabled"
fi

# Remove default Nginx site if exists
if [ -L /etc/nginx/sites-enabled/default ]; then
    rm /etc/nginx/sites-enabled/default
    echo "Removed default Nginx site"
fi

# Test Nginx configuration
nginx -t

# Setup database backups
echo ""
echo "========================================="
echo "Database Backup Configuration"
echo "========================================="
read -p "Setup automated database backups for lempdb? (y/n): " setup_backups

if [ "$setup_backups" = "y" ]; then
    BACKUP_DIR="/var/backups/postgresql"
    mkdir -p "$BACKUP_DIR"
    chown postgres:postgres "$BACKUP_DIR"

    # Create backup script
    cat > /usr/local/bin/backup_pg.sh <<'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/postgresql"
DB_NAME="lempdb"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/${DB_NAME}_${TIMESTAMP}.sql.gz"

# Create backup
sudo -u postgres pg_dump "$DB_NAME" | gzip > "$BACKUP_FILE"

# Keep only last 7 days of backups
find "$BACKUP_DIR" -name "${DB_NAME}_*.sql.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_FILE"
EOF
    chmod +x /usr/local/bin/backup_pg.sh

    # Create systemd service for backup
    cat > /etc/systemd/system/backup_pg.service <<EOF
[Unit]
Description=PostgreSQL Database Backup
After=postgresql.service

[Service]
Type=oneshot
ExecStart=/usr/local/bin/backup_pg.sh
EOF

    # Create systemd timer for daily backups
    cat > /etc/systemd/system/backup_pg.timer <<EOF
[Unit]
Description=Daily PostgreSQL Backup
Requires=backup_pg.service

[Timer]
OnCalendar=daily
OnCalendar=02:00
Persistent=true

[Install]
WantedBy=timers.target
EOF

    systemctl daemon-reload
    systemctl enable backup_pg.timer
    systemctl start backup_pg.timer
    echo "✓ Database backups configured (daily at 02:00)"
fi

# Start services
echo ""
echo "========================================="
echo "Starting Services"
echo "========================================="
systemctl daemon-reload
systemctl enable timeapp
systemctl restart timeapp
systemctl restart nginx

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

if systemctl is-active --quiet nginx; then
    echo "✓ Nginx is running"
else
    echo "✗ Nginx failed to start"
    systemctl status nginx --no-pager
    exit 1
fi

echo ""
echo "========================================="
echo "Deployment Complete!"
echo "========================================="
echo "Application URL: http://$(hostname -I | awk '{print $1}')/"
echo "Analytics URL: http://$(hostname -I | awk '{print $1}')/data-analysis/"
echo ""
echo "Service commands:"
echo "  sudo systemctl status timeapp   - Check service status"
echo "  sudo systemctl restart timeapp  - Restart application"
echo "  sudo journalctl -u timeapp -f   - View live logs"
echo ""
echo "Logs location:"
echo "  /var/log/timeapp/access.log"
echo "  /var/log/timeapp/error.log"
echo ""
