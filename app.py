from flask import Flask
from config import Config
from shop.extensions import bcrypt, db, init_async_db, jwt, mail, migrate

def create_app(config_class=Config):
    app = Flask(__name__)
    
    app.config.from_object(config_class)


    # ✅ PEHLE extensions init kar
    db.init_app(app)
    init_async_db(app)

    # Import models during app setup so Alembic sees the complete metadata.
    from shop import models  # noqa: F401

    migrate.init_app(app, db, compare_type=True)
    bcrypt.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)

    # Blueprints
    from shop.auth.routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    from shop.user.routes import user_bp
    app.register_blueprint(user_bp, url_prefix="/api/user")

    from shop.admin.routes import admin_bp
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    
    from shop.seller.routes import seller_bp
    app.register_blueprint(seller_bp, url_prefix="/api/seller")

    @app.route("/")
    def index():
        return {"message": "E-Commerce Backend is Running Successfully!"}, 200

    return app


app = create_app()


if __name__ == "__main__":
    app.run(port=5000, debug=True)
