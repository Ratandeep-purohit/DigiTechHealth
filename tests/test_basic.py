
import unittest
from app import create_app, db
from app.config import Config
from app.models import User, Patient

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class BasicTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'DigiTechHealth', response.data)

    def test_register_login(self):
        # Register
        response = self.client.post('/register', data=dict(
            username='testuser',
            email='test@example.com',
            password='password',
            confirm_password='password',
            role='doctor'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # Verify user exists
        user = User.query.filter_by(username='testuser').first()
        self.assertIsNotNone(user)

        # Logout
        self.client.get('/logout', follow_redirects=True)

        # Login
        response = self.client.post('/login', data=dict(
            email='test@example.com',
            password='password'
        ), follow_redirects=True)
        # Check for logout link which indicates user is logged in
        self.assertIn(b'Logout', response.data)

    def test_add_patient(self):
        # Must be logged in
        self.client.post('/register', data=dict(
            username='doctor',
            email='doctor@example.com',
            password='password',
            confirm_password='password',
            role='doctor'
        ), follow_redirects=True)

        self.client.post('/login', data=dict(
            email='doctor@example.com',
            password='password'
        ), follow_redirects=True)

        # Add Patient
        response = self.client.post('/patient/new', data=dict(
            name='John Doe',
            age=30,
            gender='Male',
            contact='1234567890',
            address='123 Main St',
            medical_history='None'
        ), follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Patient has been added!', response.data)
        
        # Verify patient in DB
        patient = Patient.query.filter_by(name='John Doe').first()
        self.assertIsNotNone(patient)

if __name__ == '__main__':
    unittest.main()
