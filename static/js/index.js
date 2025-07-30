// Authentication App JavaScript
// Handles form switching, validation, and user interactions

document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const loginForm = document.getElementById('login-form');
    const signupForm = document.getElementById('signup-form');
    const showSignupLink = document.getElementById('show-signup');
    const showLoginLink = document.getElementById('show-login');
    const loginFormElement = document.getElementById('loginFormElement');
    const signupFormElement = document.getElementById('signupFormElement');

    // Form switching functionality
    showSignupLink.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        switchToSignup();
    });

    showLoginLink.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        switchToLogin();
    });

    // Switch to signup form
    function switchToSignup() {
        loginForm.classList.remove('active');
        signupForm.classList.add('active');
        clearAllErrors();
        clearAllSuccessMessages();
        // Reset forms
        loginFormElement.reset();
        signupFormElement.reset();
    }

    // Switch to login form
    function switchToLogin() {
        signupForm.classList.remove('active');
        loginForm.classList.add('active');
        clearAllErrors();
        clearAllSuccessMessages();
        // Reset forms
        loginFormElement.reset();
        signupFormElement.reset();
    }

    // Login form validation and submission
    loginFormElement.addEventListener('submit', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        const email = document.getElementById('login-email').value.trim();
        const password = document.getElementById('login-password').value.trim();
        
        // Clear previous errors and states
        clearLoginErrors();
        
        let isValid = true;
        
        // Validate email
        if (!email) {
            showError('login-email-error', 'Email is required');
            setFieldState('login-email', 'error');
            isValid = false;
        } else if (!isValidEmail(email)) {
            showError('login-email-error', 'Please enter a valid email address');
            setFieldState('login-email', 'error');
            isValid = false;
        } else {
            setFieldState('login-email', 'success');
        }
        
        // Validate password
        if (!password) {
            showError('login-password-error', 'Password is required');
            setFieldState('login-password', 'error');
            isValid = false;
        } else {
            setFieldState('login-password', 'success');
        }
        
        // If validation passes, show success
        if (isValid) {
            showSuccessMessage('login-success', 'Login successful! Welcome back.');
            // Simulate loading state
            const submitBtn = loginFormElement.querySelector('button[type="submit"]');
            submitBtn.classList.add('loading');
            
            setTimeout(() => {
                submitBtn.classList.remove('loading');
            }, 1500);
        }
    });

    // Signup form validation and submission
    signupFormElement.addEventListener('submit', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        const name = document.getElementById('signup-name').value.trim();
        const email = document.getElementById('signup-email').value.trim();
        const password = document.getElementById('signup-password').value.trim();
        const confirmPassword = document.getElementById('confirm-password').value.trim();
        const termsAccepted = document.getElementById('terms-checkbox').checked;
        
        // Clear previous errors and states
        clearSignupErrors();
        
        let isValid = true;
        
        // Validate name
        if (!name) {
            showError('signup-name-error', 'Full name is required');
            setFieldState('signup-name', 'error');
            isValid = false;
        } else if (name.length < 2) {
            showError('signup-name-error', 'Name must be at least 2 characters long');
            setFieldState('signup-name', 'error');
            isValid = false;
        } else {
            setFieldState('signup-name', 'success');
        }
        
        // Validate email
        if (!email) {
            showError('signup-email-error', 'Email is required');
            setFieldState('signup-email', 'error');
            isValid = false;
        } else if (!isValidEmail(email)) {
            showError('signup-email-error', 'Please enter a valid email address');
            setFieldState('signup-email', 'error');
            isValid = false;
        } else {
            setFieldState('signup-email', 'success');
        }
        
        // Validate password
        if (!password) {
            showError('signup-password-error', 'Password is required');
            setFieldState('signup-password', 'error');
            isValid = false;
        } else if (password.length < 6) {
            showError('signup-password-error', 'Password must be at least 6 characters long');
            setFieldState('signup-password', 'error');
            isValid = false;
        } else {
            setFieldState('signup-password', 'success');
        }
        
        // Validate confirm password
        if (!confirmPassword) {
            showError('confirm-password-error', 'Please confirm your password');
            setFieldState('confirm-password', 'error');
            isValid = false;
        } else if (password !== confirmPassword) {
            showError('confirm-password-error', 'Passwords do not match');
            setFieldState('confirm-password', 'error');
            isValid = false;
        } else {
            setFieldState('confirm-password', 'success');
        }
        
        // Validate terms acceptance
        if (!termsAccepted) {
            showError('terms-error', 'You must agree to the Terms and Conditions');
            isValid = false;
        }
        
        // If validation passes, show success
        if (isValid) {
            showSuccessMessage('signup-success', 'Account created successfully! Welcome aboard.');
            // Simulate loading state
            const submitBtn = signupFormElement.querySelector('button[type="submit"]');
            submitBtn.classList.add('loading');
            
            setTimeout(() => {
                submitBtn.classList.remove('loading');
            }, 1500);
        }
    });

    // Real-time validation for better UX
    document.getElementById('login-email').addEventListener('blur', function() {
        const email = this.value.trim();
        if (email && !isValidEmail(email)) {
            showError('login-email-error', 'Please enter a valid email address');
            setFieldState('login-email', 'error');
        } else if (email && isValidEmail(email)) {
            clearError('login-email-error');
            setFieldState('login-email', 'success');
        }
    });

    document.getElementById('signup-email').addEventListener('blur', function() {
        const email = this.value.trim();
        if (email && !isValidEmail(email)) {
            showError('signup-email-error', 'Please enter a valid email address');
            setFieldState('signup-email', 'error');
        } else if (email && isValidEmail(email)) {
            clearError('signup-email-error');
            setFieldState('signup-email', 'success');
        }
    });

    document.getElementById('signup-password').addEventListener('input', function() {
        const password = this.value.trim();
        if (password && password.length < 6) {
            showError('signup-password-error', 'Password must be at least 6 characters long');
            setFieldState('signup-password', 'error');
        } else if (password && password.length >= 6) {
            clearError('signup-password-error');
            setFieldState('signup-password', 'success');
        }
    });

    document.getElementById('confirm-password').addEventListener('input', function() {
        const password = document.getElementById('signup-password').value.trim();
        const confirmPassword = this.value.trim();
        
        if (confirmPassword && password !== confirmPassword) {
            showError('confirm-password-error', 'Passwords do not match');
            setFieldState('confirm-password', 'error');
        } else if (confirmPassword && password === confirmPassword) {
            clearError('confirm-password-error');
            setFieldState('confirm-password', 'success');
        }
    });

    // Utility functions
    
    // Email validation using regex
    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
    
    // Show error message
    function showError(elementId, message) {
        const errorElement = document.getElementById(elementId);
        if (errorElement) {
            errorElement.textContent = message;
        }
    }
    
    // Clear specific error
    function clearError(elementId) {
        const errorElement = document.getElementById(elementId);
        if (errorElement) {
            errorElement.textContent = '';
        }
    }
    
    // Set field validation state
    function setFieldState(fieldId, state) {
        const field = document.getElementById(fieldId);
        if (field) {
            field.classList.remove('error', 'success');
            if (state) {
                field.classList.add(state);
            }
        }
    }
    
    // Show success message
    function showSuccessMessage(elementId, message) {
        const successElement = document.getElementById(elementId);
        if (successElement) {
            successElement.textContent = message;
            successElement.classList.add('show');
            
            // Hide success message after 5 seconds
            setTimeout(() => {
                successElement.classList.remove('show');
            }, 5000);
        }
    }
    
    // Clear all login form errors
    function clearLoginErrors() {
        clearError('login-email-error');
        clearError('login-password-error');
        setFieldState('login-email', '');
        setFieldState('login-password', '');
    }
    
    // Clear all signup form errors
    function clearSignupErrors() {
        clearError('signup-name-error');
        clearError('signup-email-error');
        clearError('signup-password-error');
        clearError('confirm-password-error');
        clearError('terms-error');
        setFieldState('signup-name', '');
        setFieldState('signup-email', '');
        setFieldState('signup-password', '');
        setFieldState('confirm-password', '');
    }
    
    // Clear all errors from both forms
    function clearAllErrors() {
        clearLoginErrors();
        clearSignupErrors();
    }
    
    // Clear all success messages
    function clearAllSuccessMessages() {
        const loginSuccess = document.getElementById('login-success');
        const signupSuccess = document.getElementById('signup-success');
        if (loginSuccess) loginSuccess.classList.remove('show');
        if (signupSuccess) signupSuccess.classList.remove('show');
    }

    // Add keyboard navigation support
    document.addEventListener('keydown', function(e) {
        // Allow Escape key to clear current form errors
        if (e.key === 'Escape') {
            clearAllErrors();
            clearAllSuccessMessages();
        }
    });

    // Add focus management for better accessibility
    showSignupLink.addEventListener('click', function() {
        setTimeout(() => {
            const nameField = document.getElementById('signup-name');
            if (nameField) nameField.focus();
        }, 100);
    });

    showLoginLink.addEventListener('click', function() {
        setTimeout(() => {
            const emailField = document.getElementById('login-email');
            if (emailField) emailField.focus();
        }, 100);
    });
});