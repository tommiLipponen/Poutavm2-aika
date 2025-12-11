"""
Time endpoint module for displaying and serving time data
"""

from flask import Blueprint, jsonify, render_template_string, current_app
from datetime import datetime
import psycopg2
import os


time_bp = Blueprint('time', __name__)


def get_db_connection():
    """Create database connection"""
    database_url = os.environ.get('DATABASE_URL', 'postgresql://lempuser:StrongPassword@localhost/lempdb')
    return psycopg2.connect(database_url)


def get_time_from_db():
    """Fetch current time from PostgreSQL database"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT NOW() AT TIME ZONE 'Europe/Helsinki'")
        result = cur.fetchone()
        db_time = result[0] if result else datetime.now()
        cur.close()
        conn.close()
        return db_time
    except Exception as e:
        current_app.logger.error(f"Database error: {e}")
        # Fallback to system time if database fails
        return datetime.now()


@time_bp.route('/')
def show_time():
    """Display current time from PostgreSQL database in HTML"""
    db_time = get_time_from_db()
    
    html = '''
    <!DOCTYPE html>
    <html lang="fi-FI">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>TimeApp - PostgreSQL Aika</title>
        <link rel="stylesheet" href="/static/css/style.css">
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                padding: 40px 20px;
            }
            .time-card {
                background: white;
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                text-align: center;
            }
            h1 {
                color: #667eea;
                margin-top: 0;
                font-size: 2.5em;
            }
            .update-info {
                color: #666;
                font-size: 1.1em;
                margin-bottom: 30px;
                padding: 10px;
                background: #f0f0f0;
                border-radius: 10px;
            }
            .time-display {
                font-size: 4em;
                font-weight: bold;
                color: #764ba2;
                margin: 20px 0;
                animation: fadeIn 0.5s;
            }
            .date-display {
                font-size: 1.5em;
                color: #555;
                margin-bottom: 20px;
            }
            .source-info {
                color: #888;
                font-size: 0.9em;
                margin-top: 20px;
                padding-top: 20px;
                border-top: 1px solid #ddd;
            }
            .nav-link {
                display: inline-block;
                margin-top: 30px;
                padding: 15px 35px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                text-decoration: none;
                border-radius: 10px;
                font-size: 1.2em;
                font-weight: bold;
                transition: all 0.3s;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
            }
            .nav-link:hover {
                transform: translateY(-3px);
                box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
            }
            @keyframes fadeIn {
                from { opacity: 0.5; }
                to { opacity: 1; }
            }
            .spinner {
                display: inline-block;
                width: 12px;
                height: 12px;
                border: 2px solid #667eea;
                border-top-color: transparent;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
        </style>
        <script>
            function updateTime() {
                fetch('/time/api')
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('time').textContent = data.time;
                        document.getElementById('date').textContent = data.date;
                        document.getElementById('last-update').textContent = 'Viimeksi päivitetty: ' + new Date().toLocaleTimeString('fi-FI');
                    })
                    .catch(error => {
                        console.error('Error fetching time:', error);
                        document.getElementById('time').textContent = 'Virhe haettaessa aikaa';
                    });
            }
            
            // Update every 5 seconds
            setInterval(updateTime, 5000);
            
            // Initial update after 5 seconds
            setTimeout(updateTime, 5000);
        </script>
    </head>
    <body>
        <div class="container">
            <div class="time-card">
                <h1>🕐 TimeApp</h1>
                <div class="update-info">
                    <strong>PostgreSQL datetime päivittyy 5 sekunnin välein</strong>
                    <div style="margin-top: 10px; font-size: 0.9em;">
                        <span class="spinner"></span> Automaattinen päivitys käynnissä
                    </div>
                </div>
                <div id="time" class="time-display">{{ time }}</div>
                <div id="date" class="date-display">{{ date }}</div>
                <div id="last-update" class="source-info">Ladattu palvelimelta</div>
                <div class="source-info">
                    <strong>Tietolähde:</strong> PostgreSQL (lempdb)<br>
                    <strong>Aikavyöhyke:</strong> Europe/Helsinki (EET/EEST)
                </div>
                <a href="/data-analysis/" class="nav-link">📊 Data-Analysis sivulle</a>
                <a href="/weather-data/" class="nav-link" style="margin-left: 15px;">🌤️ Sää ja Aurinkotuuli</a>
                <a href="/mqtt-chat/" class="nav-link" style="margin-left: 15px;">💬 MQTT Chat</a>
                <a href="/kube/" class="nav-link" style="margin-left: 15px;">☸️ Kubernetes</a>
                <a href="/cicd/" class="nav-link" style="margin-left: 15px;">🚀 CI/CD Demo</a>
            </div>
        </div>
    </body>
    </html>
    '''
    
    return render_template_string(
        html,
        time=db_time.strftime('%H:%M:%S'),
        date=db_time.strftime('%A, %d.%m.%Y')
    )


@time_bp.route('/time/api')
def time_api():
    """API endpoint for current time from PostgreSQL"""
    db_time = get_time_from_db()
    
    return jsonify({
        'time': db_time.strftime('%H:%M:%S'),
        'date': db_time.strftime('%d.%m.%Y'),
        'datetime': db_time.isoformat(),
        'timezone': 'Europe/Helsinki',
        'source': 'PostgreSQL (lempdb)',
        'timestamp': int(db_time.timestamp())
    })
