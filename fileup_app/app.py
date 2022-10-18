
from flask import Flask

import views.account
import views.home
import views.upload

ONE_MB = 1024 * 1024

app = Flask(__name__)

#  Configuration for file uploads.
app.config["MAX_CONTENT_LENGTH"] = 2 * ONE_MB
app.config["UPLOAD_EXTENSIONS"] = [".csv", ".xls", ".xlsx"]
app.config["UPLOAD_PATH"] = "uploads"

app.register_blueprint(views.home.blueprint)
app.register_blueprint(views.account.blueprint)
app.register_blueprint(views.upload.blueprint)


if __name__ == '__main__':
    app.run(debug=True)
