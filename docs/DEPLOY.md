# TimeApp Deployment Guide

## Deployment to CSC Pouta (Ubuntu Linux)

This guide covers deploying TimeApp to a CSC Pouta Ubuntu virtual machine.

## Prerequisites

- CSC Pouta account with Ubuntu 22.04 LTS VM
- SSH access to the VM
- Domain name (optional, but recommended)

## Quick Deployment

### 1. Initial Server Setup

```bash
# SSH into your CSC Pouta VM
ssh ubuntu@your-vm-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Set hostname (optional)
sudo hostnamectl set-hostname timeapp
```

### 2. Deploy TimeApp

```bash
# Clone the repository
git clone https://github.com/yourusername/timeapp.git
cd timeapp

# Make deploy script executable
chmod +x infra/deploy.sh.example
cp infra/deploy.sh.example infra/deploy.sh

# Run deployment script
sudo ./infra/deploy.sh
```

### 3. Configure Application

```bash
# Edit systemd service with production settings
sudo nano /etc/systemd/system/timeapp.service

# Change these values:
# - SECRET_KEY: Generate with: python3 -c "import secrets; print(secrets.token_hex(32))"
# - DATABASE_URL: postgresql://timeapp:YOUR_PASSWORD@localhost/timeapp
```

### 4. Configure Nginx

```bash
# Edit nginx configuration
sudo nano /etc/nginx/sites-available/timeapp

# Replace 'your-domain.com' with your actual domain
# Or use your VM's IP address for testing

# Test nginx configuration
sudo nginx -t

# Restart services
sudo systemctl restart timeapp
sudo systemctl restart nginx
```

### 5. Setup SSL (Recommended)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

## Manual Deployment Steps

If you prefer manual deployment or need to troubleshoot:

### 1. Install Dependencies

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv \
    postgresql postgresql-contrib nginx git
```

### 2. Create Application User

```bash
sudo useradd -r -s /bin/bash -d /opt/timeapp -m timeapp
```

### 3. Setup PostgreSQL

```bash
# Switch to postgres user
sudo -u postgres psql

# In PostgreSQL shell:
CREATE USER timeapp WITH PASSWORD 'secure_password_here';
CREATE DATABASE timeapp OWNER timeapp;
GRANT ALL PRIVILEGES ON DATABASE timeapp TO timeapp;
\q
```

### 4. Setup Application

```bash
# Create application directory
sudo mkdir -p /opt/timeapp
sudo chown timeapp:timeapp /opt/timeapp

# Clone repository
sudo -u timeapp git clone https://github.com/yourusername/timeapp.git /opt/timeapp
cd /opt/timeapp

# Create virtual environment
sudo -u timeapp python3 -m venv venv

# Install dependencies
sudo -u timeapp venv/bin/pip install --upgrade pip
sudo -u timeapp venv/bin/pip install -r requirements.txt
```

### 5. Configure Systemd Service

```bash
# Copy service file
sudo cp infra/timeapp.service.example /etc/systemd/system/timeapp.service

# Edit configuration
sudo nano /etc/systemd/system/timeapp.service

# Create log directory
sudo mkdir -p /var/log/timeapp
sudo chown timeapp:timeapp /var/log/timeapp

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable timeapp
sudo systemctl start timeapp
```

### 6. Configure Nginx

```bash
# Copy nginx configuration
sudo cp infra/nginx.timeapp.conf.example /etc/nginx/sites-available/timeapp

# Edit configuration
sudo nano /etc/nginx/sites-available/timeapp

# Enable site
sudo ln -s /etc/nginx/sites-available/timeapp /etc/nginx/sites-enabled/

# Remove default site (optional)
sudo rm /etc/nginx/sites-enabled/default

# Test and restart
sudo nginx -t
sudo systemctl restart nginx
```

### 7. Configure Firewall

```bash
# Allow web traffic
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH

# Enable firewall
sudo ufw enable
```

## Backup Setup (Optional)

```bash
# Create backup directory
sudo mkdir -p /opt/timeapp/backups
sudo chown timeapp:timeapp /opt/timeapp/backups

# Copy backup scripts
sudo cp infra/backup_pg.sh.example /opt/timeapp/infra/backup_pg.sh
sudo chmod +x /opt/timeapp/infra/backup_pg.sh

# Install systemd timer
sudo cp infra/backup_pg.service.example /etc/systemd/system/backup_pg.service
sudo cp infra/backup_pg.timer.example /etc/systemd/system/backup_pg.timer

# Enable backup timer
sudo systemctl daemon-reload
sudo systemctl enable backup_pg.timer
sudo systemctl start backup_pg.timer

# Check timer status
sudo systemctl list-timers backup_pg.timer
```

## Monitoring and Maintenance

### Check Application Status

```bash
# Service status
sudo systemctl status timeapp

# View logs
sudo journalctl -u timeapp -f

# View nginx logs
sudo tail -f /var/log/nginx/timeapp_access.log
sudo tail -f /var/log/nginx/timeapp_error.log

# View application logs
sudo tail -f /var/log/timeapp/error.log
```

### Update Application

```bash
# Pull latest changes
cd /opt/timeapp
sudo -u timeapp git pull

# Update dependencies
sudo -u timeapp venv/bin/pip install -r requirements.txt

# Restart service
sudo systemctl restart timeapp
```

### Database Backup and Restore

```bash
# Manual backup
sudo -u timeapp pg_dump timeapp | gzip > /opt/timeapp/backups/manual_backup_$(date +%Y%m%d).sql.gz

# Restore from backup
gunzip < backup_file.sql.gz | sudo -u postgres psql timeapp
```

## Troubleshooting

### Application won't start

```bash
# Check logs
sudo journalctl -u timeapp -n 50

# Check configuration
sudo systemctl cat timeapp

# Test manually
cd /opt/timeapp
sudo -u timeapp venv/bin/python -m timeapp.app
```

### Nginx errors

```bash
# Test configuration
sudo nginx -t

# Check error logs
sudo tail -f /var/log/nginx/error.log
```

### Database connection issues

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Test connection
sudo -u timeapp psql -d timeapp

# Check pg_hba.conf
sudo nano /etc/postgresql/14/main/pg_hba.conf
```

## Security Recommendations

1. **Change default passwords** in systemd service file
2. **Use environment variables** for sensitive data
3. **Enable SSL/TLS** with Let's Encrypt
4. **Keep system updated**: `sudo apt update && sudo apt upgrade`
5. **Monitor logs** regularly
6. **Setup automated backups**
7. **Use SSH keys** instead of password authentication
8. **Configure fail2ban** to prevent brute force attacks

## CSC Pouta Specific Notes

- Ensure security groups allow HTTP (80) and HTTPS (443)
- Configure floating IP for stable external access
- Consider using CSC object storage for backups
- Monitor resource usage in CSC Pouta dashboard

## Support

For issues related to:
- **Application**: Check GitHub issues or contact course instructor
- **CSC Pouta**: https://docs.csc.fi/cloud/pouta/
- **Flask**: https://flask.palletsprojects.com/
