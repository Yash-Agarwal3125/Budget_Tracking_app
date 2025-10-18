from flask import Blueprint, request, jsonify
from datetime import date
import mysql.connector
from database import get_db_connection
from datetime import datetime, timedelta

# Blueprint for transaction-related API endpoints
transactions_bp = Blueprint('transactions', __name__)

@transactions_bp.route("/dashboard_data", methods=['GET'])
def get_dashboard_data():
    """Fetches and calculates all dashboard data for a user."""
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = conn.cursor(dictionary=True)
    try:
        query = "SELECT * FROM transaction WHERE user_id = %s ORDER BY date DESC"
        cursor.execute(query, (user_id,))
        transactions = cursor.fetchall()

        # Calculate summary metrics
        total_income = sum(t['amount'] for t in transactions if t['type'] == 'Income')
        total_spend = sum(t['amount'] for t in transactions if t['type'] == 'Expense')
        total_payable = sum(t['amount'] for t in transactions if t['type'] == 'Payable' and t['status'] == 'Pending')
        total_receivable = sum(t['amount'] for t in transactions if t['type'] == 'Receivable' and t['status'] == 'Pending')
        current_balance = total_income - total_spend

        summary = {
            'current_balance': float(current_balance),
            'total_income': float(total_income),
            'total_spend': float(total_spend),
            'total_payable': float(total_payable),
            'total_receivable': float(total_receivable)
        }

        # Convert decimal and date objects for JSON serialization
        for tx in transactions:
            tx['amount'] = float(tx['amount'])
            if isinstance(tx['date'], date):
                tx['date'] = tx['date'].isoformat()

        return jsonify({'summary': summary, 'transactions': transactions})
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    finally:
        cursor.close()
        conn.close()


@transactions_bp.route('/transactions', methods=["POST"])
def add_transaction():
    """Adds a new transaction to the database."""
    data = request.get_json()
    user_id = data.get('user_id')
    tx_type = data.get('type')
    amount = data.get('amount')
    category_name = data.get('category_name') or 'Uncategorized'
    description = data.get('description')
    person_involved = data.get('person_involved')

    if not all([user_id, tx_type, amount, description]):
        return jsonify({'error': 'Missing required fields'}), 400

    status = 'Pending' if tx_type in ['Payable', 'Receivable'] else 'Completed'

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = conn.cursor()
    try:
        query = "INSERT INTO transaction(user_id, type, amount, category_name, description, date, person_involved, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (user_id, tx_type, amount, category_name, description, date.today(), person_involved, status))
        conn.commit()
        return jsonify({'message': 'New transaction added'}), 201
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    finally:
        cursor.close()
        conn.close()


