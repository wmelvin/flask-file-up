from datetime import datetime
from secrets import token_urlsafe

from app import db
from werkzeug.security import check_password_hash, generate_password_hash


def make_token():
    return token_urlsafe(20)


def make_hash(token):
    return generate_password_hash(token)


def _check_token(hash, token):
    return check_password_hash(hash, token)


class UserToken(db.Model):
    __tablename__ = "usertokens"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    token_type = db.Column(db.String(12), nullable=False)
    token_hash = db.Column(db.String(255), nullable=True)
    token_raw = db.Column(db.String, nullable=True)

    def __init__(
        self,
        user_id: int,
        token_type: str,
        token=None,
        do_hash=True,
    ):
        self.user_id = user_id
        self.token_type = token_type
        if token:
            self.token = token
            if do_hash:
                self.token_hash = make_hash(token)
            else:
                self.token_raw = token
        else:
            self.token = make_token()
            self.token_hash = make_hash(self.token)

    def check_token(self, token):
        return _check_token(self.token_hash, token)


class Org(db.Model):
    __tablename__ = "orgs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    org_name = db.Column(db.String(64), nullable=False, unique=True)
    org_tenant_id = db.Column(db.String, nullable=True, unique=True)
    when_added = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def __repr__(self) -> str:
        return f"<Org {self.id}: '{self.org_name}'>"


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    org_id = db.Column(db.Integer, db.ForeignKey("orgs.id"), nullable=False)
    username = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(80), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    when_added = db.Column(db.DateTime, nullable=False, default=datetime.now)
    active = db.Column(db.Boolean, default=False)
    user_tokens = db.relationship(
        "UserToken",
        backref="user",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User {self.id}: '{self.username}'>"

    @property
    def is_active(self):
        return self.active

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def is_anonymous(self):
        return not bool(self.username)

    @property
    def is_authenticated(self):
        return bool(self.username)

    def get_remember_token(self):
        user_token = UserToken(self.id, "remember")
        db.session.add(user_token)
        #  Return the ephemeral un-hashed token.
        return user_token.token

    def check_remember_token(self, token):
        if token:
            for t in self.user_tokens:
                if t.token_type == "remember" and t.check_token(token):
                    return True
        return False

    def delete_remember_tokens(self):
        self.user_tokens.filter_by(token_type="remember").delete()

    def save_raw_token(self, token_type, token):
        #  Allow only one raw token of a given type.
        self.user_tokens.filter_by(token_type=token_type).delete()
        user_token = UserToken(self.id, token_type, token=token)
        db.session.add(user_token)

    def get_raw_token(self, token_type):
        #  A user should have only one raw token of a given type.
        user_token: UserToken = self.user_tokens.filter_by(
            token_type=token_type
        ).first()
        return user_token.token_raw


class Purpose(db.Model):
    __tablename__ = "purposes"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(80), nullable=False, unique=True)
    tag = db.Column(db.String(12), nullable=False, unique=True)
    description = db.Column(db.String, nullable=True)
    when_added = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def __repr__(self) -> str:
        return f"<Purpose {self.id}: '{self.title}'>"

    def get_tag(self):
        return str(self.tag).replace(" ", "_").replace("-", "_")


class UploadedFile(db.Model):
    __tablename__ = "uploads"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    file_name = db.Column(db.String(255), nullable=False)
    org_id = db.Column(db.Integer, db.ForeignKey("orgs.id"), nullable=False)
    org_name = db.Column(db.String(64), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user_name = db.Column(db.String(80), nullable=False)
    purpose_id = db.Column(
        db.Integer, db.ForeignKey("purposes.id"), nullable=False
    )
    purpose_tag = db.Column(db.String(12), nullable=False)
    when_uploaded = db.Column(
        db.DateTime, nullable=False, default=datetime.now
    )

    def __init__(
        self,
        file_name: str,
        org_id: int,
        org_name: str,
        user_id: int,
        user_name: str,
        purpose_id: int,
        purpose_tag: str,
    ):
        self.file_name = file_name
        self.org_id = org_id
        self.org_name = org_name
        self.user_id = user_id
        self.user_name = user_name
        self.purpose_id = purpose_id
        self.purpose_tag = purpose_tag

    def __repr__(self) -> str:
        return f"<UploadedFile {self.id}: '{self.file_name}'>"
