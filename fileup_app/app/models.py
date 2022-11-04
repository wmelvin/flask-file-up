from datetime import datetime
# from app import db, login_mgr
from app import db
# from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash


class Org(db.Model):
    __tablename__ = "orgs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    org_name = db.Column(db.String(64), nullable=False, unique=True)
    when_added = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def __repr__(self) -> str:
        return f"<Org {self.id}: '{self.org_name}'>"


# class User(UserMixin, db.Model):
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    org_id = db.Column(db.Integer, db.ForeignKey("orgs.id"), nullable=False)
    username = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(80), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    when_added = db.Column(db.DateTime, nullable=False, default=datetime.now)
    active = db.Column(db.Boolean, default=False)

    def __repr__(self) -> str:
        return f"<User {self.id}: '{self.username}'>"

    @property
    def is_active(self):
        return self.active

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


# @login_mgr.user_loader
# def load_user(id):
#     user = User.query.get(int(id))

#     # DEBUG
#     print(f"load_user: user = {user}")

#     return user


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

    # TODO: Only active users should be able to see uploads.
    # The organization owns the uploaded file.
