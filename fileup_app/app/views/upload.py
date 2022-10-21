import os

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    abort,
    current_app,
)
from werkzeug.utils import secure_filename


blueprint = Blueprint("upload", __name__, template_folder="templates")


@blueprint.route("/upload")
def upload():
    files = sorted(os.listdir(current_app.config["UPLOAD_PATH"]))
    return render_template("upload.html", files=files)


@blueprint.route("/upload", methods=["POST"])
def upload_files():
    for up_file in request.files.getlist("file"):
        file_name = secure_filename(up_file.filename)
        if file_name != "":
            file_ext = os.path.splitext(file_name)[1]
            if file_ext not in current_app.config["UPLOAD_EXTENSIONS"]:
                abort(400)
            up_file.save(
                os.path.join(current_app.config["UPLOAD_PATH"], file_name)
            )
    return redirect(url_for(".upload"))
