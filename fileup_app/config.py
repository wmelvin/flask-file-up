import os

from dotenv import load_dotenv


basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


def local_db_uri() -> str:
    db_dir = os.path.join(basedir, "local_db")
    db_file = os.path.join(db_dir, "fileup.sqlite")
    return f"sqlite:///{db_file}"


class Config(object):
    SECRET_KEY = os.environ.get("FILEUP_SECRET_KEY") or "this-secret-key-SUCKS"
    # TODO: Make sure the 'or' case does not make it to prod.

    #  -- Configuration for database.

    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("FILEUP_DATABASE_URI") or local_db_uri()
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    #  -- Configuration for file uploads.

    #  Default is 2MB for max size of uploaded file.
    s = os.environ.get("FILEUP_MAX_UPLOAD_MB")
    if s is not None and s.isdigit():
        max_upload_mb = int(s)
    else:
        max_upload_mb = 2
    MAX_CONTENT_LENGTH = max_upload_mb * 1024 * 1024

    UPLOAD_EXTENSIONS = [".csv", ".xls", ".xlsx"]
    UPLOAD_PATH = "uploads"

    # -- Configuration for MSAL.

    MSAL_REDIRECT_PATH = os.environ.get("FILEUP_MSAL_REDIRECT_PATH")
    MSAL_AUTHORITY = os.environ.get("FILEUP_MSAL_AUTHORITY")
    MSAL_CLIENT_ID = os.environ.get("FILEUP_MSAL_CLIENT_ID")
    MSAL_CLIENT_SECRET = os.environ.get("FILEUP_MSAL_CLIENT_SECRET")

    MSAL_SCOPE = [os.environ.get("FILEUP_MSAL_SCOPE")]
    #  SCOPE needs to be a list.
