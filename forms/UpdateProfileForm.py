from flask_wtf import FlaskForm
from wtforms.fields import StringField, PasswordField, SubmitField, BooleanField, RadioField, TextAreaField, EmailField
from wtforms.validators import InputRequired, DataRequired, EqualTo, Length, ValidationError, Email


class UpdateProfileForm(FlaskForm):
    username = StringField("Username *",
                           validators=[
                               InputRequired("Input is required!"),
                               DataRequired("Data is required!"),
                               Length(
                                   min=5, max=20, message="Username must be between 5 and 20 characters long")
                           ])
    email = EmailField("Email *",
                       validators=[
                           InputRequired("Input is required!"),
                           DataRequired("Data is required!"),
                           Length(
                               min=10, max=30, message="Email must be between 5 and 30 characters long"),
                           Email("You did not enter a valid email!")
                       ])
    password = PasswordField("Password *",
                             validators=[
                                 InputRequired("Input is required!"),
                                 DataRequired("Data is required!"),
                                 Length(
                                     min=4, max=40, message="Password must be between 10 and 40 characters long"),
                                 EqualTo("password_confirm",
                                         message="Passwords must match")
                             ])
    password_confirm = PasswordField("Confirm Password *",
                                     validators=[
                                         InputRequired("Input is required!"),
                                         DataRequired("Data is required!")
                                     ])
    location = StringField("Your location (e.g. City, Country) *",
                           validators=[
                               InputRequired("Input is required!"),
                               DataRequired("Data is required!"),
                               Length(
                                   min=3, max=40, message="Location must be between 3 and 40 characters long")
                           ])
    description = TextAreaField("Description ",
                                validators=[
                                    Length(
                                        min=0, max=200, message="Description must be between 10 and 200 characters long")
                                ])
    submit = SubmitField("Register")
