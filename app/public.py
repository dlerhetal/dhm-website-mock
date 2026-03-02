from flask import Blueprint, render_template, request, redirect, url_for
from app.models import get_published_posts, get_post_by_slug, get_active_deals, create_deal_signup

public_bp = Blueprint('public', __name__)


@public_bp.route('/')
def home():
    deals = get_active_deals()
    return render_template('index.html', deals=deals)


@public_bp.route('/about')
def about():
    return render_template('about.html')


@public_bp.route('/flash-deals')
def flash_deals():
    deals = get_active_deals()
    signup_success = request.args.get('signed_up') == '1'
    return render_template('flash_deals.html', deals=deals, signup_success=signup_success)


@public_bp.route('/flash-deals/signup', methods=['POST'])
def deal_signup():
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    if name and email:
        create_deal_signup(name, email)
    return redirect(url_for('public.flash_deals', signed_up='1'))


@public_bp.route('/blog')
def blog_list():
    posts = get_published_posts()
    return render_template('blog/list.html', posts=posts)


@public_bp.route('/blog/<slug>')
def blog_post(slug):
    post = get_post_by_slug(slug)
    if not post:
        return render_template('404.html'), 404
    return render_template('blog/post.html', post=post)
