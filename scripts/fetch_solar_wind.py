#!/usr/bin/env python3
"""
Fetch solar wind data from NOAA Space Weather API and store in PostgreSQL
Run via cron every 5 minutes
"""
import os
import sys
import requests
import psycopg2
from datetime import datetime
import time

# NOAA DSCOVR Real-time Solar Wind API
API_URL = "https://services.swpc.noaa.gov/products/solar-wind/mag-1-day.json"

def get_db_connection():
    """Create database connection"""
    return psycopg2.connect(os.environ.get('DATABASE_URL'))

def fetch_and_store_solar_wind():
    """Fetch solar wind data and store in database with retry logic"""
    max_retries = 3
    retry_delay = 2  # seconds
    
    for attempt in range(max_retries):
        conn = None
        try:
            # Fetch data from API
            response = requests.get(API_URL, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Get the latest reading (last row, excluding header)
            if len(data) < 2:
                print(f"{datetime.now().isoformat()} - No data available", file=sys.stderr)
                return False
                
            latest = data[-1]  # Last entry
            
            # Parse fields: [time_tag, bx_gsm, by_gsm, bz_gsm, lon_gsm, lat_gsm, bt]
            # We'll store speed and density from plasma data, but mag data has bt
            bt = float(latest[6]) if latest[6] != '' else None
            
            # Get plasma data for speed and density
            plasma_url = "https://services.swpc.noaa.gov/products/solar-wind/plasma-1-day.json"
            plasma_response = requests.get(plasma_url, timeout=10)
            plasma_response.raise_for_status()
            plasma_data = plasma_response.json()
            
            if len(plasma_data) < 2:
                print(f"{datetime.now().isoformat()} - No plasma data available", file=sys.stderr)
                return False
                
            latest_plasma = plasma_data[-1]  # Last entry
            # Plasma fields: [time_tag, density, speed, temperature]
            speed = float(latest_plasma[2]) if latest_plasma[2] != '' else None
            density = float(latest_plasma[1]) if latest_plasma[1] != '' else None
            
            # Store in database
            conn = get_db_connection()
            cur = conn.cursor()
            
            cur.execute("""
                INSERT INTO solar_wind_data (speed, density, bt)
                VALUES (%s, %s, %s)
            """, (speed, density, bt))
            
            conn.commit()
            cur.close()
            conn.close()
            
            print(f"{datetime.now().isoformat()} - Solar wind data stored: {speed}km/s, {density}p/cm³, Bt={bt}nT")
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
    
    return False

if __name__ == '__main__':
    success = fetch_and_store_solar_wind()
    sys.exit(0 if success else 1)
