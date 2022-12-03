import uuid

import msal
from app import db
from app.auth.forms import LoginForm, LoginFormMsal
from app.models import User
from flask import (
    Blueprint,
    current_app,
    flash,
    g,
    has_request_context,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from itsdangerous.url_safe import URLSafeSerializer
from werkzeug.local import LocalProxy
from werkzeug.urls import url_parse
from functools import wraps


MAX_AGE_SEC = 60 * 60 * 24 * 90  # Set cookie max_age in seconds to 90 days.


bp = Blueprint("auth", __name__, template_folder="templates")

current_user = LocalProxy(lambda: get_current_user())


def login_required(f):
    @wraps(f)
    def _login_required(*args, **kwargs):
        if current_user.is_anonymous:
            flash("Please sign in to access the requested page.", "danger ")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)

    return _login_required


def get_response_to_remember(user: User):
    """
    Sets a 'remember' user_token for the User and returns a response that
    sets 'remember_token' and 'user_id' cookies in the browser.
    """
    token = user.get_remember_token()
    db.session.commit()  # Commit the UserToken added in get_remember_token.

    response = make_response(redirect(url_for("main.index")))
    response.set_cookie(
        "remember_token", encrypt_cookie(token), max_age=MAX_AGE_SEC
    )
    response.set_cookie(
        "user_id", encrypt_cookie(user.id), max_age=MAX_AGE_SEC
    )
    return response


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        flash("Already signed in.")
        return redirect(url_for("main.index"))

    form = LoginForm()

    if form.validate_on_submit():  # Always returns False for GET request.
        user: User = User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            flash("Invalid user name or password.")
            return redirect(url_for("auth.login"))

        login_user(user)
        if form.remember_me.data:
            return get_response_to_remember(user)

        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("main.index")

        return redirect(next_page)

    return render_template(
        "login.html", form=form, login2_url=url_for("auth.login2")
    )


@bp.route("/login2", methods=["GET", "POST"])
def login2():
    #  Route to sign in with Azure Active Directory.
    if current_user.is_authenticated:
        flash("Already signed in.")
        return redirect(url_for("main.index"))

    form = LoginFormMsal()

    if form.validate_on_submit():  # Always returns False for GET request.
        scopes = current_app.config["MSAL_SCOPE"]

        #  The 'state' value is returned in the response to the redirect URI.
        #  Encode the remember-me setting in the first character.
        if form.remember_me.data:
            session["state"] = f"1{str(uuid.uuid4())}"
        else:
            session["state"] = f"0{str(uuid.uuid4())}"

        auth_url = _build_auth_url(scopes=scopes, state=session["state"])

        return redirect(auth_url)

    return render_template("login2.html", form=form)


@bp.route("/signin-oidc")
def authorized():
    s = session.get("state")
    if request.args.get("state") != s:
        return redirect(url_for("index"))

    #  The 'remember-me' choice is encoded in the first character of the
    #  'state' value.
    do_remember = s and str(s).startswith("1")

    if "error" in request.args:
        return render_template("auth_error.html", result=request.args)

    if request.args.get("code"):
        cache = _load_cache()
        result = _build_msal_app(
            cache=cache
        ).acquire_token_by_authorization_code(
            request.args["code"],
            scopes=current_app.config["MSAL_SCOPE"],
            redirect_uri=url_for("auth.authorized", _external=True),
        )
        if "error" in result:
            return render_template("auth_error.html", result=result)

        user_claims = result.get("id_token_claims")

        email = user_claims.get("preferred_username")
        if email:
            user = User.query.filter_by(email=email).first()
            if user:
                login_user(user)

        _save_cache(cache)

        if user and do_remember:
            return get_response_to_remember(user)

    return redirect(url_for("main.index"))


@bp.route("/logout")
@login_required
def logout():
    #  Logout step 1.

    #  Delete the user's "remember" user_tokens in the database.
    current_user.delete_remember_tokens()
    db.session.commit()

    #  Send a response that clears the content of the "remember" cookies
    #  in the browser and redirects to step 2.
    response = make_response(redirect(url_for("auth.logout2")))
    response.set_cookie("remember_token", "", max_age=0)
    response.set_cookie("user_id", "", max_age=0)

    return response


# TODO: Confirm this two-step logout will hold up. It may be necessary to set
#  a flag in the database in step 1, and then do something in response to the
#  flag in a subsequent session, to make sure a user is logged out if the
#  redirect to step 2 fails.


@bp.route("/logout2")
@login_required
def logout2():
    #  Logout step 2. At this point, the user should still be logged in
    #  since step 1 only deletes the 'remember' user token and cookies.
    logout_user()
    session.clear()

    uri = current_app.config["MSAL_AUTHORITY"]
    uri += "/oauth2/v2.0/logout?post_logout_redirect_uri="
    uri += url_for("main.index", _external=True)

    return redirect(uri)


def login_user(user):
    session["user_id"] = user.id


def logout_user():
    session.pop("user_id")


@bp.app_context_processor
def inject_current_user():
    if has_request_context():
        return dict(current_user=get_current_user())
    return dict(current_user="")


def get_current_user():
    _current_user = getattr(g, "_current_user", None)
    if _current_user is None:
        user_id = session.get("user_id")
        if user_id:
            user = User.query.filter_by(id=user_id).first()
            if user:
                #  Also store user in Flask's g variable for quick access (no
                #  database call) when get_current_user is called multiple
                #  times in the same session.
                _current_user = g._current_user = user
        else:
            enc_cookie = request.cookies.get("user_id")
            if enc_cookie:
                uid = int(decrypt_cookie(enc_cookie))
                user: User = User.query.get(uid)
                if user:
                    token = decrypt_cookie(
                        request.cookies.get("remember_token")
                    )
                    if user.check_remember_token(token):
                        login_user(user)
                        _current_user = g._current_user = user

        if _current_user is None:
            _current_user = User()

    return _current_user


def encrypt_cookie(content):
    zer = URLSafeSerializer(current_app.config["SECRET_KEY"])
    enc = zer.dumps(content)
    return enc


def decrypt_cookie(enc):
    zer = URLSafeSerializer(current_app.config["SECRET_KEY"])
    try:
        content = zer.loads(enc)
    except:  # noqa E722
        content = "-1"
    return content


def _build_msal_app(cache=None, authority=None):
    return msal.ConfidentialClientApplication(
        current_app.config["MSAL_CLIENT_ID"],
        authority=authority or current_app.config["MSAL_AUTHORITY"],
        client_credential=current_app.config["MSAL_CLIENT_SECRET"],
        token_cache=cache,
    )


def _build_auth_url(authority=None, scopes=None, state=None):
    msal_app = _build_msal_app(authority=authority)

    auth_url = msal_app.get_authorization_request_url(
        scopes or [],
        state=state or str(uuid.uuid4()),
        redirect_uri=url_for("auth.authorized", _external=True),
    )

    return auth_url


# TODO: Implement MSAL cache some other way. It will not fit in a cookie.


def _load_cache():
    cache = msal.SerializableTokenCache()
    # if session.get("token_cache"):
    #     cache.deserialize(session["token_cache"])
    return cache


def _save_cache(cache):
    # if cache.has_state_changed:
    #     session["token_cache"] = cache.serialize()
    return
