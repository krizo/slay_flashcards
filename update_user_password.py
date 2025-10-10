"""
Script to update user password for testing login functionality.
Usage: python update_user_password.py
"""
import sys
from sqlalchemy.orm import Session

from core.db.database import SessionLocal
from core.services.user_service import UserService
from api.dependencies.auth import hash_password


def update_user_password(username: str, new_password: str):
    """Update user password in the database."""
    db: Session = SessionLocal()
    try:
        user_service = UserService(db)

        # Get user by name
        user = user_service.get_user_by_name(username)

        if not user:
            print(f"❌ User '{username}' not found")
            return False

        # Hash the new password
        password_hash = hash_password(new_password)

        # Update the user's password_hash
        user.password_hash = password_hash
        db.commit()

        print(f"✅ Password updated for user '{username}'")
        print(f"   Username: {username}")
        print(f"   Email: {user.email or 'N/A'}")
        print(f"   Password: {new_password}")
        print(f"\nYou can now login with:")
        print(f"   Username/Email: {username}")
        print(f"   Password: {new_password}")

        return True

    except Exception as e:
        print(f"❌ Error updating password: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()


def main():
    """Main function."""
    print("=" * 60)
    print("Update User Password for Testing")
    print("=" * 60)

    # Update Emila's password
    print("\n📝 Updating password for user 'Emila'...")
    update_user_password("Emila", "password123")

    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()
