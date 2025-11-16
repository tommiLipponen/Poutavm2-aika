"""
Unit tests for TimeApp
"""

import pytest
from timeapp import create_app


@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app({'TESTING': True})
    yield app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


def test_app_creation():
    """Test application factory"""
    app = create_app()
    assert app is not None
    assert app.config['SECRET_KEY'] is not None


def test_home_page(client):
    """Test home page loads"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Welcome to TimeApp' in response.data


def test_time_page(client):
    """Test time page loads"""
    response = client.get('/time/')
    assert response.status_code == 200
    assert b'Current Time' in response.data


def test_time_api(client):
    """Test time API endpoint"""
    response = client.get('/time/api')
    assert response.status_code == 200
    data = response.get_json()
    assert 'time' in data
    assert 'date' in data
    assert 'timezone' in data
    assert 'timestamp' in data


def test_analytics_page(client):
    """Test analytics dashboard loads"""
    response = client.get('/analytics/')
    assert response.status_code == 200
    assert b'Analytics Dashboard' in response.data


def test_analytics_stats_api(client):
    """Test analytics stats API"""
    response = client.get('/analytics/api/stats')
    assert response.status_code == 200
    data = response.get_json()
    assert 'hourly_requests' in data
    assert 'geo_data' in data
    assert 'response_times' in data
    assert 'total_requests' in data


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get('/analytics/api/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert 'timestamp' in data
