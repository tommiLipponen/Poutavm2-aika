#!/usr/bin/env python3
"""
Fetch weather data from OpenWeatherMap API and store in PostgreSQL
Run via cron every 5 minutes
"""
import os
import sys
import requests
import psycopg2
from datetime import datetime
import time

# API Configuration
API_KEY = "e0aaceac1814638ac4e1a8a974ba01df"
CITY = "Oulu"
COUNTRY_CODE = "FI"
API_URL = f"https://api.openweathermap.org/data/2.5/weather?q={CITY},{COUNTRY_CODE}&appid={API_KEY}&units=metric"

def get_db_connection():
    """Create database connection"""
    return psycopg2.connect(os.environ.get('DATABASE_URL'))

def fetch_and_store_weather():
    """Fetch weather data and store in database with retry logic"""
    max_retries = 3
    retry_delay = 2  # seconds
    
    for attempt in range(max_retries):
        conn = None
        try:
            # Fetch data from API
            response = requests.get(API_URL, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Extract relevant fields
            temperature = data['main']['temp']
            humidity = data['main']['humidity']
            pressure = data['main']['pressure']
            wind_speed = data['wind']['speed']
            description = data['weather'][0]['description']
            
            # Store in database
            conn = get_db_connection()
            cur = conn.cursor()
            
            cur.execute("""
                INSERT INTO weather_data (temperature, humidity, pressure, wind_speed, description)
                VALUES (%s, %s, %s, %s, %s)
            """, (temperature, humidity, pressure, wind_speed, description))
            
            conn.commit()
            cur.close()
            conn.close()
            
            print(f"{datetime.now().isoformat()} - Weather data stored: {temperature}°C, {wind_speed}m/s, {description}")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"{datetime.now().isoformat()} - API request failed (attempt {attempt+1}/{max_retries}): {e}", file=sys.stderr)
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            return False
        except psycopg2.Error as e:
            print(f"{datetime.now().isoformat()} - Database error: {e}", file=sys.stderr)
            if conn:
                try:
                    conn.rollback()
                    conn.close()
                except:
                    pass
            return False
        except Exception as e:
            print(f"{datetime.now().isoformat()} - Unexpected error: {e}", file=sys.stderr)
            if conn:
                try:
                    conn.close()
                except:
                    pass
        return False

if __name__ == '__main__':
    success = fetch_and_store_weather()
    sys.exit(0 if success else 1)
