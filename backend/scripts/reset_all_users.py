"""Reset all users with correct passwords - run inside Docker container."""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.models.enums import UserRole
from app.core.security import get_password_hash


async def reset_users():
    """Delete all users and recreate them with correct passwords."""
    print("=" * 70)
    print("RESET ALL USERS - This will delete all existing users")
    print("=" * 70)
    print()
    print("⚠️  WARNING: This will delete ALL users in the database!")
    print("   Make sure no important data will be lost.")
    print()

    # Auto-confirm in script mode
    confirm = input("Type 'YES' to continue: ")
    if confirm != "YES":
        print("Aborted.")
        return

    print()
    print("Starting user reset...")
    print()

    async with AsyncSessionLocal() as db:
        try:
            # Delete all users
            print("1. Deleting all existing users...")
            result = await db.execute(delete(User))
            deleted_count = result.rowcount
            await db.commit()
            print(f"   ✓ Deleted {deleted_count} users")
            print()

            # Create all users with password123
            print("2. Creating new users with password: password123")
            print()

            users_to_create = [
                {
                    "username": "admin",
                    "email": "admin@example.com",
                    "password": "password123",
                    "role": UserRole.ADMIN,
                    "full_name": "系统管理员",
                    "is_superuser": True
                },
                {
                    "username": "submitter",
                    "email": "submitter@example.com",
                    "password": "password123",
                    "role": UserRole.QUESTION_SUBMITTER,
                    "full_name": "题目录入员",
                    "is_superuser": False
                },
                {
                    "username": "ocr_editor",
                    "email": "ocr_editor@example.com",
                    "password": "password123",
                    "role": UserRole.OCR_EDITOR,
                    "full_name": "OCR编辑员",
                    "is_superuser": False
                },
                {
                    "username": "ocr_reviewer",
                    "email": "ocr_reviewer@example.com",
                    "password": "password123",
                    "role": UserRole.OCR_REVIEWER,
                    "full_name": "OCR审核员",
                    "is_superuser": False
                },
                {
                    "username": "rewrite_editor",
                    "email": "rewrite_editor@example.com",
                    "password": "password123",
                    "role": UserRole.REWRITE_EDITOR,
                    "full_name": "改写编辑员",
                    "is_superuser": False
                },
                {
                    "username": "rewrite_reviewer",
                    "email": "rewrite_reviewer@example.com",
                    "password": "password123",
                    "role": UserRole.REWRITE_REVIEWER,
                    "full_name": "改写审核员",
                    "is_superuser": False
                }
            ]

            for user_data in users_to_create:
                user = User(
                    username=user_data["username"],
                    email=user_data["email"],
                    hashed_password=get_password_hash(user_data["password"]),
                    full_name=user_data["full_name"],
                    role=user_data["role"],
                    is_active=True,
                    is_superuser=user_data["is_superuser"]
                )
                db.add(user)
                print(f"   ✓ Created: {user_data['username']:20} ({user_data['role'].value})")

            await db.commit()

            print()
            print("=" * 70)
            print("✓ All users reset successfully!")
            print("=" * 70)
            print()
            print("All users can now login with password: password123")
            print("-" * 70)
            for user_data in users_to_create:
                print(f"{user_data['role'].value:25} username={user_data['username']}")
            print("-" * 70)

        except Exception as e:
            print(f"✗ Error resetting users: {e}")
            await db.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(reset_users())
