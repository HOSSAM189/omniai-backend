#!/usr/bin/env python3
"""
Script to create an admin user for testing 2FA functionality.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.models.user import User, db
from src.main import app
import bcrypt

def create_admin_user():
    """Create an admin user for testing."""
    with app.app_context():
        # Check if admin user already exists
        admin_user = User.query.filter_by(username='admin').first()
        if admin_user:
            print("Admin user already exists!")
            print(f"Username: {admin_user.username}")
            print(f"Email: {admin_user.email}")
            print(f"User Type: {admin_user.user_type}")
            print(f"2FA Enabled: {admin_user.is_2fa_enabled}")
            return

        # Create admin user
        password = "admin123456"  # Strong password for testing
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        admin_user = User(
            username='admin',
            email='admin@omniai.com',
            password_hash=password_hash.decode('utf-8'),
            first_name='Admin',
            last_name='User',
            user_type='admin',  # Set as admin
            is_active=True,
            email_verified=True,
            is_2fa_enabled=False  # Will be enabled through the UI
        )
        
        db.session.add(admin_user)
        db.session.commit()
        
        print("Admin user created successfully!")
        print(f"Username: admin")
        print(f"Password: {password}")
        print(f"Email: admin@omniai.com")
        print("You can now log in and set up 2FA.")

if __name__ == '__main__':
    create_admin_user()

