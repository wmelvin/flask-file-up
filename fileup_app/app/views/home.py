from flask import Blueprint, render_template
# from flask_login import current_user

bp = Blueprint("home", __name__, template_folder="templates")


@bp.route("/")
@bp.route("/index")
def home():
    # return render_template("index.html", current_user=current_user)
    return render_template("index.html")
