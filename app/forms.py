from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError, EqualTo
from .models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=4, max=80)
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6)
    ])
    private_key = TextAreaField('RSA Private Key', validators=[
        DataRequired()
    ])
    submit = SubmitField('Register')

    def validate_username(self, field):
        user = User.query.filter_by(username=field.data).first()
        if user:
            raise ValidationError('Username already exists.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Mật khẩu cũ', validators=[DataRequired()])
    new_password = PasswordField('Mật khẩu mới', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Xác nhận mật khẩu mới', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Đổi mật khẩu')

class ChangeKeyForm(FlaskForm):
    private_key = TextAreaField('Private Key mới (PEM)', validators=[DataRequired()])
    submit = SubmitField('Đổi khóa')
