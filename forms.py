from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired, FileSize
from wtforms.fields import StringField, PasswordField, DateField, RadioField, SelectField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, length, equal_to, ValidationError
from models import User
from ext import db


class RegisterForm(FlaskForm):
    username = StringField("Pick a username", validators=[DataRequired(message="A username is required to register.")])
    password = PasswordField("Pick a password", validators=[DataRequired(message="A password is required to register."),
                                                            length(min=8, max=64)])
    repeat_password = PasswordField("Repeat your chosen password", validators=[
        equal_to("password", message="Passwords do not match. Please try again.")])
    birthday = DateField("Enter your date of birth",
                         validators=[DataRequired("Your birthday date is required to register.")])
    gender = RadioField("Pick your gender", choices=["Male", "Female", "Non-binary", "Prefer not to say"],
                        validators=[DataRequired(message="You must pick a gender to register.")])
    country = SelectField("Pick your country",
                          choices=["Select here", "Georgia", "United States", "France", "United Kingdom"],
                          validators=[DataRequired(message="You must pick a country to register.")])
    pfp = FileField("Choose your profile picture",
                    validators=[FileSize(5 * 1024 * 1024),
                                FileAllowed(["jpg", "png", "jpeg"])])

    def validate_username(self, field):
        if " " in field.data:
            raise ValidationError("Usernames cannot contain spaces.")
        if User.query.filter_by(username=field.data).first():
            raise ValidationError("That username is already registered.")

    submit = SubmitField("Register")


class EditUserForm(FlaskForm):
    username = StringField("Pick a username", validators=[DataRequired(message="A username is required to register.")])

    birthday = DateField("Enter your date of birth",
                         validators=[DataRequired("Your birthday date is required to register.")])
    gender = RadioField("Pick your gender", choices=["Male", "Female", "Non-binary", "Prefer not to say"],
                        validators=[DataRequired(message="You must pick a gender to register.")])
    country = SelectField("Pick your country",
                          choices=["Select here", "Georgia", "United States", "France", "United Kingdom"],
                          validators=[DataRequired(message="You must pick a country to register.")])
    pfp = FileField("Choose your profile picture",
                    validators=[FileSize(5 * 1024 * 1024),
                                FileAllowed(["jpg", "png", "jpeg"])])

    submit = SubmitField("Save")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(message="Your username is required to log in.")])
    password = PasswordField("Password", validators=[DataRequired(message="Your password is required to log in."),
                                                     length(min=8, max=64)])

    submit = SubmitField("Log in")


class CreateThreadForm(FlaskForm):
    threadname = StringField("Title", validators=[DataRequired(message="You must add a title to make a thread."),
                                                  length(min=3, max=16)])
    description = TextAreaField("Description", validators=[
        length(max=2000, message="Your text exceeds the maximum character limit. The limit is 2000 characters.")])
    img = FileField("Upload Image", validators=[FileSize(5 * 1024 * 1024),
                                                FileAllowed(["jpg", "png", "jpeg"])])

    submit = SubmitField("Create Thread")


class CreatePostForm(FlaskForm):
    postTitle = StringField("Title", validators=[DataRequired(message="You must add a title to make a post.")])
    text = TextAreaField("Text", validators=[DataRequired(), length(max=2000)])
    img = FileField("Upload File", validators=[FileSize(5 * 1024 * 1024),
                                               FileAllowed(["jpg", "png", "jpeg"])])

    submit = SubmitField("Post")


class PostCommentForm(FlaskForm):
    text = TextAreaField("Comment", validators=[DataRequired(), length(max=1000)])
    img = FileField("Upload File", validators=[FileSize(5 * 1024 * 1024),
                                               FileAllowed(["jpg", "png", "jpeg"])])

    submit = SubmitField("Comment")


class FeedbackForm(FlaskForm):
    FeedbackTitle = StringField("Title", validators=[DataRequired(message="You must add a title to make a feedback.")])
    FeedbackType = SelectField(
        "Choose the feedback type.",
        choices=[
            ("feedback", "Feedback"),
            ("bugreport", "Bug report")
        ],
        validators=[DataRequired()]
    )
    BugDescription = TextAreaField("Description",
                                   validators=[DataRequired(message="You must enter a description of the bug")])

    FeedbackDescription = TextAreaField("Description",
                                        validators=[
                                            DataRequired(message="You must enter a description for the feedback")])

    Images = FileField("Upload images and videos to recreate the bug", validators=[FileSize(5 * 1024 * 1024),
                                                                                   FileAllowed(["jpg", "png", "jpeg"])])

    Notes = StringField("Optional notes")

    submit = SubmitField("Submit")
