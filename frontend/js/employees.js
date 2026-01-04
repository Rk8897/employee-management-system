// Employee CRUD Operations - Complete Version

let currentEmployeeId = null;

window.showAddEmployeeModal = function() {
    currentEmployeeId = null;
    document.getElementById('modalTitle').textContent = 'Add Employee';
    document.getElementById('employeeForm').reset();
    document.getElementById('employeeId').value = '';
    document.getElementById('employeeModal').classList.remove('hidden');
}

window.closeEmployeeModal = function() {
    const modal = document.getElementById('employeeModal');
    if (modal) {
        modal.classList.add('hidden');
        document.getElementById('employeeForm').reset();
        currentEmployeeId = null;
    }
}

window.editEmployee = async function(id) {
    try {
        const response = await api.getEmployee(id);
        if (response.status === 'success') {
            const emp = response.employee;
            currentEmployeeId = id;
            document.getElementById('modalTitle').textContent = 'Edit Employee';
            document.getElementById('employeeId').value = id;
            document.getElementById('empName').value = emp.name;
            document.getElementById('empEmail').value = emp.email;
            document.getElementById('empPhone').value = emp.phone || '';
            document.getElementById('empDepartment').value = emp.department_id;
            document.getElementById('empSalary').value = emp.salary || '';
            document.getElementById('empJoinDate').value = emp.join_date || '';
            document.getElementById('employeeModal').classList.remove('hidden');
        }
    } catch (error) {
        console.error('Error loading employee:', error);
        showAlert('Failed to load employee details', 'error');
    }
}

window.deleteEmployee = async function(id) {
    if (!confirm('Are you sure you want to delete this employee?')) {
        return;
    }
    try {
        const response = await api.deleteEmployee(id);
        if (response.status === 'success') {
            showAlert('Employee deleted successfully', 'success');
            await loadEmployees();
            await loadStats();
        }
    } catch (error) {
        console.error('Error deleting employee:', error);
        showAlert('Failed to delete employee: ' + error.message, 'error');
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('employeeForm');
    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            await saveEmployee();
        });
    }

    const modal = document.getElementById('employeeModal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                window.closeEmployeeModal();
            }
        });
    }
});

async function saveEmployee() {
    const saveBtn = document.getElementById('saveBtn');
    const originalText = saveBtn.textContent;
    try {
        saveBtn.disabled = true;
        saveBtn.textContent = 'Saving...';
        const employeeData = {
            name: document.getElementById('empName').value.trim(),
            email: document.getElementById('empEmail').value.trim(),
            phone: document.getElementById('empPhone').value.trim(),
            department_id: parseInt(document.getElementById('empDepartment').value),
            salary: parseFloat(document.getElementById('empSalary').value) || null,
            join_date: document.getElementById('empJoinDate').value || null,
            status: 'active'
        };
        if (!employeeData.name || !employeeData.email || !employeeData.department_id) {
            throw new Error('Please fill in all required fields');
        }
        let response;
        if (currentEmployeeId) {
            response = await api.updateEmployee(currentEmployeeId, employeeData);
        } else {
            response = await api.createEmployee(employeeData);
        }
        if (response.status === 'success') {
            showAlert(currentEmployeeId ? 'Employee updated successfully' : 'Employee created successfully', 'success');
            window.closeEmployeeModal();
            await loadEmployees();
            await loadStats();
        } else {
            throw new Error(response.message || 'Failed to save employee');
        }
    } catch (error) {
        console.error('Error saving employee:', error);
        showAlert('Failed to save employee: ' + error.message, 'error');
    } finally {
        saveBtn.disabled = false;
        saveBtn.textContent = originalText;
    }
}
