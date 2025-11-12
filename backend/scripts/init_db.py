"""
Initialize database - create all tables.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import engine, Base
from app.models.user import User
from app.models.question import Question


async def init_db():
    """Create all database tables."""
    print("=" * 60)
    print("Initializing Database")
    print("=" * 60)
    print()

    try:
        async with engine.begin() as conn:
            print("Creating all tables...")
            await conn.run_sync(Base.metadata.create_all)
            print("✓ All tables created successfully!")

    except Exception as e:
        print(f"✗ Error initializing database: {e}")
        raise

    print()
    print("=" * 60)
    print("✓ Database initialization complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(init_db())
