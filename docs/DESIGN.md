# TimeApp Design Document

## Overview

TimeApp is a Flask-based web application designed to display current time and provide analytics capabilities. Built as part of the Linux Administration course at OAMK, it demonstrates modern web application architecture, deployment practices, and system administration concepts.

## Architecture

### System Architecture

```
┌─────────────┐
│   Client    │
│  (Browser)  │
└──────┬──────┘
       │
       │ HTTPS
       ▼
┌─────────────┐
│    Nginx    │ ← Reverse Proxy / Static Files
│   (Port 80) │
└──────┬──────┘
       │
       │ HTTP (localhost)
       ▼
┌─────────────┐
│   Gunicorn  │ ← WSGI Server
│  (Port 5000)│
└──────┬──────┘
       │
       │
       ▼
┌─────────────┐
│    Flask    │ ← Application Framework
│  TimeApp    │
└──────┬──────┘
       │
       │
       ▼
┌─────────────┐
│ PostgreSQL  │ ← Database (Future Use)
└─────────────┘
```

### Application Structure

```
timeapp/
├── __init__.py          # Application factory
├── app.py               # Main entry point & home route
├── time_endpoint.py     # Time display & API endpoints
├── analytics.py         # Analytics dashboard & stats API
├── templates/           # Jinja2 templates
└── static/             # CSS, JavaScript, assets
```

## Components

### 1. Flask Application (`timeapp/__init__.py`)

**Purpose**: Application factory pattern for creating Flask app instances.

**Key Features**:
- Factory pattern for flexibility and testing
- Blueprint registration for modular routes
- Configuration management
- Environment variable support

**Design Decisions**:
- Used factory pattern to support different configurations (dev/prod)
- Blueprints for separation of concerns
- Environment-based configuration for security

### 2. Time Endpoint (`time_endpoint.py`)

**Purpose**: Display current time and provide time API.

**Endpoints**:
- `GET /time/` - HTML time display with auto-update
- `GET /time/api` - JSON API for time data

**Features**:
- Timezone support (Europe/Helsinki)
- Real-time updates via JavaScript
- ISO 8601 formatted timestamps
- UTC conversion

**Design Decisions**:
- PostgreSQL handles timezone conversion with `AT TIME ZONE 'Europe/Helsinki'`
- Separated HTML view and API for flexibility
- Client-side updates to reduce server load

### 3. Analytics Module (`analytics.py`)

**Purpose**: Data visualization and application statistics.

**Endpoints**:
- `GET /analytics/` - Analytics dashboard
- `GET /analytics/api/stats` - Statistics API
- `GET /analytics/api/health` - Health check

**Features**:
- Request metrics (hourly, geographic)
- Response time statistics
- Health monitoring
- Sample data generation (for demonstration)

**Design Decisions**:
- Chart.js for client-side visualization
- Sample data generator for demonstration purposes
- Health check endpoint for monitoring
- Separated API for potential future integrations

### 4. Frontend (`templates/` & `static/`)

**Technologies**:
- HTML5
- CSS3 (with gradients and modern layouts)
- Vanilla JavaScript
- Chart.js for visualizations

**Design Principles**:
- Responsive design
- Clean, modern UI
- Progressive enhancement
- Minimal dependencies

## Infrastructure

### Deployment Stack

**Operating System**: Ubuntu 22.04 LTS on CSC Pouta

**Components**:
1. **Nginx** - Reverse proxy, SSL termination, static files
2. **Gunicorn** - Python WSGI HTTP server
3. **Flask** - Web application framework
4. **PostgreSQL** - Database (for future use)
5. **systemd** - Process management

### Nginx Configuration

**Responsibilities**:
- Reverse proxy to Gunicorn
- SSL/TLS termination
- Static file serving
- Security headers
- Request logging

**Design Decisions**:
- HTTP to HTTPS redirect for security
- Security headers for protection against common attacks
- Separate access and error logs
- Static file caching (30 days)
- WebSocket support for future features

### Systemd Service

**Configuration**:
- 4 Gunicorn workers for concurrency
- Automatic restart on failure
- Resource limits (memory, CPU)
- Security hardening (NoNewPrivileges, PrivateTmp)
- Comprehensive logging

**Design Decisions**:
- Worker count based on CPU cores (2 × cores + 1)
- Sync workers for simplicity
- Resource limits to prevent runaway processes
- Security features following best practices

## Data Flow

### Time Display Request

