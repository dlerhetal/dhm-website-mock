import os
import re
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from app.decorators import admin_required
from app.models import (
    get_all_users, get_user_by_id, update_user_status,
    get_all_posts, get_post_by_id, create_blog_post, update_blog_post, delete_blog_post,
    get_all_deals, get_deal_by_id, create_flash_deal, update_flash_deal, delete_flash_deal,
    get_credit_application,
)

admin_bp = Blueprint('admin', __name__)

ALLOWED_IMAGE_EXT = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}

def save_deal_image(file):
    """Save uploaded deal image, return filename or '' on failure."""
    if not file or not file.filename:
        return ''
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_IMAGE_EXT:
        return ''
    filename = f"{uuid.uuid4().hex[:12]}{ext}"
    upload_dir = os.path.join(current_app.static_folder, 'img', 'deals')
    os.makedirs(upload_dir, exist_ok=True)
    file.save(os.path.join(upload_dir, filename))
    return filename


def slugify(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text[:80]


@admin_bp.route('/')
@admin_required
def dashboard():
    users = get_all_users()
    pending = [u for u in users if u['status'] == 'pending']
    posts = get_all_posts()
    deals = get_all_deals()
    return render_template('admin/dashboard.html',
                           pending_count=len(pending), post_count=len(posts), deal_count=len(deals))


# ── User Management ──

@admin_bp.route('/users')
@admin_required
def users():
    all_users = get_all_users()
    return render_template('admin/users.html', users=all_users)


@admin_bp.route('/users/<int:user_id>/approve', methods=['POST'])
@admin_required
def approve_user(user_id):
    tier = request.form.get('tier', 'A')
    update_user_status(user_id, 'approved', tier)
    flash('User approved.', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/<int:user_id>/deny', methods=['POST'])
@admin_required
def deny_user(user_id):
    update_user_status(user_id, 'denied')
    flash('User denied.', 'info')
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/<int:user_id>/application')
@admin_required
def view_application(user_id):
    user = get_user_by_id(user_id)
    app = get_credit_application(user_id)
    return render_template('admin/application.html', user=user, application=app)


# ── Blog Management ──

@admin_bp.route('/blog')
@admin_required
def blog_list():
    posts = get_all_posts()
    return render_template('admin/blog_list.html', posts=posts)


@admin_bp.route('/blog/new', methods=['GET', 'POST'])
@admin_required
def blog_new():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        slug = slugify(title)
        category = request.form.get('category', '')
        content = request.form.get('content', '')
        excerpt = request.form.get('excerpt', '')
        status = request.form.get('status', 'draft')

        if not title:
            flash('Title is required.', 'danger')
            return render_template('admin/blog_editor.html', post=None)

        create_blog_post(title, slug, category, content, excerpt, status)
        flash('Post created.', 'success')
        return redirect(url_for('admin.blog_list'))

    return render_template('admin/blog_editor.html', post=None)


@admin_bp.route('/blog/<int:post_id>/edit', methods=['GET', 'POST'])
@admin_required
def blog_edit(post_id):
    post = get_post_by_id(post_id)
    if not post:
        flash('Post not found.', 'danger')
        return redirect(url_for('admin.blog_list'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        slug = slugify(title)
        category = request.form.get('category', '')
        content = request.form.get('content', '')
        excerpt = request.form.get('excerpt', '')
        status = request.form.get('status', 'draft')

        update_blog_post(post_id, title, slug, category, content, excerpt, status)
        flash('Post updated.', 'success')
        return redirect(url_for('admin.blog_list'))

    return render_template('admin/blog_editor.html', post=post)


@admin_bp.route('/blog/<int:post_id>/delete', methods=['POST'])
@admin_required
def blog_delete(post_id):
    delete_blog_post(post_id)
    flash('Post deleted.', 'success')
    return redirect(url_for('admin.blog_list'))


# ── Deal Management ──

@admin_bp.route('/deals')
@admin_required
def deals():
    all_deals = get_all_deals()
    return render_template('admin/deals.html', deals=all_deals)


@admin_bp.route('/deals/new', methods=['GET', 'POST'])
@admin_required
def deal_new():
    if request.method == 'POST':
        image_filename = save_deal_image(request.files.get('image'))
        create_flash_deal(
            product_name=request.form.get('product_name', ''),
            description=request.form.get('description', ''),
            price_a=float(request.form.get('price_a', 0)),
            price_b=float(request.form.get('price_b', 0)),
            price_c=float(request.form.get('price_c', 0)),
            price_unit=request.form.get('price_unit', '/lb'),
            regular_price=float(request.form.get('regular_price', 0)),
            available_qty=int(request.form.get('available_qty', 0)),
            min_order=int(request.form.get('min_order', 1)),
            urgency=request.form.get('urgency', ''),
            show_pricing=1 if request.form.get('show_pricing') else 0,
            image_filename=image_filename,
            status=request.form.get('status', 'active'),
        )
        flash('Deal created.', 'success')
        return redirect(url_for('admin.deals'))
    return render_template('admin/deal_editor.html', deal=None)


@admin_bp.route('/deals/<int:deal_id>/edit', methods=['GET', 'POST'])
@admin_required
def deal_edit(deal_id):
    deal = get_deal_by_id(deal_id)
    if not deal:
        flash('Deal not found.', 'danger')
        return redirect(url_for('admin.deals'))

    if request.method == 'POST':
        kwargs = dict(
            product_name=request.form.get('product_name', ''),
            description=request.form.get('description', ''),
            price_a=float(request.form.get('price_a', 0)),
            price_b=float(request.form.get('price_b', 0)),
            price_c=float(request.form.get('price_c', 0)),
            price_unit=request.form.get('price_unit', '/lb'),
            regular_price=float(request.form.get('regular_price', 0)),
            available_qty=int(request.form.get('available_qty', 0)),
            min_order=int(request.form.get('min_order', 1)),
            urgency=request.form.get('urgency', ''),
            show_pricing=1 if request.form.get('show_pricing') else 0,
            status=request.form.get('status', 'active'),
        )
        # Handle image: new upload replaces old, "remove" checkbox clears it
        new_image = save_deal_image(request.files.get('image'))
        if new_image:
            # Delete old file if replacing
            if deal['image_filename']:
                old_path = os.path.join(current_app.static_folder, 'img', 'deals', deal['image_filename'])
                if os.path.exists(old_path):
                    os.remove(old_path)
            kwargs['image_filename'] = new_image
        elif request.form.get('remove_image'):
            if deal['image_filename']:
                old_path = os.path.join(current_app.static_folder, 'img', 'deals', deal['image_filename'])
                if os.path.exists(old_path):
                    os.remove(old_path)
            kwargs['image_filename'] = ''

        update_flash_deal(deal_id, **kwargs)
        flash('Deal updated.', 'success')
        return redirect(url_for('admin.deals'))

    return render_template('admin/deal_editor.html', deal=deal)


@admin_bp.route('/deals/<int:deal_id>/delete', methods=['POST'])
@admin_required
def deal_delete(deal_id):
    delete_flash_deal(deal_id)
    flash('Deal deleted.', 'success')
    return redirect(url_for('admin.deals'))
