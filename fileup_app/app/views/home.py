from flask import Blueprint, render_template

blueprint = Blueprint("home", __name__, template_folder="templates")


@blueprint.route("/")
@blueprint.route("/index")
def home():
    return render_template("index.html")
