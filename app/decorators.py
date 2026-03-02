from functools import wraps
from flask import session, redirect, url_for, flash
from app.models import get_user_by_id


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            flash('Please log in to access that page.', 'warning')
            return redirect(url_for('auth.login'))
        user = get_user_by_id(user_id)
        if not user or user['status'] != 'approved':
            session.clear()
            flash('Your account is not active.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('auth.login'))
        user = get_user_by_id(user_id)
        if not user or not user['is_admin']:
            flash('Admin access required.', 'danger')
            return redirect(url_for('public.home'))
        return f(*args, **kwargs)
    return decorated
