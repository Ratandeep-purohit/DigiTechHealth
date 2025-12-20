from flask import Blueprint

patient = Blueprint('patient', __name__)

from app.patient import routes
