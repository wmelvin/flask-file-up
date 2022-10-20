import sqlalchemy as sa

from datetime import datetime

from fileup_app.data.base import SqlAlchemyBase


class UploadedFile(SqlAlchemyBase):
    __tablename__ = 'uploads'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)

    file_name = sa.Column(sa.String(255), nullable=False)
    
    when_uploaded = sa.Column(
        sa.DateTime, nullable=False, default=datetime.now()
    )

    def __repr__(self) -> str:
        return f'<UploadedFile {self.id}'
