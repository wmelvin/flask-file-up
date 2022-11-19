import os

from app.auth.routes import current_user, login_required
from app.main import bp
from app.main.forms import UploadForm
from app.models import Org, Purpose, User
from app.storage.routes import store_uploaded_file
from flask import (
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from werkzeug.utils import secure_filename


@bp.route("/")
@bp.route("/index")
def index():
    return render_template("index.html")


@bp.route("/upload")
@login_required
def upload():
    # Get list of tuples to use in radio button input.
    purposes = [(p.title, p.title) for p in Purpose.query.all()]

    files = current_user.get_uploaded_file_list()

    #  Get list of accepted file extensions.
    ext_list = current_app.config["UPLOAD_EXTENSIONS"]
    if ext_list:
        accept = ",".join(ext_list)
    else:
        print("No UPLOAD_EXTENSIONS configured. Default to '.csv'.")
        accept = ".csv"

    form = UploadForm()
    form.purpose.choices = purposes

    return render_template(
        "upload.html", form=form, files=files, accept=accept
    )


@bp.route("/upload", methods=["POST"])
@login_required
def upload_files():
    upload_url = "main.upload"
    up_files = request.files.getlist("file")
    if (not up_files) or (len(up_files[0].filename) == 0):
        flash("No file(s) selected.")
        return redirect(url_for(upload_url))

    user: User = current_user
    org: Org = Org.query.get(user.org_id)

    if "purpose" in request.form:
        purpose_input = request.form["purpose"]
    else:
        purpose_input = ""
    if not purpose_input:
        flash("A 'Purpose of File' selection is required.")
        return redirect(url_for(upload_url))

    purpose: Purpose = Purpose.query.filter_by(title=purpose_input).first()

    print(f"upload_files: user='{user}', org='{org}', purpose='{purpose}'")

    for up_file in up_files:
        #  up_file is type 'werkzeug.datastructures.FileStorage'
        file_name = secure_filename(up_file.filename)
        if file_name != "":
            file_ext = os.path.splitext(file_name)[1]
            if file_ext not in current_app.config["UPLOAD_EXTENSIONS"]:
                flash(f"Invalid file type: '{file_ext}'")
                return redirect(url_for(upload_url))

            file_name = f"fileup-u{user.id}-{purpose.get_tag()}-{file_name}"
            store_uploaded_file(file_name, org, user, purpose, up_file)

    return redirect(url_for(upload_url))
