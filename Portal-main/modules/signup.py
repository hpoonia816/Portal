from flask_wtf import FlaskForm,RecaptchaField
from wtforms import EmailField, PasswordField, SubmitField, StringField
from wtforms.validators import DataRequired, Optional, Regexp, EqualTo

class Signupform(FlaskForm):
    firstname = StringField("First Name",validators=[DataRequired()])
    middlename = StringField("Middle Name",validators=[Optional()])
    lastname = StringField("Last Name",validators=[DataRequired()])
    mobilenumber = StringField("Mobile Number",validators=[DataRequired(),Regexp(regex=r'^\d+$')])
    email = EmailField("Email" ,validators=[DataRequired()])
    password = PasswordField("Password",validators=[DataRequired()])
    confirmpassword = PasswordField("Confirm Password",validators=[DataRequired(),EqualTo('password')])
    recaptcha = RecaptchaField()
    submit = SubmitField("Sign-up")