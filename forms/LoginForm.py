
from flask_wtf import FlaskForm
from wtforms.fields import StringField, PasswordField, SubmitField, BooleanField, RadioField, TextAreaField, EmailField
from wtforms.validators import InputRequired, DataRequired, EqualTo, Length, ValidationError, Email


class LoginForm(FlaskForm):
    username = StringField("Username *",
                           validators=[
                               InputRequired("Input is required!"),
                               DataRequired("Data is required!"),
                               Length(
                                   min=5, max=20, message="Username must be between 5 and 20 characters long")
                           ])
    
    password = PasswordField("Password *",
                             validators=[
                                 InputRequired("Input is required!"),
                                 DataRequired("Data is required!"),
                                 Length(
                                     min=4, max=40, message="Password must be between 10 and 40 characters long")
                             ])
    
    submit = SubmitField("Login")
