"""Create SQLite tables and bootstrap admin user."""
import sqlite3
from werkzeug.security import generate_password_hash
import config

def init():
    conn = sqlite3.connect(config.DATABASE)
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        name TEXT NOT NULL,
        company TEXT DEFAULT '',
        phone TEXT DEFAULT '',
        address TEXT DEFAULT '',
        tier TEXT DEFAULT 'A',
        status TEXT DEFAULT 'pending',
        is_admin INTEGER DEFAULT 0,
        reset_token TEXT,
        reset_expiry TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS blog_posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        slug TEXT UNIQUE NOT NULL,
        category TEXT DEFAULT '',
        content TEXT DEFAULT '',
        excerpt TEXT DEFAULT '',
        status TEXT DEFAULT 'draft',
        published_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS flash_deals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT NOT NULL,
        description TEXT DEFAULT '',
        price_a REAL,
        price_b REAL,
        price_c REAL,
        price_unit TEXT DEFAULT '/lb',
        regular_price REAL,
        available_qty INTEGER DEFAULT 0,
        min_order INTEGER DEFAULT 1,
        urgency TEXT DEFAULT '',
        show_pricing INTEGER DEFAULT 0,
        image_filename TEXT DEFAULT '',
        status TEXT DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

    # Migrate: add missing columns to flash_deals (existing DBs)
    cols = [r[1] for r in c.execute("PRAGMA table_info(flash_deals)").fetchall()]
    for col_name, col_def in [
        ('show_pricing', "INTEGER DEFAULT 0"),
        ('image_filename', "TEXT DEFAULT ''"),
    ]:
        if col_name not in cols:
            c.execute(f"ALTER TABLE flash_deals ADD COLUMN {col_name} {col_def}")
            print(f"Migrated: added {col_name} column to flash_deals")

    c.execute("""CREATE TABLE IF NOT EXISTS credit_applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        biz_name TEXT, biz_dba TEXT, biz_type TEXT, biz_ein TEXT, biz_years TEXT,
        biz_address TEXT, biz_city TEXT, biz_state TEXT, biz_zip TEXT,
        contact_name TEXT, contact_title TEXT, contact_phone TEXT, contact_email TEXT,
        credit_terms TEXT, credit_volume TEXT,
        bank_name TEXT, bank_type TEXT, bank_phone TEXT, bank_acct TEXT,
        ref1_company TEXT, ref1_contact TEXT, ref1_phone TEXT,
        ref2_company TEXT, ref2_contact TEXT, ref2_phone TEXT,
        ref3_company TEXT, ref3_contact TEXT, ref3_phone TEXT,
        products_interested TEXT, delivery_days TEXT, notes TEXT, signature TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS deal_signups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

    # Bootstrap admin user if not exists
    existing = c.execute("SELECT id FROM users WHERE email = ?", (config.ADMIN_EMAIL.lower(),)).fetchone()
    if not existing:
        c.execute(
            """INSERT INTO users (email, password, name, company, phone, tier, status, is_admin)
               VALUES (?, ?, ?, ?, ?, 'A', 'approved', 1)""",
            (config.ADMIN_EMAIL.lower(),
             generate_password_hash(config.ADMIN_PASSWORD),
             'Alex Glew', 'D&H Meats', '')
        )
        print(f"Admin user created: {config.ADMIN_EMAIL}")

    # Seed sample blog posts
    existing_posts = c.execute("SELECT COUNT(*) FROM blog_posts").fetchone()[0]
    if existing_posts == 0:
        posts = [
            ("Beef Market Outlook: What to Expect in Spring 2026",
             "beef-market-outlook-spring-2026", "Market Updates",
             """<p>Cattle futures have been volatile heading into spring, and that means opportunity for buyers who plan ahead. Here's what we're seeing from our packer partners and what it means for your purchasing decisions over the next 60 days.</p>
<p><strong>Ground beef</strong> pricing has softened slightly due to increased cow slaughter numbers in the Southern Plains. If you typically stock 73/27 or 81/19 blends, now's the time to lock in pricing. We've seen quotes come down $0.08-0.12/lb from January peaks.</p>
<p><strong>Choice middle meats</strong> (ribeyes, strips, tenderloins) remain elevated. With grilling season approaching, expect packers to hold firm on pricing through May. Our recommendation: consider booking your Memorial Day needs now rather than waiting for spot-market availability.</p>""",
             "Cattle futures have been volatile heading into spring. Here's what we're seeing from our packer partners.",
             "published"),
            ("Cold Chain Best Practices for Your Walk-In",
             "cold-chain-best-practices", "Food Safety",
             """<p>Proper cold storage isn't just about food safety — it's about your bottom line. Every degree of temperature abuse costs money in shrink and shelf life. Here are five things every receiving dock should check.</p>
<p><strong>1. Verify on arrival.</strong> Use a calibrated thermometer to check product temp at the dock. Reject anything above 41°F for fresh or 0°F for frozen.</p>
<p><strong>2. First in, first out.</strong> Rotate stock religiously. Date everything that comes in.</p>
<p><strong>3. Don't overload.</strong> Air needs to circulate. Pack your walk-in tight and you'll get warm spots.</p>
<p><strong>4. Check your seals.</strong> Door gaskets wear out. A bad seal can cost you hundreds in energy and spoilage.</p>
<p><strong>5. Log temps daily.</strong> A simple clipboard log catches problems before they become health code violations.</p>""",
             "Proper cold storage isn't just about food safety — it's about your bottom line.",
             "published"),
            ("Why Pork/Beef Blends Are Taking Over Burger Menus",
             "pork-beef-blends-burger-menus", "Product Spotlights",
             """<p>More restaurants are moving to pork/beef blends for their burger programs. The economics are compelling — better margins with a flavor profile customers love. We break down the numbers.</p>
<p>A 60/40 beef/pork blend can save you $0.30-0.50/lb compared to straight 80/20 ground beef, and many chefs say the fat profile actually produces a juicier burger.</p>
<p>We carry several blend options from Tyson Fresh Meats. Ask Herb about current pricing.</p>""",
             "More restaurants are moving to pork/beef blends. The economics are compelling.",
             "published"),
            ("How to Read a Meat Invoice Like a Pro",
             "how-to-read-meat-invoice", "Business Tips",
             """<p>CWT pricing, catchweight vs fixed-weight, fuel surcharges — meat invoices can be confusing. This guide walks you through every line so you always know exactly what you're paying.</p>
<p><strong>CWT = per hundredweight.</strong> When you see a price like $189.00 CWT, that means $1.89/lb. Divide by 100.</p>
<p><strong>Catchweight vs fixed weight.</strong> Most wholesale meat is catchweight — the actual weight varies slightly per piece. Your invoice will show the exact weight and the calculated price.</p>
<p><strong>Fuel surcharges.</strong> These are separate from product cost. They're charged per delivery, not per pound. Don't accidentally include them in your per-pound cost calculations.</p>""",
             "CWT pricing, catchweight vs fixed-weight, fuel surcharges — meat invoices can be confusing.",
             "published"),
        ]
        for title, slug, category, content, excerpt, status in posts:
            c.execute(
                """INSERT INTO blog_posts (title, slug, category, content, excerpt, status, published_at)
                   VALUES (?, ?, ?, ?, ?, ?, datetime('now'))""",
                (title, slug, category, content, excerpt, status)
            )
        print(f"Seeded {len(posts)} blog posts")

    # Seed sample flash deals
    existing_deals = c.execute("SELECT COUNT(*) FROM flash_deals").fetchone()[0]
    if existing_deals == 0:
        deals = [
            ("81/19 Ground Beef Chubs", "Cargill — 10 lb chubs, 4/case",
             2.29, 2.39, 2.49, "/lb", 2.68, 180, 20, "Ends Today"),
            ("Boneless Pork Loins", "Smithfield — ~8 lb avg, 6/case",
             1.45, 1.55, 1.65, "/lb", 1.82, 90, 10, "2 Days Left"),
            ("IQF Chicken Wings", "Tyson — 40 lb case, Jumbo split",
             1.18, 1.28, 1.38, "/lb", 1.49, 240, 15, "New This Week"),
        ]
        for d in deals:
            c.execute(
                """INSERT INTO flash_deals
                   (product_name, description, price_a, price_b, price_c, price_unit,
                    regular_price, available_qty, min_order, urgency, status)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active')""", d
            )
        print(f"Seeded {len(deals)} flash deals")

    conn.commit()
    conn.close()
    print(f"Database initialized: {config.DATABASE}")

if __name__ == '__main__':
    init()
