from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, IntegerField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Email, NumberRange

class PatientForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    picture = FileField('Patient Photo', validators=[FileAllowed(['jpg', 'png'])])
    age = IntegerField('Age', validators=[DataRequired(), NumberRange(min=0, max=150)])
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    contact = StringField('Contact Number', validators=[DataRequired(), Length(min=10, max=15)])
    address = TextAreaField('Address', validators=[DataRequired()])
    medical_history = TextAreaField('Medical History (Optional)')
    submit = SubmitField('Save Patient')
