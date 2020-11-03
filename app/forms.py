from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError, TextAreaField, SelectField
from wtforms.validators import DataRequired, EqualTo, Length

from app.models import *
from app.visibility import Visibility

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username already in use.')

class ProfileEditForm(FlaskForm):
    #profile description
    description = TextAreaField('description')

    #profile visibility
    visibility = [(int(value), label) for label, value in Visibility.__members__.items()]
    profileVisibility = SelectField('Profile Visibility', choices=visibility)

    submitProfileEdit = SubmitField('Submit profile edit')

class PasswordChangeForm(FlaskForm):
    #passwords
    oldPassword = PasswordField('Old Password', validators=[DataRequired()])
    newPassword = PasswordField('New Password', validators=[DataRequired()])
    newPassword2 = PasswordField('Repeat new password', validators=[DataRequired(), EqualTo('newPassword')])

    submitPasswordChange = SubmitField('Change Password')

class CreateGroupForm(FlaskForm):
    name = StringField('Group Name', validators=[DataRequired(), Length(min=0, max=160)])
    description = TextAreaField('Group Description')
    visibility = [(int(value), label) for label, value in Visibility.__members__.items()]
    groupVisibility = SelectField('Group Visibility', choices=visibility)
    joinPermission = SelectField('Group Join Permission', choices=[(0,"Public"), (1, "Moderator must approve")])

    submit = SubmitField('Create Group')

    def validate_name(self, name):
        group = Group.query.filter_by(name=name.data).first()
        if group is not None:
            raise ValidationError('Group name already in use.')

class CreateThreadForm(FlaskForm):
    subject = StringField('Thread Subject', validators=[DataRequired(), Length(min=0, max=160)])
    description = TextAreaField('Thread Description')

    submit = SubmitField('Create Thread')

class CreatePostForm(FlaskForm):
    body = TextAreaField('Post')

    submit = SubmitField('Create Post')

class CreateCommentForm(FlaskForm):
    body = TextAreaField('Comment')

    submit = SubmitField('Comment')