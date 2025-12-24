# Employee Management System

A full-stack web application for managing employee records with a modern, responsive interface.

## 🚀 Features

- **User Authentication** - Secure login system with JWT tokens
- **Employee CRUD Operations** - Create, Read, Update, and Delete employee records
- **Department Management** - Organize employees by departments
- **Search & Filter** - Find employees quickly with search and department filters
- **Dashboard Statistics** - View total employees, departments, and average salary
- **Responsive Design** - Works seamlessly on desktop and mobile devices
- **Modern UI** - Clean interface with gradient designs and smooth animations

## 🛠️ Tech Stack

### Frontend
- HTML5, CSS3, JavaScript (ES6+)
- Responsive design with Flexbox/Grid
- Fetch API for HTTP requests
- Modern gradient-based UI

### Backend
- Python 3.x
- Flask (Web framework)
- MySQL (Database)
- JWT for authentication
- RESTful API architecture

## 📋 Prerequisites

- Python 3.8 or higher
- MySQL 5.7 or higher
- pip (Python package manager)

## 🔧 Installation

### 1. Clone the repository
```bash
git clone https://github.com/Rk8897/employee-management-system.git
cd employee-management-system
```

### 2. Set up Python virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install flask flask-cors mysql-connector-python pyjwt
```

### 4. Set up MySQL Database
```sql
CREATE DATABASE employee_management;

USE employee_management;

CREATE TABLE departments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20),
    department_id INT,
    salary DECIMAL(10,2),
    join_date DATE,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(id)
);

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample departments
INSERT INTO departments (name, description) VALUES
('Engineering', 'Software development and IT'),
('Product', 'Product management and strategy'),
('Design', 'UI/UX and graphic design'),
('Marketing', 'Marketing and communications'),
('Sales', 'Sales and business development'),
('HR', 'Human resources');
```

### 5. Configure database connection
Edit `backend/app.py` and update the database credentials:
```python
db_config = {
    'host': 'localhost',
    'user': 'your_username',
    'password': 'your_password',
    'database': 'employee_management'
}
```

### 6. Run the application
```bash
# Start the backend server
cd backend
python app.py

# The server will run on http://localhost:5000
```

### 7. Open the frontend
Open `frontend/login.html` in your browser or use a local server:
```bash
# Using Python's built-in server
cd frontend
python -m http.server 8000

# Open http://localhost:8000/login.html
```

## 📁 Project Structure

```
employee-management-system/
├── backend/
│   ├── app.py              # Main Flask application
│   └── employees.py        # Employee management logic
├── frontend/
│   ├── login.html          # Login page
│   ├── dashboard.html      # Main dashboard
│   ├── css/
│   │   ├── style.css
│   │   ├── login.css
│   │   └── dashboard.css
│   └── js/
│       ├── auth.js         # Authentication logic
│       ├── api.js          # API communication
│       ├── dashboard.js    # Dashboard functionality
│       └── employees.js    # Employee CRUD operations
├── employees.js            # Standalone employee operations
├── employees.py            # Python employee utilities
└── README.md
```

## 🔐 API Endpoints

### Authentication
- `POST /api/register` - Register new user
- `POST /api/login` - User login

### Employees
- `GET /api/employees` - Get all employees
- `GET /api/employees/:id` - Get employee by ID
- `POST /api/employees` - Create new employee
- `PUT /api/employees/:id` - Update employee
- `DELETE /api/employees/:id` - Delete employee

### Departments
- `GET /api/departments` - Get all departments
- `GET /api/departments/:id` - Get department by ID
- `POST /api/departments` - Create new department

### Statistics
- `GET /api/stats` - Get dashboard statistics

## 🎨 Features in Detail

### Employee Management
- Add new employees with complete information
- Edit existing employee details
- Delete employees with confirmation
- View employee cards with all details
- Filter by department
- Search by name, email, or position

### Dashboard
- Total employee count
- Number of departments
- Average salary calculation
- Quick access to all features

### Security
- JWT-based authentication
- Password encryption
- Protected API routes
- Session management

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 👤 Author

**Rohit Kemade**
- GitHub: [@Rk8897](https://github.com/Rk8897)

## 🙏 Acknowledgments

- Built as part of a full-stack development learning project
- Inspired by modern employee management systems
- Thanks to the Flask and MySQL communities

## 📞 Support

For support, email kemaderohit@gmail.com or open an issue in the repository.

---

**Note**: This is a learning project and may not be suitable for production use without additional security hardening and testing.
