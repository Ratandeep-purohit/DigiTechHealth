from flask import Blueprint

doctor = Blueprint('doctor', __name__)

from app.doctor import routes
