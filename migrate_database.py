#!/usr/bin/env python3
"""
Database migration script to add 2FA columns to the users table.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.main import app
from src.models.user import db
import sqlite3

def migrate_database():
    """Add 2FA columns to the users table."""
    with app.app_context():
        # Get the database file path
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        
        print(f"Migrating database: {db_path}")
        
        # Connect to the database directly
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # Check if the columns already exist
            cursor.execute("PRAGMA table_info(users)")
            columns = [column[1] for column in cursor.fetchall()]
            
            # Add is_2fa_enabled column if it doesn't exist
            if 'is_2fa_enabled' not in columns:
                cursor.execute("ALTER TABLE users ADD COLUMN is_2fa_enabled BOOLEAN DEFAULT 0")
                print("Added is_2fa_enabled column")
            else:
                print("is_2fa_enabled column already exists")
            
            # Add totp_secret column if it doesn't exist
            if 'totp_secret' not in columns:
                cursor.execute("ALTER TABLE users ADD COLUMN totp_secret VARCHAR(16)")
                print("Added totp_secret column")
            else:
                print("totp_secret column already exists")
            
            # Add phone_number column if it doesn't exist
            if 'phone_number' not in columns:
                cursor.execute("ALTER TABLE users ADD COLUMN phone_number VARCHAR(20)")
                print("Added phone_number column")
            else:
                print("phone_number column already exists")
            
            # Commit the changes
            conn.commit()
            print("Database migration completed successfully!")
            
        except Exception as e:
            print(f"Error during migration: {e}")
            conn.rollback()
        finally:
            conn.close()

if __name__ == '__main__':
    migrate_database()

