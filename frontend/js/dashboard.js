// ==============================
// Dashboard Main Logic
// ==============================
document.addEventListener('DOMContentLoaded', async function () {
    // Check authentication
    if (!isAuthenticated()) {
        window.location.href = 'login.html';
        return;
    }

    // Load user info
    loadUserInfo();

    // Load initial data
    await loadStats();
    await loadEmployees();

    // Set up event listeners
    setupEventListeners();
});

// ==============================
// Load User Info
// ==============================
function loadUserInfo() {
    const userStr = localStorage.getItem('user');
    if (userStr) {
        const user = JSON.parse(userStr);
        document.getElementById('userName').textContent = user.username || 'Admin';
    }
}

// ==============================
// Load Stats
// ==============================
async function loadStats() {
    try {
        const response = await api.getStats();
        if (response.status === 'success') {
            const stats = response.stats;
            document.getElementById('totalActive').textContent = stats.total_active || 0;
            document.getElementById('totalInactive').textContent = stats.total_inactive || 0;
            document.getElementById('recentHires').textContent = stats.recent_hires_30_days || 0;
        }
    } catch (error) {
        console.error('Error loading stats:', error);
        showAlert('Failed to load stats', 'error');
    }
}

// ==============================
// Load Employees
// ==============================
async function loadEmployees() {
    const loading = document.getElementById('loading');
    const emptyState = document.getElementById('emptyState');
    const tableContainer = document.querySelector('.table-container');
    const tbody = document.getElementById('employeesBody');

    // Show loading
    loading.classList.remove('hidden');
    tableContainer.classList.add('hidden');
    emptyState.classList.add('hidden');

    try {
        // Get filter values
        const status = document.getElementById('statusFilter')?.value;
        const search = document.getElementById('searchInput')?.value;

        const filters = {};
        if (status) filters.status = status;
        if (search) filters.search = search;

        const response = await api.getEmployees(filters);

        // Hide loading
        loading.classList.add('hidden');

        if (response.status === 'success') {
            const employees = response.employees;

            if (employees.length === 0) {
                emptyState.classList.remove('hidden');
            } else {
                tableContainer.classList.remove('hidden');
                displayEmployees(employees);
            }
        } else {
            showAlert('Failed to load employees', 'error');
        }
    } catch (error) {
        console.error('Error loading employees:', error);
        loading.classList.add('hidden');
        showAlert('Failed to load employees: ' + error.message, 'error');
    }
}

// ==============================
// Display Employees in Table
// ==============================
function displayEmployees(employees) {
    const tbody = document.getElementById('employeesBody');
    tbody.innerHTML = '';

    employees.forEach(emp => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><strong>${emp.id}</strong></td>
            <td>${emp.name}</td>
            <td>${emp.email}</td>
            <td>${emp.position}</td>
            <td>Rs ${emp.salary}</td>
            <td>${emp.joinedDate}</td>
            <td>
                <span class="status-badge status-${emp.status.toLowerCase()}">
                    ${emp.status}
                </span>
            </td>
            <td>
                <button class="action-btn action-edit" onclick="editEmployee(${emp.id})">
                    Edit
                </button>
                <button class="action-btn action-delete" onclick="deleteEmployee(${emp.id})">
                    Delete
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// ==============================
// Event Listeners
// ==============================
function setupEventListeners() {
    // Search input
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(loadEmployees, 500));
    }

    // Status filter
    const statusFilter = document.getElementById('statusFilter');
    if (statusFilter) {
        statusFilter.addEventListener('change', loadEmployees);
    }
}

// ==============================
// Debounce Helper
// ==============================
function debounce(func, wait) {
    let timeout;
    return function (...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func(...args), wait);
    };
}

// ==============================
// Alerts
// ==============================
function showAlert(message, type = 'info') {
    const alert = document.getElementById('alert');
    alert.textContent = message;
    alert.className = `alert alert-${type}`;
    alert.classList.remove('hidden');

    setTimeout(() => {
        alert.classList.add('hidden');
    }, 5000);
}

function hideAlert() {
    const alert = document.getElementById('alert');
    alert.classList.add('hidden');
}
