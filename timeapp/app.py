"""
Main application entry point
"""

from timeapp import create_app
import os


app = create_app()


@app.route('/')
def index():
    """Home page - displays current time from database"""
    return '''
    <!DOCTYPE html>
    <html lang="fi-FI">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>TimeApp - Aika Tietokannasta</title>
        <link rel="stylesheet" href="/static/css/style.css">
        <style>
            .time-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                text-align: center;
                padding: 40px 20px;
                margin: 0;
            }
            .time-display-main {
                font-size: 3em;
                font-weight: bold;
                margin: 20px 0;
                animation: fadeIn 0.5s;
            }
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            .info-section {
                padding: 30px;
                background: white;
                margin: 20px auto;
                max-width: 900px;
                border-radius: 15px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }
            .nav-links {
                display: flex;
                gap: 15px;
                justify-content: center;
                flex-wrap: wrap;
                margin-top: 20px;
            }
            .nav-links a {
                padding: 12px 24px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                text-decoration: none;
                border-radius: 8px;
                transition: transform 0.3s;
            }
            .nav-links a:hover {
                transform: translateY(-3px);
            }
            .footer-info {
                text-align: center;
                padding: 20px;
                background-color: #333;
                color: white;
                margin-top: 40px;
            }
        </style>
    </head>
    <body>
        <div class="time-header">
            <h1 id="db-time">Aika latautuu...</h1>
            <p>Haetaan PostgreSQL-tietokannasta (lempdb)</p>
        </div>
        
        <div class="info-section">
            <h2>Stackin Kuvaus</h2>
            <p>Tämä palvelin käyttää seuraavanlaista pinoa:</p>
            <ul>
                <li><strong>Linux:</strong> Ubuntu 24.04 LTS</li>
                <li><strong>Nginx:</strong> Reverse proxy ja staattisten tiedostojen palvelu</li>
                <li><strong>PostgreSQL:</strong> Chinook-tietokanta (lempdb)</li>
                <li><strong>Python Flask:</strong> Web-sovelluskehys</li>
                <li><strong>Gunicorn:</strong> WSGI-palvelin</li>
            </ul>
            
            <h3>Ominaisuudet</h3>
            <div class="nav-links">
                <a href="/time">Aikasivulle</a>
                <a href="/data-analysis/">Data-Analytiikka</a>
                <a href="/time/api">Time API (JSON)</a>
            </div>
        </div>
        
        <div class="footer-info">
            <p>Powered by CSC cPouta | Linux Kurssi 2025</p>
        </div>
        
        <script>
            async function fetchTime() {
                try {
                    const response = await fetch('/time/api');
                    const data = await response.json();
                    // Format the time nicely
                    const timeStr = data.time || 'Ei saatavilla';
                    const dateStr = data.date || '';
                    document.getElementById('db-time').textContent = timeStr + ' (' + dateStr + ')';
                } catch (error) {
                    document.getElementById('db-time').textContent = 'Virhe haettaessa aikaa';
                    console.error('Error fetching time:', error);
                }
            }
            
            // Initial fetch
            fetchTime();
            
            // Update every 5 seconds
            setInterval(fetchTime, 5000);
        </script>
    </body>
    </html>
    '''


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
