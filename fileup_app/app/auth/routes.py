import msal
import uuid

from rich import print as rprint

from flask import (
    Blueprint,
    current_app,
    g,
    request,
    session,
    has_request_context,
    redirect,
    render_template,
    url_for,
)
from werkzeug.local import LocalProxy

from app.models import User


bp = Blueprint("auth", __name__, template_folder="templates")

current_user = LocalProxy(lambda: get_current_user())


@bp.route("/login")
def login():

    # rprint(current_app, id(current_app))
    # rprint(session)
    # for k, v in current_app.config.items():
    #     if k.startswith("MSAL_"):
    #         rprint(f"{k}='{v}'")

    session["state"] = str(uuid.uuid4())

    scopes = current_app.config["MSAL_SCOPE"]

    auth_url = _build_auth_url(
        scopes=scopes, state=session["state"]
    )

    rprint(auth_url)

    return render_template("login.html", auth_url=auth_url)


@bp.route("/logout")
def logout():
    logout_user()
    session.clear()

    uri = current_app.config['MSAL_AUTHORITY']
    uri += "/oauth2/v2.0/logout?post_logout_redirect_uri="
    uri += url_for("main.index", _external=True)

    return redirect(uri)


@bp.route("/signin-oidc")
def authorized():

    rprint('authorized BEGIN:')
    rprint(session)

    if request.args.get("state") != session.get("state"):
        return redirect(url_for("index"))

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
        # rprint(user_claims)
        # session["user_claims"] = user_claims

        # TODO: Storing user_claims in session cookie exceeds the max
        # cookie size. The larger session details need to go in
        # the database.

        email = user_claims.get("preferred_username")
        if email:
            user = User.query.filter_by(email=email).first()
            if user:
                login_user(user)

        _save_cache(cache)

        rprint('authorized END:')
        rprint(session)

    return redirect(url_for("main.index"))


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

        rprint("get_current_user:")
        rprint(session)

        user_id = session.get("user_id")
        if user_id:
            user = User.query.filter_by(id=user_id).first()
            if user:
                _current_user = g._current_user = user
        # user_claims = session.get("user_claims")
        # if user_claims:
        #     g._current_user_claims = user_claims
    if _current_user is None:
        _current_user = User()
    return _current_user


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


def _load_cache():
    cache = msal.SerializableTokenCache()
    if session.get("token_cache"):
        cache.deserialize(session["token_cache"])
    return cache


def _save_cache(cache):
    # if cache.has_state_changed:
    #     session["token_cache"] = cache.serialize()
    pass
