"""
MQTT Chat Blueprint
Provides chat interface with MQTT messaging and PostgreSQL persistence
"""
from flask import Blueprint, render_template, jsonify
import psycopg2
import os
from datetime import datetime

mqtt_chat_bp = Blueprint('mqtt_chat', __name__, url_prefix='/mqtt-chat')

def get_db_connection():
    """Create database connection to lempdb"""
    return psycopg2.connect(os.environ.get('DATABASE_URL'))

@mqtt_chat_bp.route('/')
def chat_page():
    """Render MQTT chat page"""
    return render_template('mqtt-chat.html')

@mqtt_chat_bp.route('/api/messages')
def get_messages():
    """Get recent chat messages from database"""
    try:
        from flask import request
        limit = int(request.args.get('limit', 50))  # Default 50 messages
        offset = int(request.args.get('offset', 0))  # Default offset 0
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT id, nickname, message, client_id, created_at
            FROM mqtt_messages
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """, (limit, offset))
        
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        # Format messages (reverse to chronological order)
        messages = []
        for row in reversed(rows):
            messages.append({
                'id': row[0],
                'nickname': row[1],
                'message': row[2],
                'clientId': row[3],
                'timestamp': row[4].isoformat() if row[4] else None
            })
        
        return jsonify({
            'messages': messages,
            'count': len(messages)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mqtt_chat_bp.route('/api/stats')
def get_stats():
    """Get chat statistics"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Total messages
        cur.execute("SELECT COUNT(*) FROM mqtt_messages")
        result = cur.fetchone()
        total_messages = result[0] if result else 0
        
        # Messages today
        cur.execute("""
            SELECT COUNT(*) FROM mqtt_messages
            WHERE DATE(created_at) = CURRENT_DATE
        """)
        result = cur.fetchone()
        messages_today = result[0] if result else 0
        
        # Unique users
        cur.execute("SELECT COUNT(DISTINCT nickname) FROM mqtt_messages")
        result = cur.fetchone()
        unique_users = result[0] if result else 0
        
        # Most active user
        cur.execute("""
            SELECT nickname, COUNT(*) as msg_count
            FROM mqtt_messages
            GROUP BY nickname
            ORDER BY msg_count DESC
            LIMIT 1
        """)
        most_active = cur.fetchone()
        
        cur.close()
        conn.close()
        
        return jsonify({
            'total_messages': total_messages,
            'messages_today': messages_today,
            'unique_users': unique_users,
            'most_active_user': most_active[0] if most_active else None,
            'most_active_count': most_active[1] if most_active else 0
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
