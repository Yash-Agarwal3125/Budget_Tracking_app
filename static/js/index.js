// Authentication App JavaScript
// Handles form switching, validation, and API communication

document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const loginForm = document.getElementById('login-form');
    const signupForm = document.getElementById('signup-form');
    const showSignupLink = document.getElementById('show-signup');
    const showLoginLink = document.getElementById('show-login');
    const loginFormElement = document.getElementById('loginFormElement');
    const signupFormElement = document.getElementById('signupFormElement');

    // --- API Endpoints ---
    const API_BASE_URL = 'http://127.0.0.1:5000/api'; // Your Flask server address

    // Form switching functionality
    showSignupLink.addEventListener('click', function(e) {
        e.preventDefault();
        switchToSignup();
    });

    showLoginLink.addEventListener('click', function(e) {
        e.preventDefault();
        switchToLogin();
    });

    function switchToSignup() {
        loginForm.classList.remove('active');
        signupForm.classList.add('active');
        clearAllErrors();
        clearAllSuccessMessages();
        loginFormElement.reset();
        signupFormElement.reset();
    }

    function switchToLogin() {
        signupForm.classList.remove('active');
        loginForm.classList.add('active');
        clearAllErrors();
        clearAllSuccessMessages();
        loginFormElement.reset();
        signupFormElement.reset();
    }

    // --- Signup form submission ---
    signupFormElement.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const username = document.getElementById('signup-name').value.trim();
        const email = document.getElementById('signup-email').value.trim();
        const password = document.getElementById('signup-password').value.trim();
        const confirmPassword = document.getElementById('confirm-password').value.trim();
        
        clearSignupErrors();
        
        let isValid = true;
        // (Your existing validation logic for name, email, password, confirmPassword goes here...)
        // For brevity, I am assuming your validation logic is sound.
        if (!username || !email || !password || password !== confirmPassword) {
            // A simple check, use your detailed validation from before
            alert("Please fill all fields correctly.");
            isValid = false;
        }

        if (isValid) {
            const userData = {
                username: username,
                email: email,
                password: password
            };

            fetch(`${API_BASE_URL}/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(userData),
            })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    showSuccessMessage('signup-success', data.message + ' You can now sign in.');
                    setTimeout(switchToLogin, 2000); // Switch to login form after 2 seconds
                } else {
                    // Show error from backend, e.g., "email already exists"
                    showError('signup-email-error', data.error || 'An unknown error occurred.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showError('signup-email-error', 'Could not connect to the server.');
            });
        }
    });

    // --- Login form submission ---
    loginFormElement.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const email = document.getElementById('login-email').value.trim();
        const password = document.getElementById('login-password').value.trim();
        
        clearLoginErrors();
        
        let isValid = true;
        // (Your existing validation logic for email and password goes here...)
        if (!email || !password) {
            alert("Please fill all fields.");
            isValid = false;
        }

        if (isValid) {
            const loginData = {
                email: email,
                password: password
            };

            fetch(`${API_BASE_URL}/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(loginData),
            })
            .then(response => response.json())
            .then(data => {
                if (data.message === 'Login successful') {
                    showSuccessMessage('login-success', 'Login successful! Redirecting...');
                    // Redirect to a new dashboard page after successful login
                    window.location.href = '/dashboard'; // We will create this page next
                } else {
                    showError('login-email-error', data.error || 'Invalid credentials.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showError('login-email-error', 'Could not connect to the server.');
            });
        }
    });

    // --- All your utility functions (isValidEmail, showError, etc.) go here ---
    // I've omitted them for brevity but you should keep them.
    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
    
    function showError(elementId, message) {
        const errorElement = document.getElementById(elementId);
        if (errorElement) errorElement.textContent = message;
    }
    
    function showSuccessMessage(elementId, message) {
        const successElement = document.getElementById(elementId);
        if (successElement) {
            successElement.textContent = message;
            successElement.classList.add('show');
            setTimeout(() => successElement.classList.remove('show'), 5000);
        }
    }
    
    function clearLoginErrors() {
        showError('login-email-error', '');
        showError('login-password-error', '');
    }

    function clearSignupErrors() {
        showError('signup-name-error', '');
        showError('signup-email-error', '');
        showError('signup-password-error', '');
        showError('confirm-password-error', '');
    }

    function clearAllErrors() {
        clearLoginErrors();
        clearSignupErrors();
    }

    function clearAllSuccessMessages() {
        const loginSuccess = document.getElementById('login-success');
        const signupSuccess = document.getElementById('signup-success');
        if (loginSuccess) loginSuccess.classList.remove('show');
        if (signupSuccess) signupSuccess.classList.remove('show');
    }
});