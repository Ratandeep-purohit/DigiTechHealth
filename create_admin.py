from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    # Check if 'admin' exists
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        print("Creating default 'admin' user...")
        admin = User(username='admin', email='admin@digitech.com', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("Created successfully.")
    else:
        print("User 'admin' already exists. Resetting password to 'admin123'...")
        admin.set_password('admin123')
        # Ensure role is admin
        admin.role = 'admin' 
        db.session.commit()
        print("Password reset successfully.")

    print("Credentials:")
    print("Username: admin")
    print("Password: admin123")
