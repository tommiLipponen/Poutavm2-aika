#!/usr/bin/env python3
"""
MQTT to PostgreSQL Logger
Subscribes to MQTT chat messages and saves them to PostgreSQL database
Run as systemd service: mqtt-logger.service
"""
import json
import logging
import sys
import os
from datetime import datetime
from typing import Optional, Any
import paho.mqtt.client as mqtt  # type: ignore
import psycopg2
from psycopg2 import pool  # type: ignore
import time

# Configuration
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "chat/messages"

# Database configuration from environment
DB_URL = os.environ.get('DATABASE_URL', 'postgresql://lempuser:StrongPassword@localhost/lempdb')

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/var/log/timeapp/mqtt_logger.log', mode='a') if os.path.exists('/var/log/timeapp') else logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Database connection pool
db_pool: Optional[Any] = None

def init_db_pool():
    """Initialize database connection pool"""
    global db_pool
    try:
        db_pool = psycopg2.pool.SimpleConnectionPool(  # type: ignore
            1, 10,  # min and max connections
            DB_URL
        )
        logger.info("Database connection pool initialized")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize database pool: {e}")
        return False

def save_message(nickname, message, client_id):
    """Save MQTT message to PostgreSQL database with retry logic"""
    # Input validation
    if not nickname or not message:
        logger.warning("Empty nickname or message, skipping")
        return False
    
    # Enforce length limits
    nickname = str(nickname)[:50]  # Max 50 chars
    message = str(message)[:500]   # Max 500 chars
    client_id = str(client_id)[:100] if client_id else 'unknown'
    
    # Strip whitespace
    nickname = nickname.strip()
    message = message.strip()
    
    if not nickname or not message:
        logger.warning("Empty nickname or message after stripping, skipping")
        return False
    
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        conn = None
        try:
            conn = db_pool.getconn()  # type: ignore
            cursor = conn.cursor()
            
            query = '''
                INSERT INTO mqtt_messages (nickname, message, client_id)
                VALUES (%s, %s, %s)
            '''
            cursor.execute(query, (nickname, message, client_id))
            conn.commit()
            cursor.close()
            db_pool.putconn(conn)  # type: ignore
            
            logger.info(f"Saved: [{nickname}] {message[:50]}...")
            return True
            
        except psycopg2.Error as e:
            logger.error(f"Database error (attempt {attempt+1}/{max_retries}): {e}")
            if conn:
                try:
                    conn.rollback()
                    db_pool.putconn(conn)  # type: ignore
                except:
                    pass
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            return False
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            if conn:
                try:
                    db_pool.putconn(conn)  # type: ignore
                except:
                    pass
            return False
    
    return False

def on_connect(client, userdata, flags, rc):
    """MQTT connection callback"""
    if rc == 0:
        logger.info(f"Connected to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
        client.subscribe(MQTT_TOPIC)
        logger.info(f"Subscribed to topic: {MQTT_TOPIC}")
    else:
        logger.error(f"MQTT connection failed with code: {rc}")

def on_message(client, userdata, msg):
    """MQTT message callback"""
    try:
        payload = msg.payload.decode('utf-8')
        data = json.loads(payload)
        
        nickname = data.get('nickname', 'Unknown')[:50]
        message = data.get('text', '')
        client_id = data.get('clientId', '')[:100]
        
        if message:
            save_message(nickname, message, client_id)
        else:
            logger.warning("Received message with empty text")
            
    except json.JSONDecodeError:
        logger.warning(f"Invalid JSON: {msg.payload}")
    except Exception as e:
        logger.error(f"Error processing message: {e}")

def on_disconnect(client, userdata, rc):
    """MQTT disconnect callback"""
    if rc != 0:
        logger.warning(f"Unexpected disconnection from MQTT broker (code: {rc})")
        logger.info("Attempting to reconnect...")

def main():
    """Main function"""
    logger.info("MQTT Logger starting...")
    
    # Initialize database pool
    if not init_db_pool():
        logger.error("Cannot start without database connection")
        sys.exit(1)
    
    # Test database connection
    try:
        conn = db_pool.getconn()  # type: ignore
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM mqtt_messages")
        count = cursor.fetchone()[0]
        logger.info(f"Database OK - {count} messages in history")
        cursor.close()
        db_pool.putconn(conn)  # type: ignore
    except Exception as e:
        logger.error(f"Database test failed: {e}")
        sys.exit(1)
    
    # Setup MQTT client
    client = mqtt.Client(client_id="mqtt_logger", clean_session=False)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    
    # Connect with retry
    max_retries = 5
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Connecting to MQTT broker (attempt {attempt+1}/{max_retries})...")
            client.connect(MQTT_BROKER, MQTT_PORT, 60)
            break
        except Exception as e:
            logger.error(f"MQTT connection failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                logger.error("Failed to connect to MQTT broker after all retries")
                sys.exit(1)
    
    # Start MQTT loop
    try:
        logger.info("MQTT Logger running - Press Ctrl+C to stop")
        client.loop_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        client.disconnect()
        if db_pool:
            db_pool.closeall()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
