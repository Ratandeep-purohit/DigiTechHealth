from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, PasswordField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models import User

class DoctorForm(FlaskForm):
    specialization = StringField('Specialization', validators=[DataRequired()])
    availability = StringField('Availability (e.g., Mon-Fri 9-5)', validators=[DataRequired()])
    submit = SubmitField('Save Profile')

class AddDoctorForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    specialization = StringField('Specialization', validators=[DataRequired()])
    availability = StringField('Availability', validators=[DataRequired()])
    submit = SubmitField('Add Doctor')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

class UpdateDoctorForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    specialization = StringField('Specialization', validators=[DataRequired()])
    availability = StringField('Availability', validators=[DataRequired()])
    submit = SubmitField('Update Doctor')

    def __init__(self, original_username, original_email, *args, **kwargs):
        super(UpdateDoctorForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
         if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')
