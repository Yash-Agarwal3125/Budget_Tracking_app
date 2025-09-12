from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from database import get_db_connection

# Blueprint for authentication routes (login, register)
auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/register", methods=["POST"])
def register_user():
    """Handles new user registration."""
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({'error': 'Missing required fields'}), 400

    hashed_password = generate_password_hash(password)

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = conn.cursor()
    try:
        query = "INSERT INTO User(user_name, email, password) VALUES (%s, %s, %s)"
        cursor.execute(query, (username, email, hashed_password))
        conn.commit()
        return jsonify({'message': 'User registered successfully!'}), 201
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    finally:
        cursor.close()
        conn.close()


@auth_bp.route("/login", methods=['POST'])
def login_user():
    """Handles user login."""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Missing required fields'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = conn.cursor(dictionary=True)
    try:
        query = "SELECT * FROM User WHERE email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            return jsonify({
                'message': 'Login Successful',
                'user_id': user['user_id'],
                'username': user['user_name']
            }), 200
        else:
            return jsonify({'error': 'Invalid email or password'}), 401
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    finally:
        cursor.close()
        conn.close()
