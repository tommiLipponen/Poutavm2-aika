# TimeApp - Flask Time & Analytics Application

A Flask-based web application that displays current time from PostgreSQL and provides analytics dashboards using the Chinook database. Built as part of Linux Administration course at OAMK.

**Live Demo**: http://86.50.23.0/

## Features

- **Real-time time display** - Fetches time from PostgreSQL (lempdb) every 5 seconds
- **Analytics dashboard** (`/data-analysis/`) - Interactive data visualization using Chinook database
- **RESTful API endpoints** - JSON API for time and statistics
- **PostgreSQL integration** - Uses existing lempdb (Chinook database)
- **Production-ready deployment** - Nginx, Gunicorn, systemd configuration
- **Automated backups** - Daily database backups with systemd timers
- **Finnish language support** - User interface in Finnish

## Project Structure

```
timeapp/
├── .gitignore
├── README.md
├── LICENSE
├── requirements.txt
├── setup.cfg
├── timeapp/
│   ├── __init__.py
│   ├── app.py
│   ├── analytics.py
│   ├── time_endpoint.py
│   ├── templates/
│   └── static/
│       ├── css/
│       ├── js/
│       └── data-analytics.html
├── tests/
├── infra/
│   ├── nginx.timeapp.conf.example
│   ├── timeapp.service.example
│   ├── deploy.sh.example
│   └── backup_pg.timer.example
└── docs/
    ├── DEPLOY.md
    └── DESIGN.md
```

## Quick Start

### Local Development

```bash
# Clone the repository
git clone https://github.com/tommiLipponen/Poutavm2-aika.git
cd Poutavm2-aika

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python -m timeapp.app
```

### Production Deployment

See [DEPLOY.md](docs/DEPLOY.md) for detailed deployment instructions to CSC Pouta.

## Requirements

- Python 3.8+
- Flask
- PostgreSQL (for production)

## Testing

```bash
pytest tests/
```

## Production Deployment

See [DEPLOY.md](docs/DEPLOY.md) for comprehensive deployment instructions to CSC Pouta.

Quick deploy:
```bash
git clone https://github.com/tommiLipponen/Poutavm2-aika.git
cd Poutavm2-aika
chmod +x infra/deploy.sh
sudo ./infra/deploy.sh
```

## API Endpoints

- `GET /` - Main page with time display
- `GET /time` - Time display page
- `GET /time/api` - Time API (JSON)
- `GET /data-analysis/` - Analytics dashboard
- `GET /data-analysis/api/stats` - Analytics API (JSON)

## License

MIT License - see LICENSE file for details

## Author

Tommi Lipponen - Linux Administration Course, Fall 2025

## Repository

https://github.com/tommiLipponen/Poutavm2-aika
