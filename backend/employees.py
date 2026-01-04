"""
Employee CRUD Operations
"""
from flask import Blueprint, request, jsonify
from auth import verify_token
from datetime import datetime

# Create Blueprint
employees_bp = Blueprint('employees', __name__, url_prefix='/api/employees')

def require_auth(f):
    """Decorator to require authentication"""
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({
                'status': 'error',
                'message': 'No token provided'
            }), 401
        
        parts = auth_header.split()
        if len(parts) != 2 or parts[0] != 'Bearer':
            return jsonify({
                'status': 'error',
                'message': 'Invalid token format. Use: Bearer <token>'
            }), 401
        
        token = parts[1]
        payload = verify_token(token)
        if not payload:
            return jsonify({
                'status': 'error',
                'message': 'Invalid or expired token'
            }), 401
        
        request.user = payload
        return f(*args, **kwargs)
    
    decorated_function.__name__ = f.__name__
    return decorated_function

# ============================================================
# READ Operations
# ============================================================

@employees_bp.route('', methods=['GET'])
@require_auth
def get_all_employees():
    """
    Get all employees with optional filters
    GET /api/employees?department_id=1&status=active&search=john
    """
    try:
        from app import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get query parameters
        department_id = request.args.get('department_id')
        status = request.args.get('status', 'active')
        search = request.args.get('search', '')
        
        # Build query
        query = """
            SELECT 
                e.id, e.name, e.email, e.phone, 
                e.department_id, e.salary, e.join_date, 
                e.status, e.created_at,
                d.name as department_name
            FROM employees e
            LEFT JOIN departments d ON e.department_id = d.id
            WHERE 1=1
        """
        params = []
        
        if status:
            query += " AND e.status = %s"
            params.append(status)
        
        if department_id:
            query += " AND e.department_id = %s"
            params.append(department_id)
        
        if search:
            query += " AND (e.name LIKE %s OR e.email LIKE %s)"
            search_param = f"%{search}%"
            params.extend([search_param, search_param])
        
        query += " ORDER BY e.created_at DESC"
        
        cursor.execute(query, params)
        employees = cursor.fetchall()
        
        # Format dates
        for emp in employees:
            if emp['join_date']:
                emp['join_date'] = emp['join_date'].strftime('%Y-%m-%d')
            if emp['created_at']:
                emp['created_at'] = emp['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        
        conn.close()
        
        return jsonify({
            'status': 'success',
            'count': len(employees),
            'employees': employees
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@employees_bp.route('/<int:emp_id>', methods=['GET'])
@require_auth
def get_employee(emp_id):
    """
    Get single employee by ID
    GET /api/employees/1
    """
    try:
        from app import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                e.id, e.name, e.email, e.phone,
                e.department_id, e.salary, e.join_date,
                e.status, e.created_at, e.updated_at,
                d.name as department_name
            FROM employees e
            LEFT JOIN departments d ON e.department_id = d.id
            WHERE e.id = %s
        """, (emp_id,))
        
        employee = cursor.fetchone()
        conn.close()
        
        if not employee:
            return jsonify({
                'status': 'error',
                'message': 'Employee not found'
            }), 404
        
        # Format dates
        if employee['join_date']:
            employee['join_date'] = employee['join_date'].strftime('%Y-%m-%d')
        if employee['created_at']:
            employee['created_at'] = employee['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        if employee['updated_at']:
            employee['updated_at'] = employee['updated_at'].strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify({
            'status': 'success',
            'employee': employee
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# ============================================================
# CREATE Operation
# ============================================================

@employees_bp.route('', methods=['POST'])
@require_auth
def create_employee():
    """
    Create new employee
    POST /api/employees
    Body: {
        "name": "John Doe",
        "email": "john@company.com",
        "phone": "1234567890",
        "department_id": 1,
        "salary": 50000,
        "join_date": "2024-01-15"
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required = ['name', 'email', 'department_id']
        missing = [field for field in required if field not in data]
        if missing:
            return jsonify({
                'status': 'error',
                'message': f'Missing required fields: {", ".join(missing)}'
            }), 400
        
        from app import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if email exists
        cursor.execute("SELECT id FROM employees WHERE email = %s", (data['email'],))
        if cursor.fetchone():
            conn.close()
            return jsonify({
                'status': 'error',
                'message': 'Email already exists'
            }), 400
        
        # Check if department exists
        cursor.execute("SELECT id FROM departments WHERE id = %s", (data['department_id'],))
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'status': 'error',
                'message': 'Invalid department ID'
            }), 400
        
        # Insert employee
        cursor.execute("""
            INSERT INTO employees 
            (name, email, phone, department_id, salary, join_date, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            data['name'],
            data['email'],
            data.get('phone'),
            data['department_id'],
            data.get('salary'),
            data.get('join_date'),
            data.get('status', 'active')
        ))
        
        emp_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'message': 'Employee created successfully',
            'employee_id': emp_id
        }), 201
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# ============================================================
# UPDATE Operation
# ============================================================

@employees_bp.route('/<int:emp_id>', methods=['PUT'])
@require_auth
def update_employee(emp_id):
    """
    Update employee
    PUT /api/employees/1
    Body: {"salary": 60000, "phone": "9876543210"}
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No data provided'
            }), 400
        
        from app import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if employee exists
        cursor.execute("SELECT id FROM employees WHERE id = %s", (emp_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'status': 'error',
                'message': 'Employee not found'
            }), 404
        
        # Build update query
        fields = []
        params = []
        
        allowed_fields = ['name', 'email', 'phone', 'department_id', 'salary', 'join_date', 'status']
        for field in allowed_fields:
            if field in data:
                fields.append(f"{field} = %s")
                params.append(data[field])
        
        if not fields:
            conn.close()
            return jsonify({
                'status': 'error',
                'message': 'No valid fields to update'
            }), 400
        
        # Check department if updating
        if 'department_id' in data:
            cursor.execute("SELECT id FROM departments WHERE id = %s", (data['department_id'],))
            if not cursor.fetchone():
                conn.close()
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid department ID'
                }), 400
        
        params.append(emp_id)
        query = f"UPDATE employees SET {', '.join(fields)} WHERE id = %s"
        
        cursor.execute(query, params)
        conn.commit()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'message': 'Employee updated successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# ============================================================
