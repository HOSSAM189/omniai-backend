#!/usr/bin/env python3
"""
Script to create an AdminUser for the admin panel with correct password hashing.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.models.admin import AdminUser, db
from src.main import app

def create_admin_user():
    """Create an AdminUser for the admin panel."""
    with app.app_context():
        # Delete existing admin user if exists
        existing_admin = AdminUser.query.filter_by(username='admin').first()
        if existing_admin:
            db.session.delete(existing_admin)
            db.session.commit()
            print("Deleted existing admin user.")

        # Create admin user with correct constructor
        password = "admin123456"  # Strong password for testing
        
        admin_user = AdminUser(
            username='admin',
            email='admin@omniai.com',
            password=password,  # This will be hashed by the constructor
            role='SuperAdmin'
        )
        
        db.session.add(admin_user)
        db.session.commit()
        
        print("AdminUser created successfully!")
        print(f"Username: admin")
        print(f"Password: {password}")
        print(f"Email: admin@omniai.com")
        print(f"Role: SuperAdmin")
        print("You can now log in to the admin panel.")
        
        # Test password verification
        test_check = admin_user.check_password(password)
        print(f"Password verification test: {'PASSED' if test_check else 'FAILED'}")

if __name__ == '__main__':
    create_admin_user()

