from flask import render_template, request, flash, redirect, url_for, abort, send_file
import pandas as pd
from io import BytesIO
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
    db.session.delete(user)
    db.session.commit()
    flash('Doctor has been deleted!', 'success')
    return redirect(url_for('doctor.list_doctors'))


@doctor.route("/doctor/template")
@login_required
def download_doctor_template():
    if current_user.role != 'admin':
        abort(403)
    
    # Create a DataFrame with the required columns
    columns = ['Username', 'Email', 'Password', 'Specialization', 'Availability']
    df = pd.DataFrame(columns=columns)
    
    # Create a BytesIO buffer to hold the Excel file
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Doctors_Template')
        
    output.seek(0)
    
    return send_file(output, as_attachment=True, download_name="doctor_template.xlsx", mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


@doctor.route("/doctor/import", methods=['POST'])
@login_required
def import_doctors():
    if current_user.role != 'admin':
        abort(403)
        
    if 'file' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('doctor.list_doctors'))
        
    file = request.files['file']
    
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('doctor.list_doctors'))
        
    if file and file.filename.endswith('.xlsx'):
        try:
            df = pd.read_excel(file)
            
            # Check if required columns exist
            required_columns = ['Username', 'Email', 'Password', 'Specialization', 'Availability']
            if not all(col in df.columns for col in required_columns):
                flash('Invalid file format. Please use the template.', 'danger')
                return redirect(url_for('doctor.list_doctors'))
            
            count = 0
            for index, row in df.iterrows():
                # Check for existing user
                existing_user = User.query.filter((User.username == row['Username']) | (User.email == row['Email'])).first()
                if existing_user:
                    continue # Skip duplicates
                
                # Create User
                user = User(username=row['Username'], email=row['Email'], role='doctor')
                user.set_password(str(row['Password'])) # Ensure password is string
                db.session.add(user)
                db.session.flush() # Get ID
                
                # Create Doctor
                doctor = Doctor(user_id=user.id, 
                                specialization=row['Specialization'], 
                                availability=row.get('Availability', 'Mon-Fri 9am-5pm'))
                db.session.add(doctor)
                count += 1
                
            db.session.commit()
            flash(f'{count} doctors imported successfully!', 'success')
            
        except Exception as e:
            flash(f'Error importing file: {str(e)}', 'danger')
    else:
        flash('Invalid file type. Please upload an Excel file (.xlsx)', 'danger')
        
    return redirect(url_for('doctor.list_doctors'))


@doctor.route("/doctor/export")
@login_required
def export_doctors():
    if current_user.role != 'admin':
        abort(403)
        
    doctors = Doctor.query.all()
    
    data = []
    for doctor in doctors:
        data.append({
            'Username': doctor.user.username,
            'Email': doctor.user.email,
            'Specialization': doctor.specialization,
            'Availability': doctor.availability
        })
        
    df = pd.DataFrame(data)
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Doctors')
        
    output.seek(0)
    
    return send_file(output, as_attachment=True, download_name="doctors_export.xlsx", mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

