from flask import Blueprint

appointment = Blueprint('appointment', __name__)

from app.appointment import routes
