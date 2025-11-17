"""
Time endpoint module for displaying and serving time data
"""

from flask import Blueprint, jsonify, render_template_string
from datetime import datetime
import pytz


time_bp = Blueprint('time', __name__)


@time_bp.route('/')
def show_time():
    """Display current time in HTML"""
    now = datetime.now()
    helsinki_tz = pytz.timezone('Europe/Helsinki')
    helsinki_time = datetime.now(helsinki_tz)
    
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Current Time - TimeApp</title>
        <link rel="stylesheet" href="/static/css/style.css">
        <script>
            function updateTime() {
                fetch('/time/api')
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('time').textContent = data.time;
                        document.getElementById('date').textContent = data.date;
                    });
            }
            setInterval(updateTime, 1000);
        </script>
    </head>
    <body>
        <div class="container">
            <h1>Current Time</h1>
            <div class="time-display">
                <div id="time" class="time">{{ time }}</div>
                <div id="date" class="date">{{ date }}</div>
                <div class="timezone">{{ timezone }}</div>
            </div>
            <a href="/" class="back-link">← Back to Home</a>
        </div>
    </body>
    </html>
    '''
    
    return render_template_string(
        html,
        time=helsinki_time.strftime('%H:%M:%S'),
        date=helsinki_time.strftime('%A, %B %d, %Y'),
        timezone='Europe/Helsinki (EET/EEST)'
    )


@time_bp.route('/api')
def time_api():
    """API endpoint for current time"""
    now = datetime.now()
    helsinki_tz = pytz.timezone('Europe/Helsinki')
    helsinki_time = datetime.now(helsinki_tz)
    utc_time = datetime.now(pytz.UTC)
    
    return jsonify({
        'time': helsinki_time.strftime('%H:%M:%S'),
        'date': helsinki_time.strftime('%Y-%m-%d'),
        'datetime': helsinki_time.isoformat(),
        'timezone': 'Europe/Helsinki',
        'utc': utc_time.isoformat(),
        'timestamp': int(now.timestamp())
    })
