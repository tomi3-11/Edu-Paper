from wtforms import StringField, PasswordField
from flask_wtf import FlaskForm
from wtforms.validators import Length, Email, DataRequired, EqualTo
from app import csrf

class RegistrationForm(FlaskForm):
    class Meta:
        csrf = False
        
    username = StringField('User name', validators=[DataRequired(), Length(min=2, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[EqualTo('password')])