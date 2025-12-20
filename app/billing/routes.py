from flask import render_template, url_for, flash, redirect, request
from app import db
from app.billing import billing
from app.billing.forms import InvoiceForm
from app.models import Invoice, Patient
from flask_login import login_required

@billing.route("/invoices")
@login_required
def list_invoices():
    invoices = Invoice.query.all()
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
