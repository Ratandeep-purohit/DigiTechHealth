from flask import render_template, jsonify
from app.main import main
from app.models import User, Patient, Appointment, Doctor, Invoice
from app import db
from sqlalchemy import func
import datetime
from flask_login import login_required

@main.route("/")
def index():
    return render_template('landing.html', title='Home')

@main.route("/home")
@login_required
def home():
    # 1. New Patients (Last 7 days)
    seven_days_ago = datetime.datetime.now() - datetime.timedelta(days=7)
    new_patients = Patient.query.filter(Patient.date_created >= seven_days_ago).count()
    
    # 2. Today's Appointments (Proxy for Operations/Activity)
    today_start = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = datetime.datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
    todays_appointments = Appointment.query.filter(
        Appointment.date_time >= today_start,
        Appointment.date_time <= today_end
    ).count()

    # 3. Active Doctors (Proxy for Satisfaction/Resources)
    active_doctors = Doctor.query.count()

    return render_template('home.html', title='Home',
                           new_patients=new_patients,
                           todays_appointments=todays_appointments,
                           active_doctors=active_doctors)

@main.route("/dashboard")
@login_required
def dashboard():
    # Counts
    patient_count = Patient.query.count()
    appointment_count = Appointment.query.count()
    doctor_count = Doctor.query.count()
    
    # Revenue (Real Calculation)
    revenue = db.session.query(func.sum(Invoice.amount)).scalar() or 0
    revenue = int(revenue) 
    
    # Upcoming Appointments (Limit 5)
    upcoming_appointments = Appointment.query.filter(
        Appointment.status == 'Scheduled'
    ).order_by(Appointment.date_time.asc()).limit(5).all()

    # Chart Data: Appointments per day for last 7 days
    today = datetime.datetime.now()
    dates = []
    counts = []
    
    for i in range(6, -1, -1):
        date = today - datetime.timedelta(days=i)
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        count = Appointment.query.filter(
            Appointment.date_time >= start_of_day,
            Appointment.date_time <= end_of_day
        ).count()
        
        dates.append(date.strftime('%a')) # Mon, Tue
        counts.append(count)

    return render_template('dashboard.html', 
                           title='Dashboard',
                           patient_count=patient_count,
                           appointment_count=appointment_count,
                           doctor_count=doctor_count,
                           revenue=revenue,
                           upcoming_appointments=upcoming_appointments,
                           chart_labels=dates,
                           chart_data=counts)

@main.route("/api/dashboard/stats")
@login_required
def dashboard_stats():
    patient_count = Patient.query.count()
    appointment_count = Appointment.query.count()
    doctor_count = Doctor.query.count()
    revenue = db.session.query(func.sum(Invoice.amount)).scalar() or 0
    
    return jsonify({
        'patients': patient_count,
        'appointments': appointment_count,
        'doctors': doctor_count,
        'revenue': int(revenue)
    })
