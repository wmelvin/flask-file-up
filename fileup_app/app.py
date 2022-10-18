import os

from flask import Flask, render_template, request, redirect, url_for, abort
from werkzeug.utils import secure_filename


ONE_MB = 1024 * 1024


app = Flask(__name__)

#  Configuration for file uploads.
app.config["MAX_CONTENT_LENGTH"] = 2 * ONE_MB
app.config["UPLOAD_EXTENSIONS"] = [".csv", ".xls", ".xlsx"]
app.config["UPLOAD_PATH"] = "uploads"


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/upload')
def upload():
    files = sorted(os.listdir(app.config["UPLOAD_PATH"]))
    return render_template("upload.html", files=files)


@app.route("/upload", methods=["POST"])
def upload_files():
    for up_file in request.files.getlist("file"):
        file_name = secure_filename(up_file.filename)
        if file_name != "":
            file_ext = os.path.splitext(file_name)[1]
            if file_ext not in app.config["UPLOAD_EXTENSIONS"]:
                abort(400)
            up_file.save(os.path.join(app.config["UPLOAD_PATH"], file_name))
    return redirect(url_for("upload"))


if __name__ == '__main__':
    app.run(debug=True)
