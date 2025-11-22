"""
Weather and Solar Wind Data Analytics Blueprint
Fetches data from weather_data and solar_wind_data tables in lempdb
"""
from flask import Blueprint, render_template, jsonify
import psycopg2
import os
from datetime import datetime

api_data_bp = Blueprint('api_data', __name__, url_prefix='/weather-data')

def get_db_connection():
    """Create database connection to lempdb"""
    return psycopg2.connect(os.environ.get('DATABASE_URL'))

@api_data_bp.route('/')
def weather_data():
    """Render weather and solar wind data page"""
    return render_template('api-data.html')

@api_data_bp.route('/api/stats')
def get_stats():
    """Get latest weather and solar wind data with 24h history"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get latest 288 weather records (24 hours at 5min intervals)
        cur.execute("""
            SELECT timestamp, temperature, wind_speed, humidity, pressure
            FROM weather_data
            ORDER BY timestamp DESC
            LIMIT 288
        """)
        weather_rows = cur.fetchall()
        
        # Get latest 288 solar wind records (24 hours at 5min intervals)
        cur.execute("""
            SELECT timestamp, speed, density, bt
            FROM solar_wind_data
            ORDER BY timestamp DESC
            LIMIT 288
        """)
        solar_rows = cur.fetchall()
        
        cur.close()
        conn.close()
        
        # Format weather data (reverse to chronological order)
        weather_data = {
            'timestamps': [row[0].strftime('%H:%M') for row in reversed(weather_rows)],
            'temperature': [float(row[1]) if row[1] is not None else None for row in reversed(weather_rows)],
            'wind_speed': [float(row[2]) if row[2] is not None else None for row in reversed(weather_rows)],
            'humidity': [float(row[3]) if row[3] is not None else None for row in reversed(weather_rows)],
            'pressure': [float(row[4]) if row[4] is not None else None for row in reversed(weather_rows)]
        }
        
        # Format solar wind data (reverse to chronological order)
        solar_data = {
            'timestamps': [row[0].strftime('%H:%M') for row in reversed(solar_rows)],
            'speed': [float(row[1]) if row[1] is not None else None for row in reversed(solar_rows)],
            'density': [float(row[2]) if row[2] is not None else None for row in reversed(solar_rows)],
            'bt': [float(row[3]) if row[3] is not None else None for row in reversed(solar_rows)]
        }
        
        # Calculate latest values and statistics
        latest_weather = {
            'temperature': weather_data['temperature'][-1] if weather_data['temperature'] else None,
            'wind_speed': weather_data['wind_speed'][-1] if weather_data['wind_speed'] else None,
            'humidity': weather_data['humidity'][-1] if weather_data['humidity'] else None,
            'pressure': weather_data['pressure'][-1] if weather_data['pressure'] else None,
            'avg_temp_24h': round(sum(t for t in weather_data['temperature'] if t is not None) / 
                                 len([t for t in weather_data['temperature'] if t is not None]), 1) 
                           if weather_data['temperature'] else None
        }
        
        latest_solar = {
            'speed': solar_data['speed'][-1] if solar_data['speed'] else None,
            'density': solar_data['density'][-1] if solar_data['density'] else None,
            'bt': solar_data['bt'][-1] if solar_data['bt'] else None,
            'avg_speed_24h': round(sum(s for s in solar_data['speed'] if s is not None) / 
                                   len([s for s in solar_data['speed'] if s is not None]), 1)
                            if solar_data['speed'] else None
        }
        
        return jsonify({
            'weather': weather_data,
            'solar': solar_data,
            'latest': {
                'weather': latest_weather,
                'solar': latest_solar
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
