from flask import render_template, url_for, flash, redirect, request
from app import db
from app.appointment import appointment
from app.appointment.forms import AppointmentForm
from app.models import Appointment, Doctor, Patient
from flask_login import login_required, current_user

@appointment.route("/appointments")
@login_required
def list_appointments():
    if current_user.role == 'doctor':
        doctor = Doctor.query.filter_by(user_id=current_user.id).first()
        if doctor:
            appointments = Appointment.query.filter_by(doctor_id=doctor.id).all()
        else:
            appointments = []
    elif current_user.role == 'admin' or current_user.role == 'receptionist':
         appointments = Appointment.query.all()
    else:
        # Patient view
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        if patient:
            appointments = Appointment.query.filter_by(patient_id=patient.id).all()
        else:
            appointments = []

    return render_template('appointment/list.html', appointments=appointments)

@appointment.route("/appointment/book", methods=['GET', 'POST'])
@login_required
def book_appointment():
    form = AppointmentForm()
    # Populate doctors and patients
    form.doctor.choices = [(d.id, f"{d.user.username} ({d.specialization})") for d in Doctor.query.all()]
    form.patient.choices = [(p.id, p.name) for p in Patient.query.all()]
    
    if form.validate_on_submit():
        appointment = Appointment(
            doctor_id=form.doctor.data, 
            patient_id=form.patient.data,
            date_time=form.date_time.data, 
            reason=form.reason.data, 
            status='Scheduled'
        )
        db.session.add(appointment)
        db.session.commit()
        flash('Appointment Booked!', 'success')
        return redirect(url_for('appointment.list_appointments'))
        
    return render_template('appointment/book.html', title='Book Appointment', form=form)
