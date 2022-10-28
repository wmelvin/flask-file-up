from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_user

from app.forms import LoginForm
from app.models import User

blueprint = Blueprint("login", __name__, template_folder="templates")


@blueprint.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home.home"))
    form = LoginForm()
    if form.validate_on_submit():  # Returns False for GET request.
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid user name or password.")
            return redirect(url_for(".login"))
        login_user(user)  # TODO: Add remember option.
        return redirect(url_for("home.home"))
    return render_template("login.html", form=form)