```
1. User → Browser requests /time/
2. Nginx → Receives request
3. Nginx → Proxies to Gunicorn
4. Gunicorn → Forwards to Flask
5. Flask → time_endpoint.show_time()
6. Flask → Renders template with current time
7. Browser → Receives HTML
8. JavaScript → Fetches /time/api every second
9. Browser → Updates display without page reload
```

### Analytics Data Flow

```
1. User → Browser requests /analytics/
2. Nginx → Proxies to Gunicorn
3. Flask → Renders analytics.html template
4. Browser → JavaScript loads
5. JavaScript → Fetches /analytics/api/stats
6. Flask → Generates sample statistics
7. JavaScript → Creates charts with Chart.js
8. Browser → Displays visualizations
9. JavaScript → Auto-refreshes every 30 seconds
```

## Security Considerations

### Application Security

- **Secret Key**: Generated randomly, stored as environment variable
- **Input Validation**: Flask's built-in protections
- **SQL Injection**: Using parameterized queries (when DB is integrated)
- **XSS Protection**: Jinja2 auto-escaping

### Infrastructure Security

- **HTTPS**: SSL/TLS encryption via Let's Encrypt
- **Security Headers**: 
  - Strict-Transport-Security
  - X-Frame-Options
  - X-Content-Type-Options
  - X-XSS-Protection
- **Firewall**: UFW configured for minimal exposure
- **Process Isolation**: Dedicated user with limited permissions
- **System Hardening**: systemd security features

### Best Practices

1. Passwords in environment variables, not code
2. Regular system updates
3. Automated backups
4. Log monitoring
5. Principle of least privilege

## Testing Strategy

### Unit Tests (`tests/test_timeapp.py`)

**Coverage**:
- Application factory
- All endpoints (HTML and API)
- Response formats
- Status codes

**Framework**: pytest with Flask testing utilities

**Design Decisions**:
- Fixtures for app and client
- Isolated test environment
- Testing mode configuration

## Monitoring and Maintenance

### Logging

**Application Logs**:
- Gunicorn access log: `/var/log/timeapp/access.log`
- Gunicorn error log: `/var/log/timeapp/error.log`

**System Logs**:
- Nginx access: `/var/log/nginx/timeapp_access.log`
- Nginx error: `/var/log/nginx/timeapp_error.log`
- systemd journal: `journalctl -u timeapp`

### Backup Strategy

**Database Backups**:
- Automated daily backups via systemd timer
- 30-day retention policy
- Compressed SQL dumps
- Stored in `/opt/timeapp/backups/`

**Application Backups**:
- Git version control
- Configuration files versioned

### Health Checks

**Endpoint**: `GET /analytics/api/health`

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-15T10:30:00",
  "service": "timeapp-analytics"
}
```

**Monitoring**:
- Nginx health check endpoint
- systemd watchdog (future)
- External monitoring (optional)

## Future Enhancements

### Phase 1 - Database Integration
- Store request logs in PostgreSQL
- Real analytics instead of sample data
- User session tracking

### Phase 2 - Extended Features
- User authentication
- Custom time zones
- World clock display
- Historical data visualization

### Phase 3 - Advanced Operations
- Docker containerization
- CI/CD pipeline
- Prometheus metrics export
- Grafana dashboards

## Development Workflow

### Local Development

```bash
# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run
export FLASK_ENV=development
python -m timeapp.app

# Test
pytest tests/
```

### Deployment

```bash
# Deploy
./infra/deploy.sh

# Update
git pull
systemctl restart timeapp
```

## Technical Decisions Summary

| Decision | Rationale |
|----------|-----------|
| Flask | Lightweight, flexible, Python-based |
| Gunicorn | Production-ready WSGI server |
| Nginx | Industry standard reverse proxy |
| PostgreSQL | Robust, feature-rich database |
| systemd | Native Linux process management |
| Blueprint pattern | Modular, maintainable code |
| Chart.js | Simple, effective visualizations |
| Let's Encrypt | Free, automated SSL |

## Performance Considerations

- **Caching**: Static files cached for 30 days
- **Workers**: 4 Gunicorn workers for concurrency
- **Database**: Connection pooling (future)
- **CDN**: Chart.js loaded from CDN
- **Compression**: Gzip for backups

## References

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [CSC Pouta Documentation](https://docs.csc.fi/cloud/pouta/)
- [systemd Documentation](https://www.freedesktop.org/software/systemd/man/)

---

**Document Version**: 1.0  
**Last Updated**: November 15, 2025  
**Author**: OAMK Student  
**Course**: Linux Administration, Fall 2025
