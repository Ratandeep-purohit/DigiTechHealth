from flask import render_template, request, flash, redirect, url_for, abort
from app.doctor import doctor
from app.doctor.forms import DoctorForm, AddDoctorForm, UpdateDoctorForm
from app.models import Doctor, User
from app import db
from flask_login import login_required, current_user

@doctor.route("/doctors")
@login_required
def list_doctors():
    doctors = Doctor.query.all()
    return render_template('doctor/list.html', doctors=doctors)

@doctor.route("/doctor/profile", methods=['GET', 'POST'])
@login_required
def profile():
    if current_user.role != 'doctor':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))
        
    doctor_profile = Doctor.query.filter_by(user_id=current_user.id).first()
    if not doctor_profile:
        # Create if missing (shouldn't happen usually if created properly)
        doctor_profile = Doctor(user_id=current_user.id, specialization="General", availability="Mon-Fri")
        db.session.add(doctor_profile)
        db.session.commit()
    
    form = DoctorForm()
    if form.validate_on_submit():
        doctor_profile.specialization = form.specialization.data
        doctor_profile.availability = form.availability.data
        db.session.commit()
        flash('Profile updated!', 'success')
        return redirect(url_for('doctor.profile'))
    
    elif request.method == 'GET':
        form.specialization.data = doctor_profile.specialization
        form.availability.data = doctor_profile.availability
        
    return render_template('doctor/profile.html', title='My Profile', form=form)

@doctor.route("/doctor/add", methods=['GET', 'POST'])
@login_required
def add_doctor():
    # Ideally check if current_user.role == 'admin' here
    form = AddDoctorForm()
    if form.validate_on_submit():
        # 1. Create User
        user = User(username=form.username.data, email=form.email.data, role='doctor')
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.flush() # Get user.id
        
        # 2. Create Doctor Profile
        doctor = Doctor(user_id=user.id, 
                        specialization=form.specialization.data, 
                        availability=form.availability.data)
        db.session.add(doctor)
        db.session.commit()
        
        flash(f'Doctor account created for {form.username.data}!', 'success')
        return redirect(url_for('doctor.list_doctors'))
        
    return render_template('doctor/add.html', title='Add Doctor', form=form)

@doctor.route("/doctor/<int:doctor_id>/update", methods=['GET', 'POST'])
@login_required
def update_doctor(doctor_id):
    # Authorization: Only admins should update other doctors
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('doctor.list_doctors'))
        
    doctor = Doctor.query.get_or_404(doctor_id)
    form = UpdateDoctorForm(original_username=doctor.user.username, original_email=doctor.user.email)
    
    if form.validate_on_submit():
        doctor.user.username = form.username.data
        doctor.user.email = form.email.data
        doctor.specialization = form.specialization.data
        doctor.availability = form.availability.data
        db.session.commit()
        flash('Doctor profile updated!', 'success')
        return redirect(url_for('doctor.list_doctors'))
    elif request.method == 'GET':
        form.username.data = doctor.user.username
        form.email.data = doctor.user.email
        form.specialization.data = doctor.specialization
        form.availability.data = doctor.availability
        
    return render_template('doctor/add.html', title='Update Doctor', form=form, legend='Update Doctor Details')

@doctor.route("/doctor/<int:doctor_id>/delete", methods=['POST'])
@login_required
def delete_doctor(doctor_id):
    if current_user.role != 'admin':
        abort(403)
        
    doctor = Doctor.query.get_or_404(doctor_id)
    # Depending on requirements, we might want to keep the user or delete them?
    # Usually "Delete Doctor" implies removing them from the system.
    # We should probably delete the User account too if it's strictly a doctor account.
    user = doctor.user
    db.session.delete(doctor)
    db.session.delete(user) # Optional: Delete associated user account
    db.session.commit()
    flash('Doctor has been deleted!', 'success')
    return redirect(url_for('doctor.list_doctors'))
