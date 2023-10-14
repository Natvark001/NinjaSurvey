from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,TextAreaField,PasswordField,BooleanField
from wtforms.validators import Email,DataRequired,EqualTo,Length


class RegisterForm(FlaskForm):
    email=StringField('Email',validators=[DataRequired(message='Email is required'),Email(message='Invalid Email Format')])
    pwd=PasswordField('Password',validators=[DataRequired(message='Password is required'),Length(min=5)])
    confpwd=PasswordField('Confirm Password',validators=[EqualTo('pwd',message='Both password fields must match')])
    agree=BooleanField()
    btncreate=SubmitField('Create Account')

class AdminForm(FlaskForm):
    adminname=StringField('AdminId',validators=[DataRequired(message='Username is required')])
    btnlogin=SubmitField('LogIn')
    pwd=PasswordField('Password',validators=[DataRequired(message='Password should be supplied')])