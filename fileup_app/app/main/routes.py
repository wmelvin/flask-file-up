import os

from flask import (
    current_app,
    request,
    flash,
    redirect,
    render_template,
    url_for,
    abort,
)
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename

from app.main.forms import LoginForm
from app.models import User
from app.main import bp


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
    files = sorted(os.listdir(current_app.config["UPLOAD_PATH"]))
    a = current_app.config["UPLOAD_EXTENSIONS"]
    if a:
        accept = f"accept={','.join(a)}"
    else:
        print("No UPLOAD_EXTENSIONS configured. Default to '.csv'.")
        accept = "accept=.csv"
    return render_template("upload.html", files=files, accept=accept)


@bp.route("/upload", methods=["POST"])
@login_required
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
    return redirect(url_for("main.upload"))
