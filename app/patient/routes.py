from flask import render_template, url_for, flash, redirect, request, abort
from app import db
from app.patient import patient
from app.patient.forms import PatientForm
from app.models import Patient
from app.utils import save_picture
from flask_login import login_required, current_user

@patient.route("/patients")
@login_required
def list_patients():
    if current_user.role in ['admin', 'doctor', 'receptionist']:
        patients = Patient.query.all()
        return render_template('patient/list.html', patients=patients)
    else:
        # Patient redirected to their own profile
        patient_record = Patient.query.filter_by(user_id=current_user.id).first()
        if patient_record:
            return redirect(url_for('patient.view_patient', patient_id=patient_record.id))
        else:
            flash('No patient record found for your account.', 'warning')
            return redirect(url_for('main.home'))

@patient.route("/patient/<int:patient_id>")
@login_required
def view_patient(patient_id):
    patient_record = Patient.query.get_or_404(patient_id)
    # Authorization check
    if current_user.role not in ['admin', 'doctor', 'receptionist']:
        if patient_record.user_id != current_user.id:
            abort(403)
    return render_template('patient/view.html', patient=patient_record, title='Patient Details')

@patient.route("/patient/new", methods=['GET', 'POST'])
@login_required
def add_patient():
    form = PatientForm()
    if form.validate_on_submit():
        image_file = 'default.jpg'
        if form.picture.data:
            image_file = save_picture(form.picture.data)
            
        patient = Patient(name=form.name.data, age=form.age.data, gender=form.gender.data,
                          contact=form.contact.data, address=form.address.data,
                          medical_history=form.medical_history.data, image_file=image_file)
        db.session.add(patient)
        db.session.commit()
        flash('Patient has been added!', 'success')
        return redirect(url_for('patient.list_patients'))
    return render_template('patient/add.html', title='Add Patient', form=form, legend='Add New Patient')

@patient.route("/patient/<int:patient_id>/update", methods=['GET', 'POST'])
@login_required
def update_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    form = PatientForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            patient.image_file = picture_file
        patient.name = form.name.data
        patient.age = form.age.data
        patient.gender = form.gender.data
        patient.contact = form.contact.data
        patient.address = form.address.data
        patient.medical_history = form.medical_history.data
        db.session.commit()
        flash('Patient details have been updated!', 'success')
        return redirect(url_for('patient.list_patients'))
    elif request.method == 'GET':
        form.name.data = patient.name
        form.age.data = patient.age
        form.gender.data = patient.gender
        form.contact.data = patient.contact
        form.address.data = patient.address
        form.medical_history.data = patient.medical_history
    return render_template('patient/add.html', title='Update Patient', form=form, legend='Update Patient')

@patient.route("/patient/<int:patient_id>/delete", methods=['POST'])
@login_required
def delete_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    db.session.delete(patient)
    db.session.commit()
    flash('Patient has been deleted!', 'success')
    return redirect(url_for('patient.list_patients'))
