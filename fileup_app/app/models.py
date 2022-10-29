from datetime import datetime
from app import db, login_mgr
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash


class Org(db.Model):
    __tablename__ = "orgs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    org_name = db.Column(db.String(64), nullable=False, unique=True)
    when_added = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def __repr__(self) -> str:
        return f"<Org {self.orgname}>"


class User(UserMixin, db.Model):
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


@login_mgr.user_loader
def load_user(id):
    user = User.query.get(int(id))

    # DEBUG
    print(f"load_user: user = {user}")

    return user


class UploadedFile(db.Model):
    __tablename__ = "uploads"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    file_name = db.Column(db.String(255), nullable=False)
    org_id = db.Column(db.Integer, db.ForeignKey("orgs.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    when_uploaded = db.Column(
        db.DateTime, nullable=False, default=datetime.now
    )

    def __repr__(self) -> str:
        return f"<UploadedFile {self.id}>"

    # TODO: Only active users should be able to see uploads.
    # The organization owns the uploaded file.
