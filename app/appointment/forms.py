from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, DateTimeLocalField, TextAreaField
from wtforms.validators import DataRequired
from app.models import Doctor

class AppointmentForm(FlaskForm):
    doctor = SelectField('Doctor', coerce=int, validators=[DataRequired()])
    date_time = DateTimeLocalField('Date & Time', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    reason = TextAreaField('Reason for Visit', validators=[DataRequired()])
    submit = SubmitField('Book Appointment')
