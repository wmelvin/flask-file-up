import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
# from flask_login import LoginManager

from config import Config


db = SQLAlchemy()
migrate = Migrate()
# login_mgr = LoginManager()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    # login_mgr.init_app(app)
    # login_mgr.login_view = "login.login"

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    upload_path = app.config["UPLOAD_PATH"]
    if upload_path:
        upload_path = os.path.abspath(upload_path)
        if not os.path.exists(upload_path):
            print(f"create_app: mkdir {upload_path}")
            os.mkdir(upload_path)

    return app


from app import models  # noqa E402
