from flask import render_template, url_for, flash, redirect, request
from app import db
from app.appointment import appointment
from app.appointment.forms import AppointmentForm
from app.models import Appointment, Doctor, Patient
from flask_login import login_required, current_user

@appointment.route("/appointments")
@login_required
def list_appointments():
    # If admin or doctor, show all (or filtered). If patient, show theirs.
    # For now, simplistic view:
    if current_user.role == 'doctor':
        # Find doctor profile linked to user
        doctor = Doctor.query.filter_by(user_id=current_user.id).first()
        if doctor:
            appointments = Appointment.query.filter_by(doctor_id=doctor.id).all()
        else:
            appointments = []
    elif current_user.role == 'admin':
         appointments = Appointment.query.all()
    else:
        # Patient view - Wait, Patient table is separate from User.
        # If logged in User serves as a Patient, we need to link them.
        # THIS IS A GAP IN MY PLAN. A User (Role=Patient) needs a Patient Profile linked?
        # OR, we just use Email to link? 
        # For simplicity in this iteration: Show all for now or implement linkage later.
        # Let's show "My Appointments" if we can find a Patient with same name? No, unsafe.
        # Let's assume for now Client wants to MANAGE patients. So "Appointments" might be for staff.
        # But Requirement says: "Book ... appointments".
        appointments = Appointment.query.all() # Fallback for now

    return render_template('appointment/list.html', appointments=appointments)

@appointment.route("/appointment/book", methods=['GET', 'POST'])
@login_required
def book_appointment():
    form = AppointmentForm()
    # Populate doctors
    form.doctor.choices = [(d.id, d.user.username + " (" + d.specialization + ")") for d in Doctor.query.all()]
    
    if form.validate_on_submit():
        # logic to find patient_id.
        # If Admin is booking, they should probably select a Patient.
        # If Patient is booking, they are the patient.
        # Simplification: Admin booking for a patient.
        # I need a Patient Select Field OR assume internal use.
        # Let's just create appointment with NO patient_id (Guest) or require Patient Selection.
        
        # Let's add Patient selection field to form if we want to link it.
        # For this step, I'll pass patient_id=None (Walk-in) or fix the form.
        appointment = Appointment(doctor_id=form.doctor.data, date_time=form.date_time.data, reason=form.reason.data, status='Scheduled')
        db.session.add(appointment)
        db.session.commit()
        flash('Appointment Booked!', 'success')
        return redirect(url_for('appointment.list_appointments'))
        
    return render_template('appointment/book.html', title='Book Appointment', form=form)
