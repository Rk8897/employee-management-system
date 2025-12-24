// API Configuration
const API_BASE_URL = 'http://localhost:5000';

// API Helper Class
class API {
    constructor() {
        this.baseURL = API_BASE_URL;
    }

    // Get auth token from localStorage
    getToken() {
        return localStorage.getItem('token');
    }

    // Set auth token
    setToken(token) {
        localStorage.setItem('token', token);
    }

    // Remove auth token
    removeToken() {
        localStorage.removeItem('token');
    }

    // Get headers with auth token
    getHeaders(includeAuth = true) {
        const headers = {
            'Content-Type': 'application/json'
        };

        if (includeAuth) {
            const token = this.getToken();
            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }
        }

        return headers;
    }

    // Generic fetch wrapper
    async request(endpoint, options = {}) {
        try {
            const url = `${this.baseURL}${endpoint}`;
            const response = await fetch(url, {
                ...options,
                headers: this.getHeaders(options.includeAuth !== false)
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || 'Request failed');
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    // Auth APIs
    async login(username, password) {
        return this.request('/api/auth/login', {
            method: 'POST',
            body: JSON.stringify({ username, password }),
            includeAuth: false
        });
    }

    async verifyToken() {
        return this.request('/api/auth/verify', {
            method: 'GET'
        });
    }

    // Employee APIs
    async getEmployees(filters = {}) {
        const params = new URLSearchParams(filters);
        const query = params.toString() ? `?${params.toString()}` : '';
        return this.request(`/api/employees${query}`, {
            method: 'GET'
        });
    }

    async getEmployee(id) {
        return this.request(`/api/employees/${id}`, {
            method: 'GET'
        });
    }

    async createEmployee(employeeData) {
        return this.request('/api/employees', {
            method: 'POST',
            body: JSON.stringify(employeeData)
        });
    }

    async updateEmployee(id, employeeData) {
        return this.request(`/api/employees/${id}`, {
            method: 'PUT',
            body: JSON.stringify(employeeData)
        });
    }

    async deleteEmployee(id) {
        return this.request(`/api/employees/${id}`, {
            method: 'DELETE'
        });
    }

    async getStats() {
        return this.request('/api/employees/stats', {
            method: 'GET'
        });
    }
}

// Create global API instance
const api = new API();