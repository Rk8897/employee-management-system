"""Employee CRUD Operations"""
from flask import Blueprint, request, jsonify
from auth import verify_token

employees_bp = Blueprint('employees', __name__, url_prefix='/api/employees')

def require_auth(f):
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'status': 'error', 'message': 'No token'}), 401
        parts = auth_header.split()
        if len(parts) != 2 or parts[0] != 'Bearer':
            return jsonify({'status': 'error', 'message': 'Invalid format'}), 401
        token = parts[1]
        payload = verify_token(token)
        if not payload:
            return jsonify({'status': 'error', 'message': 'Invalid token'}), 401
        request.user = payload
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@employees_bp.route('', methods=['GET'])
@require_auth
def get_all_employees():
    try:
        from app import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        status = request.args.get('status', 'active')
        query = "SELECT e.*, d.name as department_name FROM employees e LEFT JOIN departments d ON e.department_id = d.id WHERE e.status = %s ORDER BY e.created_at DESC"
        cursor.execute(query, (status,))
        employees = cursor.fetchall()
        for emp in employees:
            if emp.get('join_date'):
                emp['join_date'] = emp['join_date'].strftime('%Y-%m-%d')
            if emp.get('created_at'):
                emp['created_at'] = emp['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        conn.close()
        return jsonify({'status': 'success', 'count': len(employees), 'employees': employees}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@employees_bp.route('/<int:emp_id>', methods=['GET'])
@require_auth
def get_employee(emp_id):
    try:
        from app import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT e.*, d.name as department_name FROM employees e LEFT JOIN departments d ON e.department_id = d.id WHERE e.id = %s", (emp_id,))
        employee = cursor.fetchone()
        conn.close()
        if not employee:
            return jsonify({'status': 'error', 'message': 'Not found'}), 404
        if employee.get('join_date'):
            employee['join_date'] = employee['join_date'].strftime('%Y-%m-%d')
        return jsonify({'status': 'success', 'employee': employee}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@employees_bp.route('', methods=['POST'])
@require_auth
def create_employee():
    try:
        data = request.get_json()
        required = ['name', 'email', 'department_id']
        if not all(f in data for f in required):
            return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400
        from app import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM employees WHERE email = %s", (data['email'],))
        if cursor.fetchone():
            conn.close()
            return jsonify({'status': 'error', 'message': 'Email exists'}), 400
        cursor.execute("INSERT INTO employees (name, email, phone, department_id, salary, join_date, status) VALUES (%s, %s, %s, %s, %s, %s, %s)", (data['name'], data['email'], data.get('phone'), data['department_id'], data.get('salary'), data.get('join_date'), data.get('status', 'active')))
        emp_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return jsonify({'status': 'success', 'employee_id': emp_id}), 201
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@employees_bp.route('/<int:emp_id>', methods=['PUT'])
@require_auth
def update_employee(emp_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'No data'}), 400
        from app import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        fields = []
        params = []
        for field in ['name', 'email', 'phone', 'department_id', 'salary', 'join_date', 'status']:
            if field in data:
                fields.append(f"{field} = %s")
                params.append(data[field])
        if not fields:
            conn.close()
            return jsonify({'status': 'error', 'message': 'No fields'}), 400
        params.append(emp_id)
        cursor.execute(f"UPDATE employees SET {', '.join(fields)} WHERE id = %s", params)
        conn.commit()
        conn.close()
        return jsonify({'status': 'success', 'message': 'Updated'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@employees_bp.route('/<int:emp_id>', methods=['DELETE'])
@require_auth
def delete_employee(emp_id):
    try:
        from app import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE employees SET status = 'inactive' WHERE id = %s", (emp_id,))
        conn.commit()
        conn.close()
        return jsonify({'status': 'success', 'message': 'Deactivated'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@employees_bp.route('/stats', methods=['GET'])
@require_auth
def get_stats():
    try:
        from app import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as total FROM employees WHERE status = 'active'")
        total = cursor.fetchone()['total']
        cursor.execute("SELECT d.name, COUNT(e.id) as count FROM departments d LEFT JOIN employees e ON d.id = e.department_id AND e.status = 'active' GROUP BY d.id, d.name")
        by_dept = cursor.fetchall()
        conn.close()
        return jsonify({'status': 'success', 'stats': {'total_active': total, 'by_department': by_dept}}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
