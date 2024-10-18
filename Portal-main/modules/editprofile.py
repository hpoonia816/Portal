from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, SubmitField, StringField
from wtforms.validators import DataRequired, Optional, Regexp, EqualTo

class EditProfileform(FlaskForm):
    firstname = StringField("First Name",validators=[Optional()])
    middlename = StringField("Middle Name",validators=[Optional()])
    lastname = StringField("Last Name",validators=[Optional()])
    mobilenumber = StringField("Number",validators=[Optional(),Regexp(regex=r'^\d+$')])
    email = EmailField("Email" ,validators=[Optional()])
    newpassword = PasswordField("New Password",validators=[Optional()])
    oldpassword = PasswordField("Old Password",validators=[DataRequired()])
    submit = SubmitField("Save Changes")    
