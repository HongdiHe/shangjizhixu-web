"""
Create initial users for testing.

This script creates the following test users:
- admin (admin): Full system access
- submitter (question_submitter): Can create and submit questions
- ocr_editor (ocr_editor): Can edit OCR content
- ocr_reviewer (ocr_reviewer): Can review OCR content
- rewrite_editor (rewrite_editor): Can edit rewrite content
- rewrite_reviewer (rewrite_reviewer): Can review rewrite content

All users have password: password123
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.models.enums import UserRole
from app.core.security import get_password_hash


async def create_user(
    db: AsyncSession,
    username: str,
    email: str,
    password: str,
    role: UserRole,
    full_name: str,
    is_superuser: bool = False
) -> User:
    """Create a user if it doesn't exist."""
    # Check if user exists
    result = await db.execute(
        select(User).where(User.username == username)
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        print(f"✓ User '{username}' already exists, skipping...")
        return existing_user

    # Create new user
    user = User(
        username=username,
        email=email,
        hashed_password=get_password_hash(password),
        full_name=full_name,
        role=role,
        is_active=True,
        is_superuser=is_superuser
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    print(f"✓ Created user '{username}' with role '{role.value}'")
    return user


async def main():
    """Create all initial users."""
    print("=" * 60)
    print("Creating Initial Users")
    print("=" * 60)
    print()

    async with AsyncSessionLocal() as db:
        try:
            # Create admin user
            await create_user(
                db=db,
                username="admin",
                email="admin@example.com",
                password="password123",
                role=UserRole.ADMIN,
                full_name="系统管理员",
                is_superuser=True
            )

            # Create question submitter
            await create_user(
                db=db,
                username="submitter",
                email="submitter@example.com",
                password="password123",
                role=UserRole.QUESTION_SUBMITTER,
                full_name="题目录入员"
            )

            # Create OCR editor
            await create_user(
                db=db,
                username="ocr_editor",
                email="ocr_editor@example.com",
                password="password123",
                role=UserRole.OCR_EDITOR,
                full_name="OCR编辑员"
            )

            # Create OCR reviewer
            await create_user(
                db=db,
                username="ocr_reviewer",
                email="ocr_reviewer@example.com",
                password="password123",
                role=UserRole.OCR_REVIEWER,
                full_name="OCR审核员"
            )

            # Create rewrite editor
            await create_user(
                db=db,
                username="rewrite_editor",
                email="rewrite_editor@example.com",
                password="password123",
                role=UserRole.REWRITE_EDITOR,
                full_name="改写编辑员"
            )

            # Create rewrite reviewer
            await create_user(
                db=db,
                username="rewrite_reviewer",
                email="rewrite_reviewer@example.com",
                password="password123",
                role=UserRole.REWRITE_REVIEWER,
                full_name="改写审核员"
            )

            print()
            print("=" * 60)
            print("✓ All users created successfully!")
            print("=" * 60)
            print()
            print("Login credentials (all passwords: password123):")
            print("-" * 60)
            print("Admin:              username=admin")
            print("Question Submitter: username=submitter")
            print("OCR Editor:         username=ocr_editor")
            print("OCR Reviewer:       username=ocr_reviewer")
            print("Rewrite Editor:     username=rewrite_editor")
            print("Rewrite Reviewer:   username=rewrite_reviewer")
            print("-" * 60)

        except Exception as e:
            print(f"✗ Error creating users: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(main())
