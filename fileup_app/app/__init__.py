import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config


db = SQLAlchemy()
migrate = Migrate()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.secret_key = config_class.SECRET_KEY

    db.init_app(app)
    migrate.init_app(app, db)

    from app.auth.routes import bp as auth_bp
    from app.main import bp as main_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    upload_path = app.config["UPLOAD_PATH"]
    if upload_path:
        upload_path = os.path.abspath(upload_path)
        if not os.path.exists(upload_path):
            print(f"create_app: mkdir {upload_path}")
            os.mkdir(upload_path)

    return app


from app import models  # noqa E402
