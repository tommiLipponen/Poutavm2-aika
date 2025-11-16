# TimeApp Deployment Guide

This guide covers deploying TimeApp to a production Ubuntu server with PostgreSQL, Nginx, and systemd.

## Prerequisites

- Ubuntu 20.04 or later
- Root access or sudo privileges
- PostgreSQL database with Chinook data (optional)
- Domain name or server IP address

## Quick Deployment

The deployment script automates the entire process:

```bash
# Clone the repository
git clone https://github.com/tommiLipponen/Poutavm2-aika.git
cd Poutavm2-aika

# Install dos2unix for Windows/Linux compatibility
sudo apt update
sudo apt install -y dos2unix

# Fix line endings and make scripts executable
dos2unix infra/deploy.sh
dos2unix infra/update.sh
chmod +x infra/deploy.sh
chmod +x infra/update.sh

# Run deployment
sudo ./infra/deploy.sh
```

During deployment, you'll be prompted for:
1. **PostgreSQL password**: Password for `lempuser` database user
2. **Domain name**: Your domain or press Enter to use server IP
3. **Automated backups**: Type `y` to enable daily database backups

## Updating the Application

To update a deployed application, run the update script from your repository:

```bash
cd ~/Poutavm2-aika
git pull
dos2unix infra/update.sh
sudo ./infra/update.sh
```

Or update manually:

```bash
cd ~/Poutavm2-aika
git pull
sudo rsync -av --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' --exclude='.venv' --exclude='.env' ./ /opt/timeapp/
sudo chown -R timeapp:timeapp /opt/timeapp
sudo -u timeapp /opt/timeapp/venv/bin/pip install -r /opt/timeapp/requirements.txt
sudo systemctl restart timeapp
```

## Manual Deployment Steps

If you prefer manual deployment or need to customize the process:

### 1. System Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install system dependencies
sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx git dos2unix
```

### 2. Create Application User

```bash
sudo useradd -r -s /bin/bash -d /opt/timeapp -m timeapp
```

### 3. Setup Application Directory

```bash
# Clone repository to temporary location
cd ~
git clone https://github.com/tommiLipponen/Poutavm2-aika.git
cd Poutavm2-aika

# Copy to application directory
sudo rsync -av --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' --exclude='.venv' ./ /opt/timeapp/
sudo chown -R timeapp:timeapp /opt/timeapp

# Create log directory
sudo mkdir -p /var/log/timeapp
sudo chown -R timeapp:timeapp /var/log/timeapp
```

### 4. Setup Python Environment

```bash
# Create virtual environment
sudo -u timeapp python3 -m venv /opt/timeapp/venv

# Install dependencies
sudo -u timeapp /opt/timeapp/venv/bin/pip install --upgrade pip
sudo -u timeapp /opt/timeapp/venv/bin/pip install -r /opt/timeapp/requirements.txt
```

### 5. Configure PostgreSQL

```bash
# Create database user
sudo -u postgres psql -c "CREATE USER lempuser WITH PASSWORD 'StrongPassword';"

# Create database
sudo -u postgres psql -c "CREATE DATABASE lempdb OWNER lempuser;"

# Grant privileges
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE lempdb TO lempuser;"

