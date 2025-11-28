#!/usr/bin/env python3
"""
Database Migration: Add Email Verification Fields
Adds verification_token and verification_token_expires to User table
"""

import sqlite3
import sys
from pathlib import Path

def migrate_database(db_path='asp_sessions.db'):
    """Add email verification fields to User table"""

    print(f"Migrating database: {db_path}")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if columns already exist
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]

        migrations_needed = []

        if 'verification_token' not in columns:
            migrations_needed.append('verification_token')

        if 'verification_token_expires' not in columns:
            migrations_needed.append('verification_token_expires')

        if not migrations_needed:
            print("✓ Database already up to date - no migration needed")
            return True

        print(f"Adding columns: {', '.join(migrations_needed)}")

        # Add verification_token column if needed
        if 'verification_token' in migrations_needed:
            cursor.execute("""
                ALTER TABLE users
                ADD COLUMN verification_token VARCHAR(100) UNIQUE
            """)
            print("✓ Added verification_token column")

        # Add verification_token_expires column if needed
        if 'verification_token_expires' in migrations_needed:
            cursor.execute("""
                ALTER TABLE users
                ADD COLUMN verification_token_expires DATETIME
            """)
            print("✓ Added verification_token_expires column")

        conn.commit()

        print("\n✅ Migration completed successfully!")
        print("\nNote: Existing users have email_verified=False by default.")
        print("They will need to verify their email on next login, or you can")
        print("manually set email_verified=True for trusted existing users.")

        return True

    except sqlite3.Error as e:
        print(f"❌ Migration failed: {e}")
        return False

    finally:
        if conn:
            conn.close()


def show_user_status(db_path='asp_sessions.db'):
    """Show current user verification status"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, email, full_name, email_verified, created_at
            FROM users
            ORDER BY created_at DESC
        """)

        users = cursor.fetchall()

        if not users:
            print("\nNo users in database")
            return

        print("\n" + "="*80)
        print("Current User Status:")
        print("="*80)
        print(f"{'ID':<5} {'Email':<30} {'Name':<20} {'Verified':<10} {'Created'}")
        print("-"*80)

        for user in users:
            user_id, email, name, verified, created = user
            verified_str = "✓ Yes" if verified else "✗ No"
            print(f"{user_id:<5} {email:<30} {name:<20} {verified_str:<10} {created}")

        print("="*80)

        unverified = sum(1 for u in users if not u[3])
        if unverified > 0:
            print(f"\n⚠️  {unverified} user(s) need email verification")

    except sqlite3.Error as e:
        print(f"Error checking user status: {e}")
    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    db_path = 'asp_sessions.db'

    # Check if database exists
    if not Path(db_path).exists():
        print(f"❌ Database not found: {db_path}")
        print("The database will be created when you run the application.")
        sys.exit(1)

    # Run migration
    success = migrate_database(db_path)

    # Show user status
    if success:
        show_user_status(db_path)

    sys.exit(0 if success else 1)
