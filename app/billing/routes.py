from flask import render_template, url_for, flash, redirect, request
from app import db
from app.billing import billing
from app.billing.forms import InvoiceForm
from app.models import Invoice, Patient
from flask_login import login_required

@billing.route("/invoices")
@login_required
def list_invoices():
    if current_user.role == 'admin' or current_user.role == 'receptionist':
        invoices = Invoice.query.all()
    elif current_user.role == 'doctor':
        # Doctors might see all or none? Usually staff sees all. 
        # For now, let's say staff (admin/receptionist) manages billing.
        # But if doctors want to see, they can. Let's allow doctors too for now.
        invoices = Invoice.query.all()
    else:
        # Patient
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        if patient:
            invoices = Invoice.query.filter_by(patient_id=patient.id).all()
        else:
            invoices = []
            
    return render_template('billing/list.html', invoices=invoices)

@billing.route("/invoice/new", methods=['GET', 'POST'])
@login_required
def create_invoice():
    form = InvoiceForm()
    form.patient.choices = [(p.id, p.name) for p in Patient.query.all()]
    
    if form.validate_on_submit():
        invoice = Invoice(patient_id=form.patient.data, 
                          description=form.description.data, 
                          amount=form.amount.data, 
                          status=form.status.data)
        db.session.add(invoice)
        db.session.commit()
        flash('Invoice created successfully!', 'success')
        return redirect(url_for('billing.list_invoices'))
        
    return render_template('billing/create.html', title='New Invoice', form=form)

@billing.route("/invoice/<int:invoice_id>")
@login_required
def view_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    return render_template('billing/view.html', invoice=invoice, title='Invoice Details')
