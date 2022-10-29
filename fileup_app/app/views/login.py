from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user
from werkzeug.urls import url_parse

from app.forms import LoginForm
from app.models import User

bp = Blueprint("login", __name__, template_folder="templates")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home.home"))

    form = LoginForm()

    if form.validate_on_submit():  # Always returns False for GET request.
        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            flash("Invalid user name or password.")
            return redirect(url_for(".login"))

        result = login_user(user)  # TODO: Add remember option.
        print(f"login_user result = {result}")

        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("home.home")

        return redirect(next_page)

    return render_template("login.html", form=form)


@bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home.home"))
