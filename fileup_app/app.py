# import sys

from pathlib import Path
from flask import Flask

import data.db_session as sess


ONE_MB = 1024 * 1024

app = Flask(__name__)

#  Configuration for file uploads.
app.config["MAX_CONTENT_LENGTH"] = 2 * ONE_MB
app.config["UPLOAD_EXTENSIONS"] = [".csv", ".xls", ".xlsx"]
app.config["UPLOAD_PATH"] = "uploads"


def register_blueprints():
    from views import account
    from views import home
    from views import upload

    app.register_blueprint(home.blueprint)
    app.register_blueprint(account.blueprint)
    app.register_blueprint(upload.blueprint)


def setup_db():
    db_file = str(Path(__file__).parent / 'local_db' / 'fileup.sqlite')
    sess.global_init(db_file)


def main():
    register_blueprints()
    setup_db()
    if __name__ == '__main__':
        # app.run(debug=True)
        app.run(
            use_debugger=False, use_reloader=False, passthrough_errors=True
        )


print(f"NAME: '{__name__}'")

if __name__ in ['__main__', 'app']:
    main()
