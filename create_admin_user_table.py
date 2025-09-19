#!/usr/bin/env python3
"""
Script to create an AdminUser for the admin panel.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.models.admin import AdminUser, db
from src.main import app
import bcrypt

def create_admin_user():
    """Create an AdminUser for the admin panel."""
    with app.app_context():
        # Check if admin user already exists
        admin_user = AdminUser.query.filter_by(username='admin').first()
        if admin_user:
            print("AdminUser already exists!")
            print(f"Username: {admin_user.username}")
            print(f"Email: {admin_user.email}")
            print(f"Role: {admin_user.role}")
            print(f"Is Active: {admin_user.is_active}")
            return

        # Create admin user
        password = "admin123456"  # Strong password for testing
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        admin_user = AdminUser(
            username='admin',
            email='admin@omniai.com',
            password_hash=password_hash.decode('utf-8'),
            first_name='Admin',
            last_name='User',
            role='super_admin',  # Highest level admin
            is_active=True,
            permissions=['user_management', 'payment_management', 'system_settings', 'analytics']
        )
        
        db.session.add(admin_user)
        db.session.commit()
        
        print("AdminUser created successfully!")
        print(f"Username: admin")
        print(f"Password: {password}")
        print(f"Email: admin@omniai.com")
        print(f"Role: super_admin")
        print("You can now log in to the admin panel.")

if __name__ == '__main__':
    create_admin_user()

