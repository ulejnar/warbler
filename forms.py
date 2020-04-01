from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, ValidationError
from wtforms.validators import DataRequired, Email, Length
from models import User
from app import g

class MessageForm(FlaskForm):
    """Form for adding/editing messages."""

    text = TextAreaField('text', validators=[DataRequired()])


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    image_url = StringField('(Optional) Image URL')


class UserEditForm(FlaskForm):
    """Form for editing user details."""

    def validate_password(form, field):
        """ Validate password """
        if not User.authenticate(g.user.username, field.data):
            raise ValidationError("Invalid Password") # Prints error twice, but why?

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    image_url = StringField('(Optional) Image URL')
    header_image_url = StringField('(Optional) Header Image URL')
    bio = StringField('(Optional) Bio')
    password = PasswordField('Password', validators=[DataRequired(), validate_password])


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])
