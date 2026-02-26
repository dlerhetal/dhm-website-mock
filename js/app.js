// D&H Meats - Mock Website JavaScript

// Mobile menu toggle
document.addEventListener('DOMContentLoaded', function() {
    const btn = document.getElementById('mobile-menu-btn');
    const menu = document.getElementById('mobile-menu');
    if (btn && menu) {
        btn.addEventListener('click', function() {
            menu.classList.toggle('hidden');
        });
    }

    // Login form handler
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const email = document.getElementById('login-email').value;
            // Mock login - any credentials work
            localStorage.setItem('dhm_logged_in', 'true');
            localStorage.setItem('dhm_user_name', email.split('@')[0].replace(/[._]/g, ' ').replace(/\b\w/g, c => c.toUpperCase()));
            window.location.href = 'portal.html';
        });
    }

    // Protect portal page
    if (window.location.pathname.includes('portal.html')) {
        const loggedIn = localStorage.getItem('dhm_logged_in');
        if (!loggedIn) {
            window.location.href = 'login.html';
        }
    }
});
