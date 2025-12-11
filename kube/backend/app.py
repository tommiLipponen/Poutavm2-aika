"""
Kubernetes Backend - Flask API
Connects to host PostgreSQL and provides simple endpoints
"""

from flask import Flask, jsonify, request
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
            '/api/info': 'Application information',
            '/api/init': 'Initialize users table (POST)',
            '/api/users': 'Get all users (GET) or add user (POST)'
        }
    })


@app.route('/api/init', methods=['POST'])
def init_database():
    """Initialize users table with sample data"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Create users table if it doesn't exist
        cur.execute('''
            CREATE TABLE IF NOT EXISTS kube_users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Check if table is empty
        cur.execute('SELECT COUNT(*) FROM kube_users')
        result = cur.fetchone()
        count = result[0] if result else 0
        
        if count == 0:
            # Add sample users
            sample_users = ['Alice', 'Bob', 'Charlie', 'Diana']
            for name in sample_users:
                cur.execute('INSERT INTO kube_users (name) VALUES (%s)', (name,))
            
            conn.commit()
            message = f'Database initialized with {len(sample_users)} sample users'
        else:
            message = f'Database already contains {count} users'
        
        cur.close()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'message': message,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/users', methods=['GET', 'POST'])
def users():
    """Get all users or add a new user"""
    # Validate input BEFORE connecting to database
    if request.method == 'POST':
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({'error': 'Name is required'}), 400
        
        name = data['name'].strip()
        if not name:
            return jsonify({'error': 'Name cannot be empty'}), 400
        
        if len(name) > 100:
            return jsonify({'error': 'Name too long (max 100 characters)'}), 400
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        if request.method == 'POST':
            # SQL injection is already prevented by using parameterized query (%s)
            cur.execute('INSERT INTO kube_users (name) VALUES (%s) RETURNING id, name, created_at', (name,))
            result = cur.fetchone()
            
            if result is None:
                conn.rollback()
                return jsonify({'error': 'Failed to insert user'}), 500
            
            conn.commit()
            
            return jsonify({
                'status': 'success',
                'message': f'User {name} added successfully',
                'user': {
                    'id': result[0],
                    'name': result[1],
                    'created_at': result[2].isoformat()
                }
            }), 201
        
        else:
            # Get all users
            cur.execute('SELECT id, name, created_at FROM kube_users ORDER BY created_at DESC')
            rows = cur.fetchall()
            
            users_list = [
                {
                    'id': row[0],
                    'name': row[1],
                    'created_at': row[2].isoformat()
                }
                for row in rows
            ]
            
            cur.close()
            conn.close()
            
            return jsonify({
                'count': len(users_list),
                'users': users_list
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # Development mode only - production uses Gunicorn
    app.run(host='0.0.0.0', port=5000, debug=True)
