// Dashboard Main Logic
document.addEventListener('DOMContentLoaded', async function() {
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

function loadUserInfo() {
    const userStr = localStorage.getItem('user');
    if (userStr) {
        const user = JSON.parse(userStr);
        document.getElementById('userName').textContent = user.username || 'Admin';
    }
}

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
    }
}

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
        const status = document.getElementById('statusFilter').value;
        const search = document.getElementById('searchInput').value;

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
        }
    } catch (error) {
        console.error('Error loading employees:', error);
        loading.classList.add('hidden');
        showAlert('Failed to load employees: ' + error.message, 'error');
    }
}

function displayEmployees(employees) {
    const tbody = document.getElementById('employeesBody');
    tbody.innerHTML = '';

    employees.forEach(emp => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><strong>${emp.name}</strong></td>
            <td>${emp.email}</td>
            <td>${emp.phone || '-'}</td>
            <td>${emp.department_name || '-'}</td>
            <td>₹${emp.salary ? emp.salary.toLocaleString() : '-'}</td>
            <td>${emp.join_date || '-'}</td>
            <td>
                <span class="status-badge status-${emp.status}">
                    ${emp.status}
                </span>
            </td>
            <td>
                <button class="action-btn action-edit" onclick="editEmployee(${emp.id})">
                    ✏️ Edit
                </button>
                <button class="action-btn action-delete" onclick="deleteEmployee(${emp.id})">
                    🗑️ Delete
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function setupEventListeners() {
    // Search input
    const searchInput = document.getElementById('searchInput');
    searchInput.addEventListener('input', debounce(loadEmployees, 500));

    // Status filter
    const statusFilter = document.getElementById('statusFilter');
    statusFilter.addEventListener('change', loadEmployees);
}

// Debounce function for search
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function showAlert(message, type = 'info') {
    const alert = document.getElementById('alert');
    alert.textContent = message;
    alert.className = `alert alert-${type}`;
    alert.classList.remove('hidden');

    // Auto hide after 5 seconds
    setTimeout(() => {
        alert.classList.add('hidden');
    }, 5000);
}

function hideAlert() {
    const alert = document.getElementById('alert');
    alert.classList.add('hidden');
}