@transactions_bp.route("/pay_debt", methods=["POST"])
def pay_debt():
    """Marks a payable as paid and creates a corresponding expense."""
    data = request.get_json()
    transaction_id = data.get('transaction_id')
    if not transaction_id:
        return jsonify({'error': 'Transaction ID is required'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM transaction WHERE transaction_id = %s", (transaction_id,))
        payable_tx = cursor.fetchone()
        if not payable_tx:
            return jsonify({'error': 'Payable transaction not found'}), 404

        # Update the original payable transaction to 'Paid'
        cursor.execute("UPDATE transaction SET status = 'Paid' WHERE transaction_id = %s", (transaction_id,))

        # Create a new 'Expense' transaction
        expense_description = f"Paid debt to {payable_tx['person_involved']}: {payable_tx['description']}"
        query = "INSERT INTO transaction (user_id, type, amount, category_name, description, date, status) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (payable_tx['user_id'], 'Expense', payable_tx['amount'], 'Debt Payment', expense_description, date.today(), 'Completed'))

        conn.commit()
        return jsonify({'message': 'Debt marked as paid!'}), 200
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({'error': str(err)}), 500
    finally:
        cursor.close()
        conn.close()


@transactions_bp.route("/reset_transactions", methods=['DELETE'])
def reset_transactions():
    """Deletes all transactions for a specific user."""
    data = request.get_json()
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = conn.cursor()
    try:
        query = "DELETE FROM transaction WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        conn.commit()
        return jsonify({'message': f'{cursor.rowcount} transactions have been reset.'}), 200
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({'error': str(err)}), 500
    finally:
        cursor.close()
        conn.close()

@transactions_bp.route("/chart_data/expenses_by_category", methods=['GET'])
def expenses_by_category_chart():
    """Provides data for the expenses by category pie chart."""
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = conn.cursor(dictionary=True)
    try:
        # Query to sum expense amounts for each category
        query = """
            SELECT category_name, SUM(amount) as total
            FROM transaction
            WHERE user_id = %s AND type = 'Expense'
            GROUP BY category_name
            ORDER BY total DESC
        """
        cursor.execute(query, (user_id,))
        data = cursor.fetchall()
        
        # Format data for Chart.js
        labels = [row['category_name'] for row in data]
        values = [float(row['total']) for row in data]

        return jsonify({'labels': labels, 'values': values})

    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    finally:
        cursor.close()
        conn.close()
# ... (keep all your existing routes) ...

# ADD THIS NEW ROUTE AT THE END OF THE FILE, INSIDE THE BLUEPRINT

@transactions_bp.route("/chart_data/income_vs_expense", methods=['GET'])
def income_vs_expense_chart():
    """Provides data for the income vs. expense bar chart."""
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = conn.cursor(dictionary=True)
    try:
        # Query to get all transactions for the user
        query = "SELECT type, amount FROM transaction WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        transactions = cursor.fetchall()
        
        # Calculate totals in Python
        total_income = sum(t['amount'] for t in transactions if t['type'] == 'Income')
        total_expense = sum(t['amount'] for t in transactions if t['type'] == 'Expense')

        # Format data for Chart.js
        data = {
            'income': float(total_income),
            'expense': float(total_expense)
        }
        
        return jsonify(data)

    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    finally:
        cursor.close()
        conn.close()

@transactions_bp.route("/chart_data/monthly_summary", methods=['GET'])
def monthly_summary_chart():
    """Provides income vs. expense data for the last 6 months."""
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = conn.cursor(dictionary=True)
    try:
        # Get the last 6 months' labels (e.g., "Apr", "May", "Jun")
        labels = []
        today = datetime.today()
        for i in range(5, -1, -1):
            month = today - timedelta(days=i*30)
            labels.append(month.strftime('%b')) # %b gives short month name

        # SQL query to get monthly sums for the last 6 months
        six_months_ago = today - timedelta(days=180)
        query = """
            SELECT
                DATE_FORMAT(date, '%Y-%m') AS month,
                SUM(CASE WHEN type = 'Income' THEN amount ELSE 0 END) AS total_income,
                SUM(CASE WHEN type = 'Expense' THEN amount ELSE 0 END) AS total_expense
            FROM transaction
            WHERE user_id = %s AND date >= %s
            GROUP BY month
            ORDER BY month ASC;
        """
        cursor.execute(query, (user_id, six_months_ago.strftime('%Y-%m-%d')))
        results = cursor.fetchall()

        # Create a dictionary for easy lookup
        data_map = {r['month']: r for r in results}

        # Prepare final data, ensuring all 6 months are present
        income_data = []
        expense_data = []
        for i in range(5, -1, -1):
            month_key = (today - timedelta(days=i*30)).strftime('%Y-%m')
            if month_key in data_map:
                income_data.append(float(data_map[month_key]['total_income']))
                expense_data.append(float(data_map[month_key]['total_expense']))
            else:
                income_data.append(0)
                expense_data.append(0)

        return jsonify({
            'labels': labels,
            'incomeData': income_data,
            'expenseData': expense_data
        })

    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    finally:
        cursor.close()
        conn.close()

