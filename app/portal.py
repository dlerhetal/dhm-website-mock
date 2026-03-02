from flask import Blueprint, render_template, session
from app.decorators import login_required
from app.models import get_active_deals, get_user_by_id
from app.excel_reader import get_inventory

portal_bp = Blueprint('portal', __name__)


@portal_bp.route('/dashboard')
@login_required
def dashboard():
    user = get_user_by_id(session['user_id'])
    deals = get_active_deals()
    return render_template('portal/dashboard.html', user=user, deals=deals, active_tab='deals')


@portal_bp.route('/inventory')
@login_required
def inventory():
    user = get_user_by_id(session['user_id'])
    items = get_inventory()
    return render_template('portal/inventory.html', user=user, items=items)


@portal_bp.route('/deals')
@login_required
def deals():
    user = get_user_by_id(session['user_id'])
    deals = get_active_deals()
    return render_template('portal/flash_deals.html', user=user, deals=deals)


@portal_bp.route('/account')
@login_required
def account():
    user = get_user_by_id(session['user_id'])
    return render_template('portal/account.html', user=user)
