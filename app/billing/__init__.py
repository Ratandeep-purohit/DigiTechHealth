from flask import Blueprint

billing = Blueprint('billing', __name__)

from app.billing import routes