# DELETE Operation
# ============================================================

@employees_bp.route('/<int:emp_id>', methods=['DELETE'])
@require_auth
def delete_employee(emp_id):
    """
    Soft delete employee (set status to inactive)
    DELETE /api/employees/1
    """
    try:
        from app import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if employee exists
        cursor.execute("SELECT id, status FROM employees WHERE id = %s", (emp_id,))
        employee = cursor.fetchone()
        
        if not employee:
            conn.close()
            return jsonify({
                'status': 'error',
                'message': 'Employee not found'
            }), 404
        
        if employee['status'] == 'inactive':
            conn.close()
            return jsonify({
                'status': 'error',
                'message': 'Employee already inactive'
            }), 400
        
        # Soft delete
        cursor.execute(
            "UPDATE employees SET status = 'inactive' WHERE id = %s",
            (emp_id,)
        )
        conn.commit()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'message': 'Employee deactivated successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# ============================================================
# STATISTICS
# ============================================================

@employees_bp.route('/stats', methods=['GET'])
@require_auth
def get_stats():
    """
    Get employee statistics
    GET /api/employees/stats
    """
    try:
        from app import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Total employees
        cursor.execute(
            "SELECT COUNT(*) as total FROM employees WHERE status = 'active'"
        )
        total = cursor.fetchone()['total']
        
        # By department
        cursor.execute("""
            SELECT 
                d.id, d.name, 
                COUNT(e.id) as employee_count
            FROM departments d
            LEFT JOIN employees e ON d.id = e.department_id 
                AND e.status = 'active'
            GROUP BY d.id, d.name
            ORDER BY employee_count DESC
        """)
        by_department = cursor.fetchall()
        
        # Recent hires (last 30 days)
        cursor.execute("""
            SELECT COUNT(*) as recent 
            FROM employees 
            WHERE join_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
                AND status = 'active'
        """)
        recent = cursor.fetchone()['recent']
        
        # Inactive employees
        cursor.execute(
            "SELECT COUNT(*) as inactive FROM employees WHERE status = 'inactive'"
        )
        inactive = cursor.fetchone()['inactive']
        
        conn.close()
        
        return jsonify({
            'status': 'success',
            'stats': {
                'total_active': total,
                'total_inactive': inactive,
                'recent_hires_30_days': recent,
                'by_department': by_department
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500