# Configure authentication
echo "host    lempdb          lempuser        127.0.0.1/32            md5" | sudo tee -a /etc/postgresql/$(ls /etc/postgresql | head -1)/main/pg_hba.conf
sudo systemctl reload postgresql
```

### 6. Create Environment File

```bash
sudo tee /opt/timeapp/.env > /dev/null <<EOF
DATABASE_URL=postgresql://lempuser:StrongPassword@localhost/lempdb
SECRET_KEY=$(openssl rand -hex 32)
FLASK_ENV=production
EOF
sudo chown timeapp:timeapp /opt/timeapp/.env
sudo chmod 600 /opt/timeapp/.env
```

### 7. Configure systemd Service

```bash
sudo tee /etc/systemd/system/timeapp.service > /dev/null <<EOF
[Unit]
Description=TimeApp Gunicorn Service
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=notify
User=timeapp
Group=timeapp
WorkingDirectory=/opt/timeapp
Environment="PATH=/opt/timeapp/venv/bin"
EnvironmentFile=/opt/timeapp/.env
ExecStart=/opt/timeapp/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:8000 --access-logfile /var/log/timeapp/access.log --error-logfile /var/log/timeapp/error.log 'timeapp:create_app()'
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable timeapp
sudo systemctl start timeapp
```

### 8. Configure Nginx

```bash
sudo tee /etc/nginx/sites-available/timeapp > /dev/null <<EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static {
        alias /opt/timeapp/timeapp/static;
        expires 30d;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/timeapp /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

### 9. Setup Database Backups (Optional)

```bash
# Create backup directory
sudo mkdir -p /var/backups/postgresql
sudo chown postgres:postgres /var/backups/postgresql

# Create backup script
sudo tee /usr/local/bin/backup_pg.sh > /dev/null <<'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/postgresql"
DB_NAME="lempdb"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/${DB_NAME}_${TIMESTAMP}.sql.gz"

sudo -u postgres pg_dump "$DB_NAME" | gzip > "$BACKUP_FILE"
find "$BACKUP_DIR" -name "${DB_NAME}_*.sql.gz" -mtime +7 -delete
echo "Backup completed: $BACKUP_FILE"
EOF
sudo chmod +x /usr/local/bin/backup_pg.sh

# Create systemd timer
sudo tee /etc/systemd/system/backup_pg.service > /dev/null <<EOF
[Unit]
Description=PostgreSQL Database Backup
After=postgresql.service

[Service]
Type=oneshot
ExecStart=/usr/local/bin/backup_pg.sh
EOF

sudo tee /etc/systemd/system/backup_pg.timer > /dev/null <<EOF
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

sudo systemctl daemon-reload
sudo systemctl enable backup_pg.timer
sudo systemctl start backup_pg.timer
```

## Common Issues and Solutions

### 1. `/bin/bash^M: bad interpreter` Error

**Cause**: CRLF line endings from Windows

**Solution**:
```bash
sudo apt install -y dos2unix
dos2unix infra/deploy.sh
dos2unix infra/update.sh
chmod +x infra/deploy.sh infra/update.sh
sudo ./infra/deploy.sh
```

### 2. `pathspec 'main' did not match` Error

**Cause**: Repository uses `master` branch, not `main`

**Solution**: The improved deploy.sh script auto-detects the current branch. If you see this error with old scripts:
```bash
git branch --show-current  # Check current branch
# Update BRANCH variable in script to match
```

### 3. `dubious ownership in repository` Warning

**Cause**: Git ownership mismatch

**Solution**:
```bash
sudo git config --system --add safe.directory /opt/timeapp
```

### 4. Script runs but nothing happens

**Cause**: Running from wrong directory or using .example files

**Solution**:
```bash
# Always run from repository root
cd ~/Poutavm2-aika
sudo ./infra/deploy.sh  # Not deploy.sh.example

# Verify you're in the right place
ls timeapp/app.py  # Should exist
```

### 5. Service fails to start

**Cause**: Various - check logs for details

**Solution**:
```bash
sudo journalctl -u timeapp -n 50 --no-pager
sudo systemctl status timeapp
# Check if port 8000 is already in use
sudo lsof -i :8000
```

### 6. Database connection errors

**Cause**: PostgreSQL not running or wrong credentials

**Solution**:
```bash
sudo systemctl status postgresql
# Test connection
psql -U lempuser -d lempdb -h localhost
# Check pg_hba.conf
sudo cat /etc/postgresql/*/main/pg_hba.conf | grep lempdb
```

### 7. Permission issues

**Cause**: Wrong file ownership

**Solution**:
```bash
sudo chown -R timeapp:timeapp /opt/timeapp
sudo chown -R timeapp:timeapp /var/log/timeapp
sudo chmod 600 /opt/timeapp/.env
```

### 8. `fatal: destination path '/opt/timeapp' already exists`

**Cause**: Running deploy.sh multiple times

**Solution**: The improved deploy.sh is idempotent and handles this automatically. With old scripts:
```bash
# Remove and redeploy
sudo systemctl stop timeapp
sudo rm -rf /opt/timeapp
sudo ./infra/deploy.sh
```

### 9. Nginx shows 502 Bad Gateway

**Cause**: Gunicorn not running or wrong port

**Solution**:
```bash
sudo systemctl status timeapp
# Check if Gunicorn is listening on port 8000
sudo netstat -tlnp | grep 8000
# Restart services
sudo systemctl restart timeapp
sudo systemctl restart nginx
```

### 10. Changes not appearing after update

**Cause**: Old files cached or service not restarted

**Solution**:
```bash
# Clear browser cache or use incognito mode
# Verify files were updated
ls -la /opt/timeapp/timeapp/
# Force restart
sudo systemctl restart timeapp
sudo systemctl restart nginx
```

## Monitoring and Maintenance

### View Logs

```bash
# Follow live application logs
sudo journalctl -u timeapp -f

# View recent errors
sudo journalctl -u timeapp -n 100 --no-pager

# View access logs
sudo tail -f /var/log/timeapp/access.log

# View error logs
sudo tail -f /var/log/timeapp/error.log
```

### Service Management

```bash
# Check service status
sudo systemctl status timeapp

# Restart service
sudo systemctl restart timeapp

# Stop service
sudo systemctl stop timeapp

# Start service
sudo systemctl start timeapp

# View service configuration
systemctl cat timeapp
```

### Database Management

```bash
# Connect to database
psql -U lempuser -d lempdb -h localhost

# List databases
sudo -u postgres psql -l

# Backup database manually
sudo -u postgres pg_dump lempdb > backup.sql

# Restore database
sudo -u postgres psql lempdb < backup.sql

# Check backup status
sudo systemctl status backup_pg.timer
sudo systemctl list-timers backup_pg.timer
```

### Performance Monitoring

```bash
# Check resource usage
htop

# Check disk usage
df -h

# Check memory usage
free -h

# Check active connections
sudo netstat -tlnp | grep -E ':(80|8000|5432)'

# Check Gunicorn workers
ps aux | grep gunicorn
```

## Security Recommendations

1. **Firewall Configuration**:
   ```bash
   sudo ufw allow 22/tcp  # SSH
   sudo ufw allow 80/tcp  # HTTP
   sudo ufw allow 443/tcp # HTTPS
   sudo ufw enable
   ```

2. **SSL/TLS Setup** (if you have a domain):
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d yourdomain.com
   ```

3. **Regular Updates**:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

4. **Secure Database Password**: Use strong, unique password for PostgreSQL

5. **Environment Variables**: Never commit `.env` file to version control

## URLs and Endpoints

After deployment, your application will be available at:

- **Homepage**: `http://your-server-ip/`
- **Analytics Dashboard**: `http://your-server-ip/data-analysis/`
- **Time API** (JSON): `http://your-server-ip/time/api`

Example: `http://86.50.23.0/data-analysis/`

## Support

For issues or questions:
1. Check the logs: `sudo journalctl -u timeapp -n 50`
2. Review common issues section above
3. Check GitHub repository issues
4. Contact system administrator

## Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [systemd Documentation](https://www.freedesktop.org/software/systemd/man/)
