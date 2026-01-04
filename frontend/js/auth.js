// Auth Handler for Login Page
document.addEventListener("DOMContentLoaded", function() {
    checkAuth();
    
    const loginForm = document.getElementById("loginForm");
    
    if (loginForm) {
        const usernameInput = document.getElementById("username");
        const passwordInput = document.getElementById("password");
        const loginBtn = document.getElementById("loginBtn");
        const btnText = document.getElementById("btnText");
        const btnSpinner = document.getElementById("btnSpinner");
        const alertDiv = document.getElementById("alert");
        
        loginForm.addEventListener("submit", async function(e) {
            e.preventDefault();
            await handleLogin();
        });
        
        usernameInput.value = "admin";
        passwordInput.value = "admin123";
        
        async function handleLogin() {
            const username = usernameInput.value.trim();
            const password = passwordInput.value.trim();
            
            if (!username || !password) {
                showAlert("Please enter both username and password", "error");
                return;
            }
            
            setLoading(true);
            hideAlert();
            
            try {
                const response = await api.login(username, password);
                
                if (response.status === "success") {
                    api.setToken(response.token);
                    localStorage.setItem("user", JSON.stringify(response.user));
                    showAlert("Login successful! Redirecting...", "success");
                    
                    setTimeout(function() {
                        window.location.href = "dashboard.html";
                    }, 1000);
                } else {
                    showAlert(response.message || "Login failed", "error");
                    setLoading(false);
                }
            } catch (error) {
                console.error("Login error:", error);
                showAlert(error.message || "Login failed. Please check your credentials.", "error");
                setLoading(false);
            }
        }
        
        function setLoading(loading) {
            if (loading) {
                loginBtn.disabled = true;
                btnText.classList.add("hidden");
                btnSpinner.classList.remove("hidden");
            } else {
                loginBtn.disabled = false;
                btnText.classList.remove("hidden");
                btnSpinner.classList.add("hidden");
            }
        }
        
        function showAlert(message, type) {
            alertDiv.textContent = message;
            alertDiv.className = "alert alert-" + type;
            alertDiv.classList.remove("hidden");
        }
        
        function hideAlert() {
            alertDiv.classList.add("hidden");
        }
    }
    
    function checkAuth() {
        const token = api.getToken();
        if (token && window.location.pathname.includes("login.html")) {
            window.location.href = "dashboard.html";
        }
    }
});

function isAuthenticated() {
    return !!api.getToken();
}

function logout() {
    api.removeToken();
    localStorage.removeItem("user");
    window.location.href = "login.html";
}
