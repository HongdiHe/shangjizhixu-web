"""Question model."""
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.enums import (
    Grade,
    QuestionSource,
    QuestionStatus,
    QuestionType,
    ReviewStatus,
    Subject,
)

if TYPE_CHECKING:
    from app.models.user import User


class Question(Base):
    """Question model representing the entire question lifecycle."""

    __tablename__ = "questions"

    # Primary Key
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # ==================== 元信息 ====================
    subject: Mapped[Subject] = mapped_column(
        Enum(Subject, native_enum=False),
        nullable=False
    )
    grade: Mapped[Grade] = mapped_column(
        Enum(Grade, native_enum=False),
        nullable=False
    )
    question_type: Mapped[QuestionType] = mapped_column(
        Enum(QuestionType, native_enum=False),
        nullable=False
    )
    source: Mapped[QuestionSource] = mapped_column(
        Enum(QuestionSource, native_enum=False),
        nullable=False,
        default=QuestionSource.HLE
    )
    tags: Mapped[list[str]] = mapped_column(JSON, nullable=True, default=list)

    # ==================== 原题图片 ====================
    original_images: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=True,
        default=list,
        comment="S3/MinIO URLs of original question images"
    )

    # ==================== OCR 阶段字段 ====================
    # 待处理原题（Markdown格式）
    draft_original_question: Mapped[str] = mapped_column(
        Text,
        nullable=True,
        comment="Draft original question in Markdown from MinerU"
    )
    draft_original_answer: Mapped[str] = mapped_column(
        Text,
        nullable=True,
        comment="Draft original answer in Markdown from MinerU"
    )

    # 原题（单行要求格式）
    original_question: Mapped[str] = mapped_column(
        Text,
        nullable=True,
        comment="Original question in required format (single line)"
    )
    original_answer: Mapped[str] = mapped_column(
        Text,
        nullable=True,
        comment="Original answer in required format (single line)"
    )

    # 原题审核
    original_review_comment: Mapped[str] = mapped_column(
        Text,
        nullable=True,
        comment="Review comment from OCR reviewer"
    )
    original_review_status: Mapped[ReviewStatus] = mapped_column(
        Enum(ReviewStatus, native_enum=False),
        nullable=False,
        default=ReviewStatus.PENDING
    )

    # ==================== 改写阶段字段 ====================
    rewrite_prompt_version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=3,
        comment="Version of the rewrite prompt used"
    )

    # 待处理改写题目和答案（Markdown格式，共5组）
    draft_rewrite_question_1: Mapped[str] = mapped_column(Text, nullable=True)
    draft_rewrite_answer_1: Mapped[str] = mapped_column(Text, nullable=True)
    draft_rewrite_question_2: Mapped[str] = mapped_column(Text, nullable=True)
    draft_rewrite_answer_2: Mapped[str] = mapped_column(Text, nullable=True)
    draft_rewrite_question_3: Mapped[str] = mapped_column(Text, nullable=True)
    draft_rewrite_answer_3: Mapped[str] = mapped_column(Text, nullable=True)
    draft_rewrite_question_4: Mapped[str] = mapped_column(Text, nullable=True)
    draft_rewrite_answer_4: Mapped[str] = mapped_column(Text, nullable=True)
    draft_rewrite_question_5: Mapped[str] = mapped_column(Text, nullable=True)
    draft_rewrite_answer_5: Mapped[str] = mapped_column(Text, nullable=True)

    # 改写题目和答案（单行要求格式，共5组）
    rewrite_question_1: Mapped[str] = mapped_column(Text, nullable=True)
    rewrite_answer_1: Mapped[str] = mapped_column(Text, nullable=True)
    rewrite_question_2: Mapped[str] = mapped_column(Text, nullable=True)
    rewrite_answer_2: Mapped[str] = mapped_column(Text, nullable=True)
    rewrite_question_3: Mapped[str] = mapped_column(Text, nullable=True)
    rewrite_answer_3: Mapped[str] = mapped_column(Text, nullable=True)
    rewrite_question_4: Mapped[str] = mapped_column(Text, nullable=True)
    rewrite_answer_4: Mapped[str] = mapped_column(Text, nullable=True)
    rewrite_question_5: Mapped[str] = mapped_column(Text, nullable=True)
    rewrite_answer_5: Mapped[str] = mapped_column(Text, nullable=True)

    # 改写评价（编辑评价和二次审核评价，共5组）
    rewrite_edit_comment_1: Mapped[str] = mapped_column(Text, nullable=True)
    rewrite_edit_comment_2: Mapped[str] = mapped_column(Text, nullable=True)
    rewrite_edit_comment_3: Mapped[str] = mapped_column(Text, nullable=True)
    rewrite_edit_comment_4: Mapped[str] = mapped_column(Text, nullable=True)
    rewrite_edit_comment_5: Mapped[str] = mapped_column(Text, nullable=True)

    rewrite_review_comment_1: Mapped[str] = mapped_column(Text, nullable=True)
    rewrite_review_comment_2: Mapped[str] = mapped_column(Text, nullable=True)
    rewrite_review_comment_3: Mapped[str] = mapped_column(Text, nullable=True)
    rewrite_review_comment_4: Mapped[str] = mapped_column(Text, nullable=True)
    rewrite_review_comment_5: Mapped[str] = mapped_column(Text, nullable=True)

    # 改写审核状态（5组）
    rewrite_review_status_1: Mapped[ReviewStatus] = mapped_column(
        Enum(ReviewStatus, native_enum=False),
        nullable=False,
        default=ReviewStatus.PENDING
    )
    rewrite_review_status_2: Mapped[ReviewStatus] = mapped_column(
        Enum(ReviewStatus, native_enum=False),
        nullable=False,
        default=ReviewStatus.PENDING
    )
    rewrite_review_status_3: Mapped[ReviewStatus] = mapped_column(
        Enum(ReviewStatus, native_enum=False),
        nullable=False,
        default=ReviewStatus.PENDING
    )
    rewrite_review_status_4: Mapped[ReviewStatus] = mapped_column(
        Enum(ReviewStatus, native_enum=False),
        nullable=False,
        default=ReviewStatus.PENDING
    )
    rewrite_review_status_5: Mapped[ReviewStatus] = mapped_column(
        Enum(ReviewStatus, native_enum=False),
        nullable=False,
        default=ReviewStatus.PENDING
    )

    # ==================== 分配信息 ====================
    ocr_editor_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )
    ocr_reviewer_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )
    rewrite_editor_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )
    rewrite_reviewer_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    # ==================== 状态和进度 ====================
    status: Mapped[QuestionStatus] = mapped_column(
        Enum(QuestionStatus, native_enum=False),
        nullable=False,
        default=QuestionStatus.NEW,
        index=True
    )

    # 进度百分比
    ocr_progress: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="OCR progress percentage (0-100)"
    )
    rewrite_progress: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Rewrite progress percentage (0-100)"
    )

    # ==================== 时间戳 ====================
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
    ocr_completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    rewrite_completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # ==================== Relationships ====================
    ocr_editor: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[ocr_editor_id],
        back_populates="ocr_assigned_questions"
    )
    ocr_reviewer: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[ocr_reviewer_id],
        back_populates="ocr_reviewed_questions"
    )
    rewrite_editor: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[rewrite_editor_id],
        back_populates="rewrite_assigned_questions"
    )
    rewrite_reviewer: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[rewrite_reviewer_id],
        back_populates="rewrite_reviewed_questions"
    )

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<Question(id={self.id}, "
            f"subject={self.subject}, "
            f"status={self.status})>"
        )

    @property
    def is_completed(self) -> bool:
        """Check if question processing is completed."""
        return (
            self.ocr_progress == 100
            and self.rewrite_progress == 100
            and self.status == QuestionStatus.DONE
        )

    def get_rewrite_pair(self, index: int) -> tuple[str | None, str | None]:
        """
        Get rewrite question-answer pair by index (1-5).

        Args:
            index: Rewrite pair index (1-5)

        Returns:
            Tuple of (question, answer) or (None, None) if invalid index
        """
        if index < 1 or index > 5:
            return None, None

        question = getattr(self, f"rewrite_question_{index}", None)
        answer = getattr(self, f"rewrite_answer_{index}", None)
        return question, answer

    def get_draft_rewrite_pair(self, index: int) -> tuple[str | None, str | None]:
        """
        Get draft rewrite question-answer pair by index (1-5).

        Args:
            index: Rewrite pair index (1-5)

        Returns:
            Tuple of (question, answer) or (None, None) if invalid index
        """
        if index < 1 or index > 5:
            return None, None

        question = getattr(self, f"draft_rewrite_question_{index}", None)
        answer = getattr(self, f"draft_rewrite_answer_{index}", None)
        return question, answer
