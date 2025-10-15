from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from database import get_db_connection
import secrets
from datetime import datetime, timedelta
from extention import mail  # Import the mail instance from your app file
from flask_mail import Message

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

@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    """
    Handles the initial forgot password request.
    Generates a token, stores it, and emails the reset link.
    """
    data = request.get_json()
    email = data.get("email")
    if not email:
        return jsonify({'error': 'Email is required'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM User WHERE email = %s", (email,))
        user = cursor.fetchone()

        # IMPORTANT: Always return a success message to prevent email enumeration attacks
        if not user:
            return jsonify({'message': 'If an account with that email exists, a reset link has been sent.'}), 200

        # Generate a secure token and expiration time
        token = secrets.token_urlsafe(32)
        expires = datetime.utcnow() + timedelta(hours=1)
        
        # Store the token in the database
        query = "INSERT INTO password_reset_tokens (user_id, token, expires_at) VALUES (%s, %s, %s)"
        cursor.execute(query, (user['user_id'], token, expires))
        
        # Send the email
        reset_link = f"http://127.0.0.1:5000/reset-password/{token}" # Use your domain in production
        msg = Message("Password Reset Request", recipients=[email])
        msg.body = f"Click the following link to reset your password: {reset_link}\nThis link will expire in one hour."
        mail.send(msg)

        conn.commit()
        return jsonify({'message': 'If an account with that email exists, a reset link has been sent.'}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    """Handles the final password reset submission."""
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('new_password')

    if not token or not new_password:
        return jsonify({'error': 'Token and new password are required'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = conn.cursor(dictionary=True)
    try:
        # Find the valid token
        query = "SELECT * FROM password_reset_tokens WHERE token = %s AND expires_at > %s"
        cursor.execute(query, (token, datetime.utcnow()))
        token_data = cursor.fetchone()

        if not token_data:
            return jsonify({'error': 'Invalid or expired token'}), 404
        
        user_id = token_data['user_id']
        
        # Hash the new password and update the user's record
        hashed_password = generate_password_hash(new_password)
        cursor.execute("UPDATE User SET password = %s WHERE user_id = %s", (hashed_password, user_id))
        
        # Invalidate the token by deleting it
        cursor.execute("DELETE FROM password_reset_tokens WHERE token = %s", (token,))
        
        conn.commit()
        return jsonify({'message': 'Password has been reset successfully!'}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()