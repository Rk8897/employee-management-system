from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
import pymysql

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
CORS(app, resources={r"/*": {"origins": "*"}})

# Database connection helper
def get_db_connection():
    import pymysql
    try:
        connection = pymysql.connect(
            host="localhost",
            user="root",
            password="8897",   # hardcoded temporary
            database="employee_db",
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Exception as e:
        print("❌ Database connection error:", e)
        return None


# Import and register blueprints
from auth import auth_bp
app.register_blueprint(auth_bp)
from employees import employees_bp
app.register_blueprint(employees_bp)

# Basic routes
@app.route('/')
def home():
    """API home - shows available endpoints"""
    return jsonify({
        'message': 'Employee Management System API',
        'status': 'running',
        'version': '1.0',
        'endpoints': {
            'GET /': 'API information',
            'GET /health': 'Health check',
            'GET /test-db': 'Database connection test',
            'POST /api/auth/login': 'Login (username, password)',
            'GET /api/auth/verify': 'Verify token (Authorization header)',
            'GET /api/employees': 'Get all employees (with filters)',
            'GET /api/employees/<id>': 'Get single employee',
            'POST /api/employees': 'Create employee',
            'PUT /api/employees/<id>': 'Update employee',
            'DELETE /api/employees/<id>': 'Delete employee',
            'GET /api/employees/stats': 'Get statistics'
        }
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    conn = get_db_connection()
    db_status = 'connected' if conn else 'disconnected'
    if conn:
        conn.close()
    
    return jsonify({
        'status': 'healthy',
        'database': db_status,
        'version': '1.0'
    })

@app.route('/test-db')
def test_db():
    """Test database connection"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'status': 'error',
                'message': 'Could not connect to database'
            }), 500
        
        cursor = conn.cursor()
        
        # Get MySQL version
        cursor.execute("SELECT VERSION() as version")
        version = cursor.fetchone()
        
        # Count departments
        cursor.execute("SELECT COUNT(*) as count FROM departments")
        dept_count = cursor.fetchone()
        
        # Count employees
        cursor.execute("SELECT COUNT(*) as count FROM employees")
        emp_count = cursor.fetchone()
        
        # Count admin users
        cursor.execute("SELECT COUNT(*) as count FROM admin_users")
        admin_count = cursor.fetchone()
        
        conn.close()
        
        return jsonify({
            'status': 'success',
            'message': 'Database connected successfully',
            'mysql_version': version['version'],
            'tables': {
                'departments': dept_count['count'],
                'employees': emp_count['count'],
                'admin_users': admin_count['count']
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# Run app
if __name__ == '__main__':
    print("=" * 70)
    print("🚀 Employee Management System API - Day 2")
    print("=" * 70)
    print(f"📊 Database: {Config.DB_NAME}")
    print(f"🔧 Debug Mode: {Config.DEBUG}")
    print("=" * 70)
    print("\n📍 API running on: http://localhost:5000")
    print("\n🔑 Authentication Endpoints:")
    print("   POST   /api/auth/login      - Login with username & password")
    print("   GET    /api/auth/verify     - Verify JWT token")
    print("\n⚡ Quick Test:")
    print("   curl -X POST http://localhost:5000/api/auth/login \\")
    print('        -H "Content-Type: application/json" \\')
    print('        -d "{\\"username\\":\\"admin\\",\\"password\\":\\"admin123\\"}"')
    print("\n" + "=" * 70)
    print("Press CTRL+C to quit\n")
    
    app.run(debug=Config.DEBUG, port=5000)