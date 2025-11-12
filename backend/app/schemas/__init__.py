"""Pydantic schemas for request/response validation."""
from app.schemas.common import APIResponse, ErrorResponse, PaginationParams
from app.schemas.user import (
    LoginRequest,
    PasswordChange,
    Token,
    TokenPayload,
    User,
    UserCreate,
    UserInDB,
    UserUpdate,
    UserWithStats,
)
from app.schemas.question import (
    AssignmentUpdate,
    OCRContentUpdate,
    OCRReviewSubmit,
    Question,
    QuestionCreate,
    QuestionInDB,
    QuestionListResponse,
    QuestionSummary,
    QuestionUpdate,
    RewritePairUpdate,
    RewriteReviewSubmit,
    TaskStats,
    UserTaskSummary,
)

__all__ = [
    # Common
    "APIResponse",
    "ErrorResponse",
    "PaginationParams",
    # User
    "User",
    "UserCreate",
    "UserUpdate",
    "UserInDB",
    "UserWithStats",
    "Token",
    "TokenPayload",
    "LoginRequest",
    "PasswordChange",
    # Question
    "Question",
    "QuestionCreate",
    "QuestionUpdate",
    "QuestionInDB",
    "QuestionSummary",
    "QuestionListResponse",
    "OCRContentUpdate",
    "OCRReviewSubmit",
    "RewritePairUpdate",
    "RewriteReviewSubmit",
    "AssignmentUpdate",
    "TaskStats",
    "UserTaskSummary",
]
