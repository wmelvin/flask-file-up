from flask import Blueprint, render_template

from app.forms import LoginForm

blueprint = Blueprint("login", __name__, template_folder="templates")


@blueprint.route("/login")
def login():
    form = LoginForm()
    return render_template("login.html", form=form)
