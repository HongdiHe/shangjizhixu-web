"""User model."""
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import Boolean, DateTime, Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.enums import UserRole

if TYPE_CHECKING:
    from app.models.question import Question


class User(Base):
    """User model for authentication and authorization."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=True)

    # Role
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, native_enum=False),
        nullable=False,
        default=UserRole.OCR_EDITOR
    )

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    last_login: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # Additional info
    bio: Mapped[str] = mapped_column(Text, nullable=True)
    avatar_url: Mapped[str] = mapped_column(String(500), nullable=True)

    # Relationships
    ocr_assigned_questions: Mapped[list["Question"]] = relationship(
        "Question",
        foreign_keys="Question.ocr_editor_id",
        back_populates="ocr_editor",
        lazy="selectin"
    )
    ocr_reviewed_questions: Mapped[list["Question"]] = relationship(
        "Question",
        foreign_keys="Question.ocr_reviewer_id",
        back_populates="ocr_reviewer",
        lazy="selectin"
    )
    rewrite_assigned_questions: Mapped[list["Question"]] = relationship(
        "Question",
        foreign_keys="Question.rewrite_editor_id",
        back_populates="rewrite_editor",
        lazy="selectin"
    )
    rewrite_reviewed_questions: Mapped[list["Question"]] = relationship(
        "Question",
        foreign_keys="Question.rewrite_reviewer_id",
        back_populates="rewrite_reviewer",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<User(id={self.id}, username={self.username}, role={self.role})>"
