from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    StringField,
    PasswordField,
    SubmitField,
)
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign in")


class LoginFormMsal(FlaskForm):
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign in")
