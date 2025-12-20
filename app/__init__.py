from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from app.config import Config

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    from app.main import main
    from app.auth import auth
    from app.patient import patient
    from app.doctor import doctor
    from app.appointment import appointment
    from app.billing import billing
    
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(patient)
    app.register_blueprint(doctor)
    app.register_blueprint(appointment)
    app.register_blueprint(billing)

    return app
