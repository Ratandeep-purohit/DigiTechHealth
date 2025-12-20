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
