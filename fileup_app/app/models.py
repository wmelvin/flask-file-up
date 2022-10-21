from datetime import datetime

from app import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password_hash = db.Column(db.String, nullable=False)
    when_added = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def __repr__(self) -> str:
        return f"<User {self.id}>"


class UploadedFile(db.Model):
    __tablename__ = "uploads"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    file_name = db.Column(db.String(255), nullable=False)
    when_uploaded = db.Column(
        db.DateTime, nullable=False, default=datetime.now
    )

    def __repr__(self) -> str:
        return f"<UploadedFile {self.id}>"
