"""
Analytics module for data visualization and statistics
"""

from flask import Blueprint, render_template, jsonify
from datetime import datetime, timedelta
import random


analytics_bp = Blueprint('analytics', __name__, url_prefix='/data-analysis')


@analytics_bp.route('/')
def analytics_dashboard():
    """Analytics dashboard page"""
    return render_template('data-analytics.html')


@analytics_bp.route('/api/stats')
def get_stats():
    """API endpoint for analytics statistics"""
    # Generate sample data for demonstration
    now = datetime.now()
    
    # Sample data: requests per hour for last 24 hours
    hourly_requests = []
    for i in range(24):
        hour = (now - timedelta(hours=23-i)).strftime('%H:00')
        requests = random.randint(10, 100)
        hourly_requests.append({'hour': hour, 'requests': requests})
    
    # Sample data: geographic distribution
    geo_data = [
        {'country': 'Finland', 'requests': random.randint(100, 500)},
        {'country': 'Sweden', 'requests': random.randint(50, 200)},
        {'country': 'Norway', 'requests': random.randint(30, 150)},
        {'country': 'Denmark', 'requests': random.randint(20, 100)},
        {'country': 'Other', 'requests': random.randint(40, 180)},
    ]
    
    # Sample data: response times
    response_times = {
        'avg': round(random.uniform(50, 150), 2),
        'min': round(random.uniform(10, 40), 2),
        'max': round(random.uniform(200, 400), 2),
        'p95': round(random.uniform(150, 250), 2),
    }
    
    return jsonify({
        'hourly_requests': hourly_requests,
        'geo_data': geo_data,
        'response_times': response_times,
        'total_requests': sum(item['requests'] for item in hourly_requests),
        'uptime_hours': round(random.uniform(720, 744), 1),
    })


@analytics_bp.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'timeapp-analytics'
    })
