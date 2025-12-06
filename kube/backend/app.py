"""
Kubernetes Backend - Flask API
Connects to host PostgreSQL and provides simple endpoints
"""

from flask import Flask, jsonify
import psycopg2
import os
from datetime import datetime

app = Flask(__name__)

# Database configuration from environment variables
DB_HOST = os.getenv('DB_HOST', 'host.minikube.internal')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'lempdb')
DB_USER = os.getenv('DB_USER', 'lempuser')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')


def get_db_connection():
    """Create PostgreSQL connection"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        raise


@app.route('/api/health')
def health():
    """Health check endpoint"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT 1')
        cur.close()
        conn.close()
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 503


@app.route('/api/time')
def get_time():
    """Get current time from PostgreSQL"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT NOW() AT TIME ZONE 'Europe/Helsinki'")
        result = cur.fetchone()
        cur.close()
        conn.close()
        
        if result is None:
            return jsonify({'error': 'No data returned from database'}), 500
        
        current_time = result[0]
        return jsonify({
            'time': current_time.isoformat(),
            'timezone': 'Europe/Helsinki',
            'source': 'PostgreSQL on host',
            'database': DB_NAME
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/info')
def info():
    """Get application information"""
    return jsonify({
        'application': 'Kubernetes LEMP Demo',
        'backend': 'Python Flask',
        'database': f'PostgreSQL ({DB_HOST}:{DB_PORT}/{DB_NAME})',
        'environment': {
            'db_host': DB_HOST,
            'db_port': DB_PORT,
            'db_name': DB_NAME,
            'db_user': DB_USER
        }
    })


@app.route('/api/')
@app.route('/api')
def index():
    """Root API endpoint"""
    return jsonify({
        'message': 'Kubernetes Backend API',
        'endpoints': {
            '/api': 'This endpoint',
            '/api/health': 'Health check',
            '/api/time': 'Current time from PostgreSQL',
            '/api/info': 'Application information'
        }
    })


if __name__ == '__main__':
    # Development mode only - production uses Gunicorn
    app.run(host='0.0.0.0', port=5000, debug=True)
