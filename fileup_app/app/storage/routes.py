from flask import Blueprint, flash, redirect, url_for

from app.auth.routes import current_user, login_required


bp = Blueprint("storage", __name__, template_folder="templates")


@bp.route("/checkstorage", methods=["GET"])
def check_storage():
    pass
    # TODO: ...


@bp.route("/upload2", methods=["POST"])
@login_required
def upload_to_storage():
    print(current_user)
    flash("Not implemented.")
    return redirect(url_for("main.index"))
    # TODO: ...
