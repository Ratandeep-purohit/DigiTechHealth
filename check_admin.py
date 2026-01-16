from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    admins = User.query.filter_by(role='admin').all()
    if admins:
        print("Found existing admin(s):")
        for admin in admins:
            print(f"Username: {admin.username}, Email: {admin.email}") 
            # Note: We can't see the password, but we can reset it if needed.
    else:
        print("No admin found. Creating one...")
        admin = User(username='admin', email='admin@digitech.com', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("Created admin user:")
        print("Username: admin")
        print("Email: admin@digitech.com")
        print("Password: admin123")
