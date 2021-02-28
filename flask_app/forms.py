from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import (StringField, PasswordField, SubmitField, 
                    BooleanField, TextAreaField, Form, SelectField)
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_app.models import Teacher, Student

class RegistrationForm(FlaskForm):
    name = StringField('Name',
                           validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    # choices = [('Student','Student'),('Teacher','Teacher')]
    # user_type = SelectField('Select user type', choices=choices,validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()],id='register_password')
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')],id='confirm_password')
    show_password = BooleanField('Show password', id='show_password')
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        teacher = Teacher.query.filter_by(email=email.data).first()
        student = Student.query.filter_by(email=email.data).first()
        if teacher or student:
            raise ValidationError('That email is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()],id='password')
    remember = BooleanField('Remember Me')
    show_password = BooleanField('Show password', id='show_password')
    google = SubmitField('Sign in with Google')
    submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):
    name = StringField('Name',
                           validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_email(self, email):
        if email.data != current_user.email:
            teacher = Teacher.query.filter_by(email=email.data).first()
            student = Student.query.filter_by(email=email.data).first()
            if teacher or student:
                raise ValidationError('That email is taken. Please choose a different one.')

class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        teacher = Teacher.query.filter_by(email=email.data).first()
        student = Student.query.filter_by(email=email.data).first()
        if teacher is None and student is None:
            raise ValidationError('There is no account with that email. You must register first.')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

class CodeForm(FlaskForm):
    code = StringField('Enter Code', validators=[DataRequired(),Length(min=8, max=8)])
    submit = SubmitField('Submit')