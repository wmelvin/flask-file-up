# import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

from config import Config


db = SQLAlchemy()
migrate = Migrate()
login_mgr = LoginManager()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    # login_mgr.init_app(app)
    # login_mgr.login_view = "login.login"

    from app.views import home
    from app.views import upload
    from app.views import login

    app.register_blueprint(home.bp)
    app.register_blueprint(upload.bp)
    app.register_blueprint(login.bp)

    login_mgr.init_app(app)
    login_mgr.login_view = "login.login"

    return app


from app import models  # noqa
