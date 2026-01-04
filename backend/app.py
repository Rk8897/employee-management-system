# backend/app.py
from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
import pymysql

# ------------------------
# Initialize Flask app
# ------------------------
app = Flask(__name__)
app.config.from_object(Config)
CORS(app, resources={r"/*": {"origins": "*"}})

# ------------------------
# Database connection helper
# ------------------------
def get_db_connection():
    try:
        conn = pymysql.connect(
            host="localhost",
            user="root",
            password="8897",
            database="employee_db",
            cursorclass=pymysql.cursors.DictCursor,
            port=3306
        )
        return conn
    except Exception as e:
        print("❌ Database connection failed:", e)
        return None

# Optional: test connection on app start
conn = get_db_connection()
if conn:
    print("✅ Database connected successfully!")
    conn.close()
else:
    print("❌ Could not connect to database!")

# ------------------------
# Import and register blueprints
# ------------------------
# Adjust imports for running inside backend folder
from auth import auth_bp
from employees import employees_bp  # <- changed import

app.register_blueprint(auth_bp)
app.register_blueprint(employees_bp)

# ------------------------
# Basic routes
# ------------------------
@app.route('/')
def home():
    return jsonify({
        'message': 'Employee Management System API',
        'status': 'running',
        'version': '1.0',
        'endpoints': {
            'GET /': 'API information',
            'GET /health': 'Health check',
            'GET /test-db': 'Database connection test',
            'POST /api/auth/login': 'Login',
            'GET /api/auth/verify': 'Verify token',
            'GET /api/employees': 'Get all employees',
            'GET /api/employees/<id>': 'Get single employee',
            'POST /api/employees': 'Create employee',
            'PUT /api/employees/<id>': 'Update employee',
            'DELETE /api/employees/<id>': 'Delete employee',
            'GET /api/employees/stats': 'Get statistics'
        }
    })

@app.route('/health')
def health():
    conn = get_db_connection()
    db_status = 'connected' if conn else 'disconnected'
    if conn:
        conn.close()
    return jsonify({'status': 'healthy', 'database': db_status, 'version': '1.0'})

@app.route('/test-db')
def test_db():
    conn = get_db_connection()
    if not conn:
        return jsonify({'status': 'error', 'message': 'Could not connect to database'}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION() as version")
        version = cursor.fetchone()

        # Safe table counts
        tables = {}
        for table in ['departments', 'employees', 'admin_users']:
            cursor.execute(f"SHOW TABLES LIKE '{table}'")
            if cursor.fetchone():
                cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                tables[table] = cursor.fetchone()['count']
            else:
                tables[table] = 0

        conn.close()

        return jsonify({
            'status': 'success',
            'message': 'Database connected successfully',
            'mysql_version': version['version'],
            'tables': tables
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ------------------------
# Run app
# ------------------------
if __name__ == '__main__':
    print("="*70)
    print("🚀 Employee Management System API")
    print("="*70)
    print(f"📊 Database: {Config.DB_NAME}")
    print(f"🔧 Debug Mode: {Config.DEBUG}")
    print("="*70)
    print("\n📍 API running on: http://localhost:5000\n")
    app.run(debug=Config.DEBUG, port=5000)
