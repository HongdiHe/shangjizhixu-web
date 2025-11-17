"""Question schemas for API requests and responses."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from app.models.enums import (
    Grade,
    QuestionSource,
    QuestionStatus,
    QuestionType,
    ReviewStatus,
    Subject,
)


# Base schemas
class QuestionBase(BaseModel):
    """Base question schema with common fields."""

    subject: Subject
    grade: Grade
    question_type: QuestionType
    source: QuestionSource = QuestionSource.HLE
    tags: List[str] = Field(default_factory=list)


class QuestionCreate(QuestionBase):
    """Schema for creating a new question."""

    original_images: List[str] = Field(default_factory=list)


class QuestionUpdate(BaseModel):
    """Schema for updating question metadata."""

    subject: Optional[Subject] = None
    grade: Optional[Grade] = None
    question_type: Optional[QuestionType] = None
    source: Optional[QuestionSource] = None
    tags: Optional[List[str]] = None


# OCR-related schemas
class OCRContentUpdate(BaseModel):
    """Schema for updating OCR content."""

    draft_original_question: Optional[str] = None
    draft_original_answer: Optional[str] = None


class OCRReviewSubmit(BaseModel):
    """Schema for submitting OCR review."""

    original_question: str
    original_answer: str
    review_comment: Optional[str] = None
    review_status: ReviewStatus


# Rewrite-related schemas
class RewritePairUpdate(BaseModel):
    """Schema for updating a single rewrite pair."""

    draft_question: Optional[str] = None
    draft_answer: Optional[str] = None
    edit_comment: Optional[str] = None


class RewriteReviewSubmit(BaseModel):
    """Schema for submitting rewrite review."""

    question: str
    answer: str
    review_comment: Optional[str] = None
    review_status: ReviewStatus


# Assignment schemas
class AssignmentUpdate(BaseModel):
    """Schema for updating question assignments."""

    ocr_editor_id: Optional[int] = None
    ocr_reviewer_id: Optional[int] = None
    rewrite_editor_id: Optional[int] = None
    rewrite_reviewer_id: Optional[int] = None


# Response schemas
class QuestionInDB(QuestionBase):
    """Question schema with all database fields."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    original_images: List[str]

    # OCR fields
    ocr_raw_question: Optional[str] = None  # MinerU原始OCR结果（只读）
    ocr_raw_answer: Optional[str] = None    # MinerU原始OCR答案（只读）
    draft_original_question: Optional[str] = None  # 可编辑的题目草稿
    draft_original_answer: Optional[str] = None    # 可编辑的答案草稿
    original_question: Optional[str] = None
    original_answer: Optional[str] = None
    original_review_comment: Optional[str] = None
    original_review_status: ReviewStatus

    # Rewrite fields
    rewrite_prompt_version: int
    draft_rewrite_question_1: Optional[str] = None
    draft_rewrite_answer_1: Optional[str] = None
    draft_rewrite_question_2: Optional[str] = None
    draft_rewrite_answer_2: Optional[str] = None
    draft_rewrite_question_3: Optional[str] = None
    draft_rewrite_answer_3: Optional[str] = None
    draft_rewrite_question_4: Optional[str] = None
    draft_rewrite_answer_4: Optional[str] = None
    draft_rewrite_question_5: Optional[str] = None
    draft_rewrite_answer_5: Optional[str] = None

    rewrite_question_1: Optional[str] = None
    rewrite_answer_1: Optional[str] = None
    rewrite_question_2: Optional[str] = None
    rewrite_answer_2: Optional[str] = None
    rewrite_question_3: Optional[str] = None
    rewrite_answer_3: Optional[str] = None
    rewrite_question_4: Optional[str] = None
    rewrite_answer_4: Optional[str] = None
    rewrite_question_5: Optional[str] = None
    rewrite_answer_5: Optional[str] = None

    rewrite_edit_comment_1: Optional[str] = None
    rewrite_edit_comment_2: Optional[str] = None
    rewrite_edit_comment_3: Optional[str] = None
    rewrite_edit_comment_4: Optional[str] = None
    rewrite_edit_comment_5: Optional[str] = None

    rewrite_review_comment_1: Optional[str] = None
    rewrite_review_comment_2: Optional[str] = None
    rewrite_review_comment_3: Optional[str] = None
    rewrite_review_comment_4: Optional[str] = None
    rewrite_review_comment_5: Optional[str] = None

    rewrite_review_status_1: ReviewStatus
    rewrite_review_status_2: ReviewStatus
    rewrite_review_status_3: ReviewStatus
    rewrite_review_status_4: ReviewStatus
    rewrite_review_status_5: ReviewStatus

    # Assignments
    ocr_editor_id: Optional[int] = None
    ocr_reviewer_id: Optional[int] = None
    rewrite_editor_id: Optional[int] = None
    rewrite_reviewer_id: Optional[int] = None

    # Status and progress
    status: QuestionStatus
    ocr_progress: int
    rewrite_progress: int

    # Timestamps
    created_at: datetime
    updated_at: datetime
    ocr_completed_at: Optional[datetime] = None
    rewrite_completed_at: Optional[datetime] = None


class Question(QuestionInDB):
    """Full question response schema."""

    pass


class QuestionSummary(BaseModel):
    """Summary question schema for list views."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    subject: Subject
    grade: Grade
    question_type: QuestionType
    source: QuestionSource
    status: QuestionStatus
    ocr_progress: int
    rewrite_progress: int
    created_at: datetime
    updated_at: datetime


class QuestionListResponse(BaseModel):
    """Paginated question list response."""

    items: List[QuestionSummary]
    total: int
    page: int
    page_size: int
    total_pages: int


# Task-related schemas
class TaskStats(BaseModel):
    """Task statistics schema."""

    total: int = 0
    pending: int = 0
    in_progress: int = 0
    completed: int = 0


class UserTaskSummary(BaseModel):
    """User task summary schema."""

    ocr_editing: TaskStats
    ocr_reviewing: TaskStats
    rewrite_editing: TaskStats
    rewrite_reviewing: TaskStats


class DashboardStats(BaseModel):
    """Dashboard statistics schema."""

    total_questions: int = 0
    completed_questions: int = 0
    in_progress_questions: int = 0
    my_tasks: int = 0
