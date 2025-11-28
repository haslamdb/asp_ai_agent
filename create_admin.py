#!/usr/bin/env python3
"""
Secure Admin User Creation Script

Usage:
    python create_admin.py

This script creates admin users with secure, randomly generated passwords.
Use this in production instead of hardcoded credentials.
"""

import os
import sys
import secrets
import getpass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the app and models
from unified_server import app, db
from auth_models import User


def generate_secure_password(length=20):
    """Generate a cryptographically secure random password"""
    return secrets.token_urlsafe(length)


def create_admin_user(email=None, full_name=None, custom_password=None):
    """
    Create an admin user with a secure password

    Args:
        email: Admin email address (will prompt if not provided)
        full_name: Admin full name (will prompt if not provided)
        custom_password: Optional custom password (generates random if not provided)
    """
    with app.app_context():
        # Get email
        if not email:
            email = input("Enter admin email address: ").strip()

        # Validate email
        if not email or '@' not in email:
            print("❌ Invalid email address")
            return False

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            print(f"❌ User with email {email} already exists")

            # Ask if they want to make them admin
            if not existing_user.is_admin:
                make_admin = input("Make this user an admin? (yes/no): ").strip().lower()
                if make_admin == 'yes':
                    existing_user.is_admin = True
                    db.session.commit()
                    print(f"✅ User {email} is now an admin")
                return True
            else:
                print(f"ℹ️  User {email} is already an admin")
                return True

        # Get full name
        if not full_name:
            full_name = input("Enter admin full name: ").strip()

        if not full_name:
            print("❌ Full name is required")
            return False

        # Generate or get password
        if custom_password:
            password = custom_password
            print("⚠️  Using custom password (ensure it's strong!)")
        else:
            use_random = input("Generate random password? (yes/no, default: yes): ").strip().lower()
            if use_random == 'no':
                password = getpass.getpass("Enter password: ")
                password_confirm = getpass.getpass("Confirm password: ")

                if password != password_confirm:
                    print("❌ Passwords don't match")
                    return False

                if len(password) < 12:
                    print("❌ Password must be at least 12 characters")
                    return False
            else:
                password = generate_secure_password(20)

        # Create admin user
        admin = User(
            email=email,
            full_name=full_name,
            is_admin=True,
            is_active=True,
            email_verified=True  # Mark as verified for admin
        )
        admin.set_password(password)

        db.session.add(admin)
        db.session.commit()

        print("\n" + "=" * 60)
        print("✅ Admin User Created Successfully")
        print("=" * 60)
        print(f"📧 Email:     {email}")
        print(f"👤 Name:      {full_name}")
        if not custom_password and use_random != 'no':
            print(f"🔑 Password:  {password}")
            print("=" * 60)
            print("⚠️  SAVE THIS PASSWORD SECURELY - it will not be shown again!")
        else:
            print("🔑 Password:  [as entered]")
        print("=" * 60)

        return True


def list_admins():
    """List all admin users"""
    with app.app_context():
        admins = User.query.filter_by(is_admin=True).all()

        if not admins:
            print("No admin users found")
            return

        print("\n" + "=" * 60)
        print("Current Admin Users")
        print("=" * 60)
        for admin in admins:
            status = "✅ Active" if admin.is_active else "❌ Inactive"
            verified = "✓ Verified" if admin.email_verified else "✗ Not verified"
            print(f"\n📧 {admin.email}")
            print(f"   Name:     {admin.full_name}")
            print(f"   Status:   {status}")
            print(f"   Email:    {verified}")
            print(f"   ID:       {admin.id}")
        print("=" * 60)


def main():
    """Main entry point"""
    # Check if running in production
    is_production = os.environ.get('FLASK_ENV') == 'production'

    if is_production:
        print("🔒 Running in PRODUCTION mode")
    else:
        print("🔧 Running in DEVELOPMENT mode")

    print("\nAdmin User Management")
    print("=" * 60)
    print("1. Create new admin user")
    print("2. List all admin users")
    print("3. Exit")
    print("=" * 60)

    choice = input("\nSelect option (1-3): ").strip()

    if choice == '1':
        create_admin_user()
    elif choice == '2':
        list_admins()
    elif choice == '3':
        print("Goodbye!")
        return
    else:
        print("❌ Invalid option")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
