"""
TimeApp - Flask application for time display and analytics
"""

__version__ = '1.0.0'
__author__ = 'OAMK Student'

from flask import Flask
import os


def create_app(config=None):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Default configuration
    app.config.update(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production'),
        DATABASE_URL=os.environ.get('DATABASE_URL', 'postgresql://localhost/timeapp'),
    )
    
    # Override with custom config if provided
    if config:
        app.config.update(config)
    
    # Register blueprints
    from timeapp.time_endpoint import time_bp
    from timeapp.analytics import analytics_bp
    
    app.register_blueprint(time_bp)
    app.register_blueprint(analytics_bp)
    
    return app
