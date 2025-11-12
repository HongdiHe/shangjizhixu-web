"""Create a test question submitter user."""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.core.config import settings
from app.models.user import User
from app.models.enums import UserRole
from app.core.security import get_password_hash


async def create_question_submitter():
    """Create a question submitter test account."""
    # Create async engine
    engine = create_async_engine(
        str(settings.DATABASE_URI),
        echo=True,
        future=True,
    )

    AsyncSessionLocal = async_sessionmaker(
        engine,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async with AsyncSessionLocal() as db:
        try:
            # Check if user already exists
            from sqlalchemy import select
            result = await db.execute(
                select(User).where(User.username == "submitter")
            )
            existing_user = result.scalar_one_or_none()

            if existing_user:
                print("✓ Question submitter user already exists!")
                print(f"  Username: submitter")
                print(f"  Role: {existing_user.role}")
                return

            # Create new user
            new_user = User(
                username="submitter",
                email="submitter@example.com",
                full_name="题目录入员",
                hashed_password=get_password_hash("submitter123"),
                role=UserRole.QUESTION_SUBMITTER,
                is_active=True,
                is_superuser=False
            )

            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)

            print("✓ Question submitter user created successfully!")
            print(f"  Username: submitter")
            print(f"  Password: submitter123")
            print(f"  Role: {new_user.role}")
            print(f"  Email: {new_user.email}")

        except Exception as e:
            print(f"✗ Error creating user: {e}")
            await db.rollback()
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_question_submitter())
