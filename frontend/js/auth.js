// Auth Handler for Login Page

// Wait for DOM to load
document.addEventListener('DOMContentLoaded', function() {
    // Check if already logged in
    checkAuth();

    // Get form elements
    const loginForm = document.getElementById('loginForm');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const loginBtn = document.getElementById('loginBtn');
    const btnText = document.getElementById('btnText');
    const btnSpinner = document.getElementById('btnSpinner');
    const alertDiv = document.getElementById('alert');

    // Handle form submission
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        await handleLogin();
    });

    // Auto-fill demo credentials (optional - for testing)
    usernameInput.value = 'admin';
    passwordInput.value = 'admin123';

    async function handleLogin() {
        const username = usernameInput.value.trim();
        const password = passwordInput.value.trim();

        // Validate inputs
        if (!username || !password) {
            showAlert('Please enter both username and password', 'error');
            return;
        }

        // Show loading state
        setLoading(true);
        hideAlert();

        try {
            // Call login API
            const response = await api.login(username, password);

            if (response.status === 'success') {
                // Save token
                api.setToken(response.token);
                
                // Save user info
                localStorage.setItem('user', JSON.stringify(response.user));

                // Show success message
                showAlert('Login successful! Redirecting...', 'success');

                // Redirect to dashboard after 1 second
                setTimeout(() => {
                    window.location.href = 'dashboard.html';
                }, 1000);
            } else {
                showAlert(response.message || 'Login failed', 'error');
                setLoading(false);
            }
        } catch (error) {
            console.error('Login error:', error);
            showAlert(error.message || 'Login failed. Please check your credentials.', 'error');
            setLoading(false);
        }
    }

    function setLoading(loading) {
        if (loading) {
            loginBtn.disabled = true;
            btnText.classList.add('hidden');
            btnSpinner.classList.remove('hidden');
        } else {
            loginBtn.disabled = false;
            btnText.classList.remove('hidden');
            btnSpinner.classList.add('hidden');
        }
    }

    function showAlert(message, type) {
        alertDiv.textContent = message;
        alertDiv.className = `alert alert-${type}`;
        alertDiv.classList.remove('hidden');
    }

    function hideAlert() {
        alertDiv.classList.add('hidden');
    }

    function checkAuth() {
        const token = api.getToken();
        if (token) {
            // Already logged in, redirect to dashboard
            window.location.href = 'dashboard.html';
        }
    }
});

// Utility function to check if user is authenticated
function isAuthenticated() {
    return !!api.getToken();
}

// Utility function to logout
function logout() {
    api.removeToken();
    localStorage.removeItem('user');
    window.location.href = 'login.html';
}
