import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

SECRET_KEY = os.environ.get('DHM_SECRET_KEY', 'dev-secret-change-in-production')

DATABASE = os.path.join(BASE_DIR, 'dhm_website.db')

# Path to inventory Excel workbook (read-only)
# On PythonAnywhere: set DHM_INVENTORY_DB env var, or place file in website/data/
INVENTORY_DB = os.environ.get(
    'DHM_INVENTORY_DB',
    os.path.join(DATA_DIR, 'DHM.Inventory.xlsx')
)

# Mail config for password reset
MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'info@dandhmeatco.com')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
MAIL_FROM = os.environ.get('MAIL_FROM', 'info@dandhmeatco.com')

# Admin bootstrap
ADMIN_EMAIL = os.environ.get('DHM_ADMIN_EMAIL', 'herb@dandhmeatco.com')
ADMIN_PASSWORD = os.environ.get('DHM_ADMIN_PASSWORD', 'changeme123')
