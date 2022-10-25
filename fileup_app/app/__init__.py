import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


basedir = os.path.abspath(os.path.dirname(__file__))
db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)

    db_dir = os.path.join(os.path.dirname(basedir), "local_db")
    db_file = os.path.join(db_dir, "fileup.sqlite")

    # TODO: Prod db settings.

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
    migrate.init_app(app, db)

    from app.views import account
    from app.views import home
    from app.views import upload

    app.register_blueprint(home.blueprint)
    app.register_blueprint(account.blueprint)
    app.register_blueprint(upload.blueprint)

    return app


from app import models  # noqa
