document.addEventListener('DOMContentLoaded', function () {
    const loginForm = document.getElementById('login-form');
    const signupForm = document.getElementById('signup-form');
    const forgotForm = document.getElementById('forgot-form');
    const showSignup = document.getElementById('show-signup');
    const showLogin = document.getElementById('show-login');
    const showForgot = document.getElementById('show-forgot');
    const backToLogin = document.getElementById('back-to-login');

    // --- API Endpoints ---
    const API_BASE_URL = 'http://127.0.0.1:5000/api'; // For local testing

    // --- Switch Forms ---
    const switchForm = (from, to) => {
        from.classList.remove('active');
        to.classList.add('active');
    };

    showSignup.addEventListener('click', e => { e.preventDefault(); switchForm(loginForm, signupForm); });
    showLogin.addEventListener('click', e => { e.preventDefault(); switchForm(signupForm, loginForm); });
    showForgot.addEventListener('click', e => { e.preventDefault(); switchForm(loginForm, forgotForm); });
    backToLogin.addEventListener('click', e => { e.preventDefault(); switchForm(forgotForm, loginForm); });

    // --- Password Toggle ---
    document.querySelectorAll('.toggle-password').forEach(icon => {
        icon.addEventListener('click', () => {
            const target = document.getElementById(icon.dataset.target);
            const type = target.type === 'password' ? 'text' : 'password';
            target.type = type;
            icon.textContent = type === 'password' ? '🫣' : '🙈';
        });
    });

    // --- Email Validation ---
    function isValidEmail(email) {
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return regex.test(email);
    }

    // --- Signup Form ---
    document.getElementById('signupFormElement').addEventListener('submit', async e => {
        e.preventDefault();

        const name = document.getElementById('signup-name').value.trim();
        const email = document.getElementById('signup-email').value.trim();
        const password = document.getElementById('signup-password').value.trim();
        const confirmPassword = document.getElementById('confirm-password').value.trim();

        if (!isValidEmail(email)) {
            showError('signup-email-error', 'Invalid email format');
            return;
        }
        if (password !== confirmPassword) {
            showError('confirm-password-error', 'Passwords do not match');
            return;
        }

        try {
            const res = await fetch(`${API_BASE_URL}/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username: name, email, password })
            });
            const data = await res.json();
            if (data.message) {
                showSuccess('signup-success', 'Account created successfully! Redirecting...');
                setTimeout(() => switchForm(signupForm, loginForm), 2000);
            } else {
                showError('signup-email-error', data.error || 'Error creating account.');
            }
        } catch {
            showError('signup-email-error', 'Server connection failed.');
        }
    });

    // --- Login Form ---
    document.getElementById('loginFormElement').addEventListener('submit', async e => {
        e.preventDefault();

        const email = document.getElementById('login-email').value.trim();
        const password = document.getElementById('login-password').value.trim();

        if (!isValidEmail(email)) {
            showError('login-email-error', 'Invalid email format');
            return;
        }

        try {
            const res = await fetch(`${API_BASE_URL}/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });
            const data = await res.json();

            if (data.message === 'Login Successful') {
                localStorage.setItem('userInfo', JSON.stringify({ user_id: data.user_id, username: data.username }));
                showSuccess('login-success', 'Login successful! Redirecting...');
                window.location.href = '/dashboard';
            } else {
                showError('login-email-error', data.error || 'Invalid credentials.');
            }
        } catch {
            showError('login-email-error', 'Server connection failed.');
        }
    });

    // --- Forgot Password Form ---
    document.getElementById('forgotFormElement').addEventListener('submit', async e => {
        e.preventDefault();

        const email = document.getElementById('forgot-email').value.trim();
        if (!isValidEmail(email)) {
            showError('forgot-email-error', 'Invalid email format');
            return;
        }

        try {
            const res = await fetch(`${API_BASE_URL}/forgot-password`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email })
            });
            const data = await res.json();
            if (data.message) {
                showSuccess('forgot-success', data.message);
            } else {
                showError('forgot-email-error', data.error || 'Could not send reset link.');
            }
        } catch {
            showError('forgot-email-error', 'Server connection failed.');
        }
    });

    // --- Helper Functions ---
    function showError(id, msg) {
        const el = document.getElementById(id);
        if (el) el.textContent = msg;
    }

    function showSuccess(id, msg) {
        const el = document.getElementById(id);
        if (el) {
            el.textContent = msg;
            el.style.color = '#5cb85c';
        }
    }
});