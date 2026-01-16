from flask import render_template, url_for, flash, redirect, request, abort
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
    # Populate doctors
    form.doctor.choices = [(d.id, f"{d.user.username} ({d.specialization})") for d in Doctor.query.all()]
    
    # Context-aware patient selection
    if current_user.role == 'patient':
        current_appt_patient = Patient.query.filter_by(user_id=current_user.id).first()
        if current_appt_patient:
            form.patient.choices = [(current_appt_patient.id, current_appt_patient.name)]
            if request.method == 'GET':
                 form.patient.data = current_appt_patient.id
        else:
             # Should practically not happen if registration flow is correct, but safe fallback
             form.patient.choices = []
             flash('No patient profile found. Please contact support.', 'danger')
    else:
        # Admin / Receptionist / Doctor can book for anyone
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
        
    return render_template('appointment/book.html', title='Book Appointment', form=form, legend='Book Appointment')

@appointment.route("/appointment/<int:appointment_id>/update", methods=['GET', 'POST'])
@login_required
def update_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    if appointment.patient_id != current_user.id and appointment.doctor.user_id != current_user.id and current_user.role not in ['admin', 'receptionist']:
        abort(403)
        
    form = AppointmentForm()
    # Populate doctors choices
    form.doctor.choices = [(d.id, f"{d.user.username} ({d.specialization})") for d in Doctor.query.all()]
    # Populate patient choices - Context aware
    if current_user.role == 'patient':
        current_appt_patient = Patient.query.filter_by(user_id=current_user.id).first()
        if current_appt_patient:
             form.patient.choices = [(current_appt_patient.id, current_appt_patient.name)]
        else:
             form.patient.choices = []
    else:
        # Admin / Receptionist / Doctor can choose any patient
        form.patient.choices = [(p.id, p.name) for p in Patient.query.all()]

    if form.validate_on_submit():
        appointment.doctor_id = form.doctor.data
        appointment.patient_id = form.patient.data
        appointment.date_time = form.date_time.data
        appointment.reason = form.reason.data
        db.session.commit()
        flash('Appointment updated!', 'success')
        return redirect(url_for('appointment.list_appointments'))
    elif request.method == 'GET':
        form.doctor.data = appointment.doctor_id
        form.patient.data = appointment.patient_id
        form.date_time.data = appointment.date_time
        form.reason.data = appointment.reason

    return render_template('appointment/book.html', title='Update Appointment', form=form, legend='Update Appointment')

@appointment.route("/appointment/<int:appointment_id>/delete", methods=['POST'])
@login_required
def delete_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    # Authorization check
    if appointment.patient_id != current_user.id and appointment.doctor.user_id != current_user.id and current_user.role not in ['admin', 'receptionist']:
        abort(403)
        
    db.session.delete(appointment)
    db.session.commit()
    flash('Appointment deleted!', 'success')
    return redirect(url_for('appointment.list_appointments'))
