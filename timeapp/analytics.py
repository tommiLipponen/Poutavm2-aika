"""
Analytics module for data visualization and statistics from Chinook database
"""

from flask import Blueprint, render_template, jsonify, current_app
from datetime import datetime
import psycopg2
import os


analytics_bp = Blueprint('analytics', __name__, url_prefix='/data-analysis')


def get_db_connection():
    """Create database connection"""
    database_url = os.environ.get('DATABASE_URL', 'postgresql://lempuser:StrongPassword@localhost/lempdb')
    return psycopg2.connect(database_url)


@analytics_bp.route('/')
def analytics_dashboard():
    """Analytics dashboard page"""
    return render_template('data-analytics.html')


@analytics_bp.route('/api/stats')
def get_stats():
    """API endpoint for analytics statistics from Chinook database"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # 1. Sales by Country (Top 10)
        cur.execute("""
            SELECT 
                billing_country,
                COUNT(*) as invoice_count,
                ROUND(SUM(total)::numeric, 2) as total_sales
            FROM invoice
            GROUP BY billing_country
            ORDER BY total_sales DESC
            LIMIT 10;
        """)
        sales_by_country = [
            {'country': row[0], 'invoices': row[1], 'sales': float(row[2])}
            for row in cur.fetchall()
        ]
        
        # 2. Top Genres by Track Count
        cur.execute("""
            SELECT 
                g.name as genre_name,
                COUNT(t.track_id) as track_count
            FROM genre g
            LEFT JOIN track t ON g.genre_id = t.genre_id
            GROUP BY g.name
            ORDER BY track_count DESC
            LIMIT 8;
        """)
        genre_data = [
            {'genre': row[0], 'tracks': row[1]}
            for row in cur.fetchall()
        ]
        
        # 3. Monthly Sales Trend (last 12 months)
        cur.execute("""
            SELECT 
                TO_CHAR(invoice_date, 'YYYY-MM') as month,
                COUNT(*) as invoice_count,
                ROUND(SUM(total)::numeric, 2) as total_sales
            FROM invoice
            GROUP BY TO_CHAR(invoice_date, 'YYYY-MM')
            ORDER BY month DESC
            LIMIT 12;
        """)
        monthly_sales = [
            {'month': row[0], 'invoices': row[1], 'sales': float(row[2])}
            for row in cur.fetchall()
        ]
        monthly_sales.reverse()  # Chronological order
        
        # 4. Top Artists by Album Count
        cur.execute("""
            SELECT 
                ar.name as artist_name,
                COUNT(al.album_id) as album_count
            FROM artist ar
            LEFT JOIN album al ON ar.artist_id = al.artist_id
            GROUP BY ar.name
            ORDER BY album_count DESC
            LIMIT 10;
        """)
        top_artists = [
            {'artist': row[0], 'albums': row[1]}
            for row in cur.fetchall()
        ]
        
        # 5. Summary Statistics
        cur.execute("""
            SELECT 
                COUNT(DISTINCT customer_id) as total_customers,
                COUNT(*) as total_invoices,
                COUNT(DISTINCT billing_country) as countries,
                ROUND(SUM(total)::numeric, 2) as total_revenue,
                ROUND(AVG(total)::numeric, 2) as avg_invoice_value
            FROM invoice;
        """)
        stats = cur.fetchone()
        
        # 6. Track Statistics
        cur.execute("""
            SELECT COUNT(*) FROM track;
        """)
        track_result = cur.fetchone()
        total_tracks = track_result[0] if track_result else 0
        
        cur.close()
        conn.close()
        
        return jsonify({
            'sales_by_country': sales_by_country,
            'genre_data': genre_data,
            'monthly_sales': monthly_sales,
            'top_artists': top_artists,
            'summary': {
                'total_customers': stats[0] if stats else 0,
                'total_invoices': stats[1] if stats else 0,
                'countries': stats[2] if stats else 0,
                'total_revenue': float(stats[3]) if stats else 0.0,
                'avg_invoice': float(stats[4]) if stats else 0.0,
                'total_tracks': total_tracks
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Database error in analytics: {e}")
        return jsonify({'error': 'Database error', 'message': str(e)}), 500


@analytics_bp.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'timeapp-analytics'
    })
