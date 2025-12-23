"""
Authentication routes and utilities
"""
from flask import Blueprint, request, jsonify
import bcrypt
import jwt
import datetime
from config import Config

# Create Blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

def hash_password(password):
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password, hashed_password):
    """Verify password against hash"""
    return bcrypt.checkpw(
        password.encode('utf-8'), 
        hashed_password.encode('utf-8')
    )

def generate_token(user_id, username):
    """Generate JWT token"""
    payload = {
        'user_id': user_id,
        'username': username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24),
        'iat': datetime.datetime.utcnow()
    }
    token = jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm='HS256')
    return token

def verify_token(token):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login endpoint"""
    try:
        # Get request data
        data = request.get_json()
        
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Username and password are required'
            }), 400
        
        username = data['username']
        password = data['password']
        
        # Import here to avoid circular import
        from app import get_db_connection
        
        # Get user from database
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'status': 'error',
                'message': 'Database connection failed'
            }), 500
        
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM admin_users WHERE username = %s",
            (username,)
        )
        user = cursor.fetchone()
        conn.close()
        
        # Check if user exists
        if not user:
            return jsonify({
                'status': 'error',
                'message': 'Invalid username or password'
            }), 401
        
        # For now, we're using plain text passwords (we'll hash them properly later)
        # In production, always use hashed passwords!
        if password != user['password']:
            return jsonify({
                'status': 'error',
                'message': 'Invalid username or password'
            }), 401
        
        # Generate token
        token = generate_token(user['id'], user['username'])
        
        return jsonify({
            'status': 'success',
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email']
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@auth_bp.route('/verify', methods=['GET'])
def verify():
    """Verify token endpoint"""
    try:
        # Get token from header
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({
                'status': 'error',
                'message': 'No token provided'
            }), 401
        
        # Extract token (format: "Bearer <token>")
        parts = auth_header.split()
        if len(parts) != 2 or parts[0] != 'Bearer':
            return jsonify({
                'status': 'error',
                'message': 'Invalid token format'
            }), 401
        
        token = parts[1]
        
        # Verify token
        payload = verify_token(token)
        if not payload:
            return jsonify({
                'status': 'error',
                'message': 'Invalid or expired token'
            }), 401
        
        return jsonify({
            'status': 'success',
            'message': 'Token is valid',
            'user': {
                'id': payload['user_id'],
                'username': payload['username']
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@auth_bp.route('/change-password', methods=['POST'])
def change_password():
    """Change password endpoint"""
    try:
        # Get token
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({
                'status': 'error',
                'message': 'No token provided'
            }), 401
        
        token = auth_header.split()[1]
        payload = verify_token(token)
        if not payload:
            return jsonify({
                'status': 'error',
                'message': 'Invalid token'
            }), 401
        
        # Get request data
        data = request.get_json()
        if not data or 'old_password' not in data or 'new_password' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Old password and new password are required'
            }), 400
        
        old_password = data['old_password']
        new_password = data['new_password']
        
        # Get user
        from app import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM admin_users WHERE id = %s",
            (payload['user_id'],)
        )
        user = cursor.fetchone()
        
        # Verify old password
        if old_password != user['password']:
            conn.close()
            return jsonify({
                'status': 'error',
                'message': 'Old password is incorrect'
            }), 401
        
        # Update password
        cursor.execute(
            "UPDATE admin_users SET password = %s WHERE id = %s",
            (new_password, payload['user_id'])
        )
        conn.commit()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'message': 'Password changed successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500