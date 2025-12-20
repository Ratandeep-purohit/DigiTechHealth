from flask import render_template, url_for, flash, redirect, request, abort
from app import db
from app.patient import patient
from app.patient.forms import PatientForm
from app.models import Patient
from flask_login import login_required, current_user

@patient.route("/patients")
@login_required
def list_patients():
    patients = Patient.query.all()
    return render_template('patient/list.html', patients=patients)

@patient.route("/patient/new", methods=['GET', 'POST'])
@login_required
def add_patient():
    form = PatientForm()
    if form.validate_on_submit():
        patient = Patient(name=form.name.data, age=form.age.data, gender=form.gender.data,
                          contact=form.contact.data, address=form.address.data,
                          medical_history=form.medical_history.data)
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
