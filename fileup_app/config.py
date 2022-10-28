import os


basedir = os.path.abspath(os.path.dirname(__file__))


def local_db_uri() -> str:
    db_dir = os.path.join(basedir, "local_db")
    db_file = os.path.join(db_dir, "fileup.sqlite")
    return f"sqlite:///{db_file}"


class Config(object):
    SECRET_KEY = os.environ.get("FILEUP_SECRET_KEY") or "this-secret-key-SUCKS"
    # TODO: Make sure the 'or' case does not make it to prod.

    #  Configuration for database.
    SQLALCHEMY_DATABASE_URI = local_db_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # TODO: Prod db settings.

    #  Configuration for file uploads.
    MAX_CONTENT_LENGTH = (1024 * 1024)
    # TODO: 1 MB for now, but needs to be set.

    UPLOAD_EXTENSIONS = [".csv", ".xls", ".xlsx"]
    UPLOAD_PATH = "uploads"
