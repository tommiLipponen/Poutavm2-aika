#!/bin/bash
# Setup cron jobs for weather and solar wind data collection
# Run as: sudo bash infra/setup_cron.sh

set -e

TIMEAPP_USER="ubuntu"
PROJECT_DIR="/home/ubuntu/Poutavm2-aika"
VENV_PATH="$PROJECT_DIR/venv"
SCRIPTS_DIR="$PROJECT_DIR/scripts"
LOG_DIR="/var/log/timeapp"

# Create log directory
mkdir -p "$LOG_DIR"
chown $TIMEAPP_USER:$TIMEAPP_USER "$LOG_DIR"

# Create cron job file for timeapp user
CRON_FILE="/tmp/timeapp_cron"

# Export existing crontab (if any)
crontab -u $TIMEAPP_USER -l > "$CRON_FILE" 2>/dev/null || echo "# TimeApp Cron Jobs" > "$CRON_FILE"

# Remove old entries for these scripts (if they exist)
sed -i '/fetch_weather.py/d' "$CRON_FILE"
sed -i '/fetch_solar_wind.py/d' "$CRON_FILE"

# Add new cron jobs
echo "# Fetch weather data every 5 minutes" >> "$CRON_FILE"
echo "*/5 * * * * cd $PROJECT_DIR && DATABASE_URL=\$(cat $PROJECT_DIR/.env | grep DATABASE_URL | cut -d '=' -f2-) $VENV_PATH/bin/python3 $SCRIPTS_DIR/fetch_weather.py >> $LOG_DIR/weather.log 2>&1" >> "$CRON_FILE"

echo "# Fetch solar wind data every 5 minutes" >> "$CRON_FILE"
echo "*/5 * * * * cd $PROJECT_DIR && DATABASE_URL=\$(cat $PROJECT_DIR/.env | grep DATABASE_URL | cut -d '=' -f2-) $VENV_PATH/bin/python3 $SCRIPTS_DIR/fetch_solar_wind.py >> $LOG_DIR/solar.log 2>&1" >> "$CRON_FILE"

# Install crontab
crontab -u $TIMEAPP_USER "$CRON_FILE"

# Clean up
rm "$CRON_FILE"

echo "✅ Cron jobs installed for user $TIMEAPP_USER"
echo "Weather data: every 5 minutes -> $LOG_DIR/weather.log"
echo "Solar wind data: every 5 minutes -> $LOG_DIR/solar.log"
echo ""
echo "View crontab: sudo crontab -u $TIMEAPP_USER -l"
echo "View logs: tail -f $LOG_DIR/weather.log $LOG_DIR/solar.log"
