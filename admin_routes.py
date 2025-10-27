from flask import Blueprint, jsonify
from database import get_db_connection
import mysql.connector
from datetime import datetime, timedelta

# Blueprint for admin-related API endpoints
admin_bp = Blueprint('admin', __name__)

@admin_bp.route("/stats", methods=['GET'])
def get_admin_stats():
    """Fetches high-level statistics for the admin dashboard."""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = conn.cursor(dictionary=True)
    try:
        # Get total users
        cursor.execute("SELECT COUNT(*) as total_users FROM User")
        total_users = cursor.fetchone()['total_users']

        # Get total transactions
        cursor.execute("SELECT COUNT(*) as total_transactions FROM transaction")
        total_transactions = cursor.fetchone()['total_transactions']
        
        # Get total money tracked (simple sum)
        cursor.execute("""
            SELECT SUM(CASE WHEN type = 'Income' THEN amount ELSE 0 END) as total_income,
                   SUM(CASE WHEN type = 'Expense' THEN amount ELSE 0 END) as total_expense
            FROM transaction
        """)
        totals = cursor.fetchone()

        return jsonify({
            'total_users': total_users,
            'total_transactions': total_transactions,
            'total_income': float(totals['total_income'] or 0),
            'total_expense': float(totals['total_expense'] or 0)
        })
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    finally:
        cursor.close()
        conn.close()

@admin_bp.route("/latest_transactions", methods=['GET'])
def get_latest_transactions():
    """Fetches the 50 most recent transactions from all users."""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = conn.cursor(dictionary=True)
    try:
        # Join with User table to get the username
        query = """
            SELECT t.*, u.user_name 
            FROM transaction t
            JOIN User u ON t.user_id = u.user_id
            ORDER BY t.date DESC, t.transaction_id DESC
            LIMIT 50
        """
        cursor.execute(query)
        transactions = cursor.fetchall()

        # Convert date/decimal for JSON
        for tx in transactions:
            tx['amount'] = float(tx['amount'])
            tx['date'] = tx['date'].isoformat()

        return jsonify(transactions)
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    finally:
        cursor.close()
        conn.close()

@admin_bp.route("/chart/types_by_value", methods=['GET'])
def chart_types_by_value():
    """Provides a breakdown of all transaction types by SUM(amount)."""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT type, SUM(amount) as total_value
            FROM transaction
            GROUP BY type
        """
        cursor.execute(query)
        results = cursor.fetchall()

        labels = [r['type'] for r in results]
        data = [float(r['total_value'] or 0) for r in results]

        return jsonify({'labels': labels, 'data': data})
        
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    finally:
        cursor.close()
        conn.close()


@admin_bp.route("/chart/types_by_count", methods=['GET'])
def chart_types_by_count():
    """Provides a breakdown of all transaction types by COUNT(*)."""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT type, COUNT(*) as total_count
            FROM transaction
            GROUP BY type
        """
        cursor.execute(query)
        results = cursor.fetchall()

        labels = [r['type'] for r in results]
        data = [r['total_count'] for r in results]

        return jsonify({'labels': labels, 'data': data})
        
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    finally:
        cursor.close()
        conn.close()
@admin_bp.route("/chart/transaction_activity", methods=['GET'])
def chart_transaction_activity():
    """Provides data for transaction activity over the last 30 days."""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    try:
        thirty_days_ago = datetime.now() - timedelta(days=30)
        query = """
            SELECT DATE(date) as date, COUNT(*) as count 
            FROM transaction
            WHERE date >= %s
            GROUP BY DATE(date)
            ORDER BY date ASC
        """
        cursor.execute(query, (thirty_days_ago,))
        results = cursor.fetchall()
        
        date_map = {res['date'].isoformat(): res['count'] for res in results}
        labels = []
        data = []
        for i in range(29, -1, -1):
            date_key = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            labels.append(date_key)
            data.append(date_map.get(date_key, 0))

        return jsonify({'labels': labels, 'data': data})
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    finally:
        cursor.close()
        conn.close()