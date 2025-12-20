from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField, SubmitField, TextAreaField
from wtforms.validators import DataRequired
from app.models import Patient

class InvoiceForm(FlaskForm):
    # Select Patient
    patient = SelectField('Patient', coerce=int, validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    amount = FloatField('Amount ($)', validators=[DataRequired()])
    status = SelectField('Status', choices=[('Pending', 'Pending'), ('Paid', 'Paid')], default='Pending')
    submit = SubmitField('Create Invoice')
