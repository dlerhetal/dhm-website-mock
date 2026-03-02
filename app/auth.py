from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models import (
    create_user, get_user_by_email, check_user_password,
    create_credit_application, generate_reset_token, verify_reset_token,
    update_user_password
)
from app.mail import send_reset_email

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        user = get_user_by_email(email)
        if not user or not check_user_password(user, password):
            flash('Invalid email or password.', 'danger')
            return render_template('auth/login.html')

        if user['status'] == 'pending':
            return redirect(url_for('auth.pending_approval'))
        if user['status'] == 'denied':
            flash('Your account application was not approved. Contact us at (319) 270-4800.', 'danger')
            return render_template('auth/login.html')

        session['user_id'] = user['id']
        session['user_name'] = user['name']
        session['is_admin'] = bool(user['is_admin'])

        if user['is_admin']:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('portal.dashboard'))

    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been signed out.', 'info')
    return redirect(url_for('public.home'))


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('contact_email', '').strip()
        password = request.form.get('password', '')
        name = request.form.get('contact_name', '').strip()
        company = request.form.get('biz_name', '').strip()
        phone = request.form.get('contact_phone', '').strip()
        address = ', '.join(filter(None, [
            request.form.get('biz_address', ''),
            request.form.get('biz_city', ''),
            request.form.get('biz_state', ''),
            request.form.get('biz_zip', ''),
        ]))

        if not email or not password or not name or not company:
            flash('Please fill in all required fields.', 'danger')
            return render_template('auth/signup.html')

        if len(password) < 8:
            flash('Password must be at least 8 characters.', 'danger')
            return render_template('auth/signup.html')

        existing = get_user_by_email(email)
        if existing:
            flash('An account with that email already exists.', 'danger')
            return render_template('auth/signup.html')

        user_id = create_user(email, password, name, company, phone, address)

        # Save credit application data
        app_data = {k: request.form.get(k, '') for k in [
            'biz_name', 'biz_dba', 'biz_type', 'biz_ein', 'biz_years',
            'biz_address', 'biz_city', 'biz_state', 'biz_zip',
            'contact_name', 'contact_title', 'contact_phone', 'contact_email',
            'credit_terms', 'credit_volume',
            'bank_name', 'bank_type', 'bank_phone', 'bank_acct',
            'ref1_company', 'ref1_contact', 'ref1_phone',
            'ref2_company', 'ref2_contact', 'ref2_phone',
            'ref3_company', 'ref3_contact', 'ref3_phone',
            'notes', 'signature',
        ]}
        app_data['products_interested'] = ', '.join(request.form.getlist('products_interested'))
        app_data['delivery_days'] = ', '.join(request.form.getlist('delivery_days'))
        create_credit_application(user_id, app_data)

        return redirect(url_for('auth.pending_approval'))

    return render_template('auth/signup.html')


@auth_bp.route('/pending')
def pending_approval():
    return render_template('auth/pending_approval.html')


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        user = get_user_by_email(email)
        if user:
            token = generate_reset_token(email)
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            send_reset_email(email, reset_url)
        # Always show same message (no email enumeration)
        flash('If that email is in our system, you\'ll receive a reset link shortly.', 'info')
        return render_template('auth/forgot_password.html')

    return render_template('auth/forgot_password.html')


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    email = verify_reset_token(token)
    if not email:
        flash('This reset link is invalid or has expired.', 'danger')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        if len(password) < 8:
            flash('Password must be at least 8 characters.', 'danger')
            return render_template('auth/reset_password.html', token=token)
        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/reset_password.html', token=token)

        user = get_user_by_email(email)
        if user:
            update_user_password(user['id'], password)
        flash('Your password has been reset. You can now sign in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', token=token)
