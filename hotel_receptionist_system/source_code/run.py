from app import create_app, db
from app.models import Admin
import os
from werkzeug.security import generate_password_hash
import hashlib

app = create_app()

# Create default admin user if it doesn't exist
with app.app_context():
    # Create all tables
    db.create_all()
    
    # Check if admin user exists
    admin = Admin.query.filter_by(username='admin').first()
    if not admin:
        admin = Admin(username='admin')
        # Use SHA2-256 hashing to match the schema.sql format
        admin.password_hash = hashlib.sha256('admin123'.encode()).hexdigest()
        db.session.add(admin)
        db.session.commit()
        print("Default admin user created!")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')