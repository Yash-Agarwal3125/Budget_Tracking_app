from flask import Blueprint, request, jsonify
from datetime import date
import mysql.connector
from database import get_db_connection

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
