import os

from flask import (
    current_app,
    request,
    flash,
    redirect,
    render_template,
    url_for,
)
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename

from app.main.forms import LoginForm
from app.models import Purpose, User, Org, UploadedFile
from app.main import bp
from app import db


@bp.route("/")
@bp.route("/index")
def index():
    return render_template("index.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()

    if form.validate_on_submit():  # Always returns False for GET request.
        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            flash("Invalid user name or password.")
            return redirect(url_for("main.login"))

        login_user(user, remember=form.remember_me.data)

        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("main.index")

        return redirect(next_page)

    return render_template("login.html", form=form)


@bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.index"))


@bp.route("/upload")
@login_required
def upload():
    # Get a list of tuples to use in radio button input.
    purposes = [(f"value={p.title}", p.title) for p in Purpose.query.all()]

    files = sorted(os.listdir(current_app.config["UPLOAD_PATH"]))

    ext_list = current_app.config["UPLOAD_EXTENSIONS"]
    if ext_list:
        accept = f"accept={','.join(ext_list)}"
    else:
        print("No UPLOAD_EXTENSIONS configured. Default to '.csv'.")
        accept = "accept=.csv"

    return render_template(
        "upload.html", files=files, accept=accept, purposes=purposes
    )


@bp.route("/upload", methods=["POST"])
@login_required
def upload_files():
    up_files = request.files.getlist("file")
    if (not up_files) or (len(up_files[0].filename) == 0):
        flash("No file(s) selected.")
        return redirect(url_for("main.upload"))

    user: User = current_user
    org: Org = Org.query.get(user.org_id)

    if "purpose" in request.form:
        purpose_input = request.form["purpose"]
    else:
        purpose_input = ""
    if not purpose_input:
        flash("A 'Purpose of File' selection is required.")
        return redirect(url_for("main.upload"))
        # TODO: If this happens, the file selection is lost.
        # Perhaps this can be handled better using WTForms
        # by adding a UploadForm class to forms.py.

    purpose: Purpose = Purpose.query.filter_by(title=purpose_input).first()

    print(f"upload_files: user='{user}', org='{org}', purpose='{purpose}'")

    for up_file in up_files:
        file_name = secure_filename(up_file.filename)
        if file_name != "":
            file_ext = os.path.splitext(file_name)[1]
            if file_ext not in current_app.config["UPLOAD_EXTENSIONS"]:
                flash(f"Invalid file type: '{file_ext}'")
                return redirect(url_for("main.upload"))

            up_file.save(
                os.path.join(current_app.config["UPLOAD_PATH"], file_name)
            )

            uf: UploadedFile = UploadedFile(
                file_name,
                org.id,
                org.org_name,
                user.id,
                user.username,
                purpose.id,
                purpose.tag,
            )
            db.session.add(uf)
            db.session.commit()

    return redirect(url_for("main.upload"))
