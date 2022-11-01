from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    StringField,
    PasswordField,
    SubmitField,
    MultipleFileField,
    RadioField,
)
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign in")


class UploadForm(FlaskForm):
    file = MultipleFileField("Select file(s)", validators=[DataRequired()])
    purpose = RadioField("Purpose of File(s)", validators=[DataRequired()])
    submit = SubmitField("Upload")
