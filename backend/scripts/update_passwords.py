"""Update all user passwords to password123."""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.core.security import get_password_hash


async def update_all_passwords():
    """Update all user passwords to password123."""
    print("=" * 60)
    print("Updating All User Passwords to password123")
    print("=" * 60)
    print()

    new_password = "password123"
    new_hash = get_password_hash(new_password)

    async with AsyncSessionLocal() as db:
        try:
            # Get all users
            result = await db.execute(select(User))
            users = result.scalars().all()

            if not users:
                print("No users found in database")
                return

            print(f"Found {len(users)} users. Updating passwords...")
            print()

            for user in users:
                user.hashed_password = new_hash
                print(f"✓ Updated password for user: {user.username} ({user.role})")

            await db.commit()

            print()
            print("=" * 60)
            print("✓ All passwords updated successfully!")
            print("=" * 60)
            print()
            print("All users can now login with password: password123")
            print("-" * 60)
            for user in users:
                print(f"{user.role:20} username={user.username}")
            print("-" * 60)

        except Exception as e:
            print(f"✗ Error updating passwords: {e}")
            await db.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(update_all_passwords())
