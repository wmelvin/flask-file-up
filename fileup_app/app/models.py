from datetime import datetime

from app import db


class UploadedFile(db.Model):
    __tablename__ = 'uploads'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    file_name = db.Column(db.String(255), nullable=False)

    when_uploaded = db.Column(
        db.DateTime, nullable=False, default=datetime.now
    )

    def __repr__(self) -> str:
        return f'<UploadedFile {self.id}'
