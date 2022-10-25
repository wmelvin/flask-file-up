from datetime import datetime

from app import db


class Org(db.Model):
    __tablename__ = "orgs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    org_name = db.Column(db.String(64), nullable=False, unique=True)
    when_added = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def __repr__(self) -> str:
        return f"<Org {self.orgname}>"


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    org_id = db.Column(db.Integer, db.ForeignKey("orgs.id"), nullable=False)
    username = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(80), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    when_added = db.Column(db.DateTime, nullable=False, default=datetime.now)
    is_active = db.Column(db.Boolean, default=False)

    def __repr__(self) -> str:
        return f"<User {self.username}>"


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
