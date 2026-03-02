from flask import Flask
import config


def create_app():
    app = Flask(
        __name__,
        template_folder='../templates',
        static_folder='../static',
    )
    app.secret_key = config.SECRET_KEY

    from app.public import public_bp
    from app.auth import auth_bp
    from app.portal import portal_bp
    from app.admin import admin_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(portal_bp, url_prefix='/portal')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    return app
