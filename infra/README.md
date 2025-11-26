# Infrastructure Files

This directory contains deployment and configuration files for the TimeApp project.

## File Patterns

### `.example` Files
Files ending with `.example` are **templates** that need to be copied and customized for deployment:

- `backup_pg.service.example` → Copy to `/etc/systemd/system/backup_pg.service`
- `backup_pg.sh.example` → Copy to actual location and customize paths
- `backup_pg.timer.example` → Copy to `/etc/systemd/system/backup_pg.timer`
- `mqtt-logger.service.example` → Copy to `/etc/systemd/system/mqtt-logger.service`

**Important:** These `.example` files are tracked in git. The actual files (without `.example`) are gitignored to prevent committing sensitive data or server-specific configurations.

### Active Deployment Files
These files are already customized for deployment and are **gitignored**:

- `deploy.sh` - Main deployment script
- `update.sh` - Application update script
- `setup_cron.sh` - Cron job installation
- `timeapp.service` - Systemd service for main app
- `nginx.timeapp.conf` - Nginx configuration

### SQL Schema Files
- `create_api_tables.sql` - Database schema for weather/solar wind data
- `create_mqtt_tables.sql` - Database schema for MQTT chat messages

## Usage

### For MQTT Logger Service:
```bash
# Copy example to systemd directory
sudo cp mqtt-logger.service.example /etc/systemd/system/mqtt-logger.service

# Reload systemd
sudo systemctl daemon-reload

# Enable and start
sudo systemctl enable mqtt-logger
sudo systemctl start mqtt-logger
```

### For Updates:
```bash
# From repository directory
cd ~/Poutavm2-aika
git pull
sudo bash infra/update.sh
```

## Notes

- All `.example` files are safe to commit to git
- Actual service/config files are in `.gitignore`
- The `update.sh` script copies everything from repo to `/opt/timeapp`
- No automatic `.example` stripping occurs - manual copy required
