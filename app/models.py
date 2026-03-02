import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
import config

def get_db():
    conn = sqlite3.connect(config.DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

# ── Users ──

def create_user(email, password, name, company, phone, address=''):
    db = get_db()
    hashed = generate_password_hash(password)
    try:
        db.execute(
            """INSERT INTO users (email, password, name, company, phone, address, tier, status, is_admin)
               VALUES (?, ?, ?, ?, ?, ?, 'A', 'pending', 0)""",
            (email.lower(), hashed, name, company, phone, address)
        )
        db.commit()
        user_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
        return user_id
    finally:
        db.close()

def get_user_by_email(email):
    db = get_db()
    try:
        return db.execute("SELECT * FROM users WHERE email = ?", (email.lower(),)).fetchone()
    finally:
        db.close()

def get_user_by_id(user_id):
    db = get_db()
    try:
        return db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    finally:
        db.close()

def check_user_password(user, password):
    return check_password_hash(user['password'], password)

def update_user_status(user_id, status, tier=None):
    db = get_db()
    try:
        if tier:
            db.execute("UPDATE users SET status = ?, tier = ? WHERE id = ?", (status, tier, user_id))
        else:
            db.execute("UPDATE users SET status = ? WHERE id = ?", (status, user_id))
        db.commit()
    finally:
        db.close()

def set_user_reset_token(email, token, expiry):
    db = get_db()
    try:
        db.execute("UPDATE users SET reset_token = ?, reset_expiry = ? WHERE email = ?", (token, expiry, email.lower()))
        db.commit()
    finally:
        db.close()

def get_user_by_reset_token(token):
    db = get_db()
    try:
        return db.execute("SELECT * FROM users WHERE reset_token = ?", (token,)).fetchone()
    finally:
        db.close()

def update_user_password(user_id, new_password):
    db = get_db()
    try:
        hashed = generate_password_hash(new_password)
        db.execute("UPDATE users SET password = ?, reset_token = NULL, reset_expiry = NULL WHERE id = ?", (hashed, user_id))
        db.commit()
    finally:
        db.close()

def get_all_users():
    db = get_db()
    try:
        return db.execute("SELECT * FROM users ORDER BY id DESC").fetchall()
    finally:
        db.close()

# ── Blog Posts ──

def create_blog_post(title, slug, category, content, excerpt, status='draft'):
    db = get_db()
    try:
        db.execute(
            """INSERT INTO blog_posts (title, slug, category, content, excerpt, status)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (title, slug, category, content, excerpt, status)
        )
        db.commit()
    finally:
        db.close()

def get_published_posts():
    db = get_db()
    try:
        return db.execute(
            "SELECT * FROM blog_posts WHERE status = 'published' ORDER BY published_at DESC"
        ).fetchall()
    finally:
        db.close()

def get_all_posts():
    db = get_db()
    try:
        return db.execute("SELECT * FROM blog_posts ORDER BY id DESC").fetchall()
    finally:
        db.close()

def get_post_by_slug(slug):
    db = get_db()
    try:
        return db.execute("SELECT * FROM blog_posts WHERE slug = ?", (slug,)).fetchone()
    finally:
        db.close()

def get_post_by_id(post_id):
    db = get_db()
    try:
        return db.execute("SELECT * FROM blog_posts WHERE id = ?", (post_id,)).fetchone()
    finally:
        db.close()

def update_blog_post(post_id, title, slug, category, content, excerpt, status):
    db = get_db()
    try:
        published_at = None
        if status == 'published':
            existing = db.execute("SELECT published_at FROM blog_posts WHERE id = ?", (post_id,)).fetchone()
            if not existing['published_at']:
                published_at = "datetime('now')"
        if published_at:
            db.execute(
                """UPDATE blog_posts SET title=?, slug=?, category=?, content=?, excerpt=?, status=?, published_at=datetime('now')
                   WHERE id=?""",
                (title, slug, category, content, excerpt, status, post_id)
            )
        else:
            db.execute(
                """UPDATE blog_posts SET title=?, slug=?, category=?, content=?, excerpt=?, status=?
                   WHERE id=?""",
                (title, slug, category, content, excerpt, status, post_id)
            )
        db.commit()
    finally:
        db.close()

def delete_blog_post(post_id):
    db = get_db()
    try:
        db.execute("DELETE FROM blog_posts WHERE id = ?", (post_id,))
        db.commit()
    finally:
        db.close()

# ── Flash Deals ──

def create_flash_deal(product_name, description, price_a, price_b, price_c, price_unit,
                      regular_price, available_qty, min_order, urgency, status='active'):
    db = get_db()
    try:
        db.execute(
            """INSERT INTO flash_deals
               (product_name, description, price_a, price_b, price_c, price_unit,
                regular_price, available_qty, min_order, urgency, status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (product_name, description, price_a, price_b, price_c, price_unit,
             regular_price, available_qty, min_order, urgency, status)
        )
        db.commit()
    finally:
        db.close()

def get_active_deals():
    db = get_db()
    try:
        return db.execute("SELECT * FROM flash_deals WHERE status = 'active' ORDER BY id DESC").fetchall()
    finally:
        db.close()

def get_all_deals():
    db = get_db()
    try:
        return db.execute("SELECT * FROM flash_deals ORDER BY id DESC").fetchall()
    finally:
        db.close()

def get_deal_by_id(deal_id):
    db = get_db()
    try:
        return db.execute("SELECT * FROM flash_deals WHERE id = ?", (deal_id,)).fetchone()
    finally:
        db.close()

def update_flash_deal(deal_id, **kwargs):
    db = get_db()
    try:
        sets = ', '.join(f"{k} = ?" for k in kwargs)
        vals = list(kwargs.values()) + [deal_id]
        db.execute(f"UPDATE flash_deals SET {sets} WHERE id = ?", vals)
        db.commit()
    finally:
        db.close()

def delete_flash_deal(deal_id):
    db = get_db()
    try:
        db.execute("DELETE FROM flash_deals WHERE id = ?", (deal_id,))
        db.commit()
    finally:
        db.close()

# ── Credit Applications ──

def create_credit_application(user_id, data):
    db = get_db()
    try:
        db.execute(
            """INSERT INTO credit_applications
               (user_id, biz_name, biz_dba, biz_type, biz_ein, biz_years,
                biz_address, biz_city, biz_state, biz_zip,
                contact_name, contact_title, contact_phone, contact_email,
                credit_terms, credit_volume,
                bank_name, bank_type, bank_phone, bank_acct,
                ref1_company, ref1_contact, ref1_phone,
                ref2_company, ref2_contact, ref2_phone,
                ref3_company, ref3_contact, ref3_phone,
                products_interested, delivery_days, notes, signature)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, data.get('biz_name'), data.get('biz_dba'), data.get('biz_type'),
             data.get('biz_ein'), data.get('biz_years'),
             data.get('biz_address'), data.get('biz_city'), data.get('biz_state'), data.get('biz_zip'),
             data.get('contact_name'), data.get('contact_title'), data.get('contact_phone'), data.get('contact_email'),
             data.get('credit_terms'), data.get('credit_volume'),
             data.get('bank_name'), data.get('bank_type'), data.get('bank_phone'), data.get('bank_acct'),
             data.get('ref1_company'), data.get('ref1_contact'), data.get('ref1_phone'),
             data.get('ref2_company'), data.get('ref2_contact'), data.get('ref2_phone'),
             data.get('ref3_company'), data.get('ref3_contact'), data.get('ref3_phone'),
             data.get('products_interested'), data.get('delivery_days'), data.get('notes'), data.get('signature'))
        )
        db.commit()
    finally:
        db.close()

def get_credit_application(user_id):
    db = get_db()
    try:
        return db.execute("SELECT * FROM credit_applications WHERE user_id = ?", (user_id,)).fetchone()
    finally:
        db.close()

# ── Deal Signups ──

def create_deal_signup(name, email):
    db = get_db()
    try:
        db.execute(
            "INSERT OR IGNORE INTO deal_signups (name, email) VALUES (?, ?)",
            (name, email.lower())
        )
        db.commit()
    finally:
        db.close()

def get_all_deal_signups():
    db = get_db()
    try:
        return db.execute("SELECT * FROM deal_signups ORDER BY created_at DESC").fetchall()
    finally:
        db.close()

# ── Token Helpers ──

def generate_reset_token(email):
    s = URLSafeTimedSerializer(config.SECRET_KEY)
    return s.dumps(email, salt='password-reset')

def verify_reset_token(token, max_age=3600):
    s = URLSafeTimedSerializer(config.SECRET_KEY)
    try:
        email = s.loads(token, salt='password-reset', max_age=max_age)
        return email
    except Exception:
        return None
