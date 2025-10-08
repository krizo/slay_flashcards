#!/usr/bin/env python3
"""
Generate a valid JWT token for SlayFlashcards frontend development
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.db.database import get_db
from core.services.user_service import UserService
import jwt

# JWT Configuration (from auth.py)
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict):
    """Create JWT access token."""
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def main():
    """Main function to generate token."""
    print("🚀 Generating access token for SlayFlashcards...\n")

    db = next(get_db())

    try:
        user_service = UserService(db)

        # Get or verify existing user (Emila)
        user = user_service.get_user_by_name("Emila")

        if not user:
            print("❌ User 'Emila' not found!")
            return

        print(f"✅ Found user: {user.name} (id: {user.id})")

        # Generate access token
        access_token = create_access_token(
            data={"sub": user.name, "user_id": user.id}
        )

        print("\n" + "="*80)
        print("✅ Access token generated successfully!")
        print("="*80)
        print(f"\n👤 User: {user.name}")
        print(f"🆔 User ID: {user.id}")
        print(f"\n🔑 Access Token (valid for {ACCESS_TOKEN_EXPIRE_MINUTES} minutes):")
        print(f"\n{access_token}")
        print("\n" + "="*80)
        print("\n📝 Update frontend/src/services/apiClient.ts:")
        print("   Replace 'mock-token-placeholder' with the token above")
        print("="*80)

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
