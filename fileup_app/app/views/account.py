from flask import Blueprint, render_template

blueprint = Blueprint("account", __name__, template_folder="templates")


@blueprint.route("/account")
def index():
    # TODO: Add account login and logout.
    return render_template("index.html")
