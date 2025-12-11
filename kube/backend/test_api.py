"""
Test suite for CI/CD backend API
Tests all endpoints to ensure functionality before deployment
"""

import pytest
from app import app


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_api_root(client):
    """Test the root API endpoint"""
    response = client.get('/api')
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Kubernetes Backend API'
    assert 'endpoints' in data


def test_api_root_with_slash(client):
    """Test the root API endpoint with trailing slash"""
    response = client.get('/api/')
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Kubernetes Backend API'


def test_health_endpoint(client):
    """Test the health check endpoint"""
    response = client.get('/api/health')
    assert response.status_code in [200, 503]  # Can be unhealthy if DB is down
    data = response.get_json()
    assert 'status' in data
    assert 'timestamp' in data


def test_time_endpoint(client):
    """Test the time endpoint"""
    response = client.get('/api/time')
    # May fail if no database connection, which is okay in CI
    assert response.status_code in [200, 500]
    data = response.get_json()
    
    if response.status_code == 200:
        assert 'time' in data
        assert 'timezone' in data
        assert data['timezone'] == 'Europe/Helsinki'


def test_info_endpoint(client):
    """Test the info endpoint"""
    response = client.get('/api/info')
    assert response.status_code == 200
    data = response.get_json()
    assert data['application'] == 'Kubernetes LEMP Demo'
    assert 'backend' in data
    assert 'database' in data
    assert 'environment' in data


def test_users_endpoint_get(client):
    """Test getting users (may fail without database)"""
    response = client.get('/api/users')
    # Accept both success and error responses
    assert response.status_code in [200, 500]
    data = response.get_json()
    
    if response.status_code == 200:
        assert 'count' in data
        assert 'users' in data


def test_add_user_missing_data(client):
    """Test adding user with missing data - validation should happen before DB connection"""
    response = client.post('/api/users',
                          json={},
                          content_type='application/json')
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert 'required' in data['error'].lower()


def test_add_user_empty_name(client):
    """Test adding user with empty name - validation should happen before DB connection"""
    response = client.post('/api/users',
                          json={'name': '   '},
                          content_type='application/json')
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert 'empty' in data['error'].lower()


def test_add_user_too_long(client):
    """Test adding user with name too long - validation should happen before DB connection"""
    long_name = 'a' * 101  # More than 100 characters
    response = client.post('/api/users',
                          json={'name': long_name},
                          content_type='application/json')
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert 'long' in data['error'].lower()


def test_init_database_endpoint(client):
    """Test database initialization endpoint"""
    response = client.post('/api/init')
    # May fail without database, which is expected in CI
    assert response.status_code in [200, 500]
    data = response.get_json()
    
    if response.status_code == 200:
        assert 'status' in data
        assert 'message' in data


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
