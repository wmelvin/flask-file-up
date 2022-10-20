import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy


basedir = os.path.abspath(os.path.dirname(__file__))
db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    db_file = os.path.join(basedir, 'fileup.sqlite')
    app.config.from_mapping(
        #  Configuration for database.
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{db_file}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        #  Configuration for file uploads.
        MAX_CONTENT_LENGTH=(1024 * 1024),
        UPLOAD_EXTENSIONS=[".csv", ".xls", ".xlsx"],
        UPLOAD_PATH="uploads",
    )

    db.init_app(app)

    from app.views import account
    from app.views import home
    from app.views import upload

    app.register_blueprint(home.blueprint)
    app.register_blueprint(account.blueprint)
    app.register_blueprint(upload.blueprint)

    return app
