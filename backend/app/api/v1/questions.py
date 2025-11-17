"""Question management API endpoints."""
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import (
    get_admin,
    get_current_user,
    get_ocr_editor,
    get_ocr_reviewer,
    get_rewrite_editor,
    get_rewrite_reviewer,
)
from app.models.user import User
from app.models.enums import QuestionStatus, ReviewStatus
from app.schemas.question import (
    AssignmentUpdate,
    DashboardStats,
    OCRContentUpdate,
    OCRReviewSubmit,
    Question as QuestionSchema,
    QuestionCreate,
    QuestionListResponse,
    QuestionSummary,
    QuestionUpdate,
    RewritePairUpdate,
    RewriteReviewSubmit,
)
from app.schemas.common import APIResponse
from app.services.question_service import QuestionService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=APIResponse[QuestionSchema])
async def create_question(
    question_in: QuestionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> APIResponse[QuestionSchema]:
    """
    Create a new question.

    Args:
        question_in: Question creation data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Created question
    """
    question = await QuestionService.create(db, question_in)

    # Auto-assign to first OCR editor
    from app.services.user_service import UserService
    from app.models.enums import UserRole
    ocr_editors = await UserService.get_users_by_role(db, UserRole.OCR_EDITOR)
    if ocr_editors:
        question.ocr_editor_id = ocr_editors[0].id
        await db.commit()
        await db.refresh(question)

    # Trigger MinerU OCR task asynchronously
    from app.tasks.ocr_tasks import process_mineru_ocr
    process_mineru_ocr.delay(question.id)

    return APIResponse(
        success=True,
        message="Question created successfully",
        data=QuestionSchema.model_validate(question)
    )


@router.get("/{question_id}", response_model=APIResponse[QuestionSchema])
async def get_question(
    question_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> APIResponse[QuestionSchema]:
    """
    Get question by ID.

    Args:
        question_id: Question ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Question details
    """
    question = await QuestionService.get_by_id(db, question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )

    return APIResponse(
        success=True,
        data=QuestionSchema.model_validate(question)
    )


@router.get("/", response_model=APIResponse[QuestionListResponse])
async def list_questions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: QuestionStatus | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> APIResponse[QuestionListResponse]:
    """
    List questions with pagination.

    Args:
        page: Page number
        page_size: Items per page
        status_filter: Filter by status
        db: Database session
        current_user: Current authenticated user

    Returns:
        Paginated question list
    """
    skip = (page - 1) * page_size
    questions, total = await QuestionService.get_paginated(
        db,
        skip=skip,
        limit=page_size,
        status=status_filter
    )

    total_pages = (total + page_size - 1) // page_size

    return APIResponse(
        success=True,
        data=QuestionListResponse(
            items=[QuestionSummary.model_validate(q) for q in questions],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    )


@router.put("/{question_id}", response_model=APIResponse[QuestionSchema])
async def update_question(
    question_id: int,
    question_in: QuestionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin)
) -> APIResponse[QuestionSchema]:
    """
    Update question metadata (admin only).

    Args:
        question_id: Question ID
        question_in: Update data
        db: Database session
        current_user: Current admin user

    Returns:
        Updated question
    """
    question = await QuestionService.get_by_id(db, question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )

    updated_question = await QuestionService.update(db, question, question_in)

    return APIResponse(
        success=True,
        message="Question updated successfully",
        data=QuestionSchema.model_validate(updated_question)
    )


@router.delete("/{question_id}", response_model=APIResponse[None])
async def delete_question(
    question_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin)
) -> APIResponse[None]:
    """
    Delete a question (admin only).

    Args:
        question_id: Question ID
        db: Database session
        current_user: Current admin user

    Returns:
        Success message
    """
    question = await QuestionService.get_by_id(db, question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )

    await QuestionService.delete(db, question)

    return APIResponse(
        success=True,
        message="Question deleted successfully"
    )


# ==================== OCR Endpoints ====================

@router.post("/{question_id}/ocr/trigger", response_model=APIResponse[dict])
async def trigger_ocr(
    question_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_ocr_editor)
) -> APIResponse[dict]:
    """
    Trigger or re-trigger OCR processing for a question.

    Args:
        question_id: Question ID
        db: Database session
        current_user: Current OCR editor

    Returns:
        Task status
    """
    question = await QuestionService.get_by_id(db, question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )

    # Check assignment
    if question.ocr_editor_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not assigned to this question"
        )

    # Check if images exist
    if not question.original_images:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No images to process"
        )

    # Trigger OCR task
    from app.tasks.ocr_tasks import process_mineru_ocr
    task = process_mineru_ocr.delay(question.id)

    return APIResponse(
        success=True,
        message="OCR task triggered successfully",
        data={
            "task_id": task.id,
            "question_id": question_id
        }
    )


@router.put("/{question_id}/ocr/draft", response_model=APIResponse[QuestionSchema])
async def update_ocr_draft(
    question_id: int,
    content: OCRContentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_ocr_editor)
) -> APIResponse[QuestionSchema]:
    """
    Update OCR draft content.

    Args:
        question_id: Question ID
        content: OCR content update
        db: Database session
        current_user: Current OCR editor

    Returns:
        Updated question
    """
    question = await QuestionService.get_by_id(db, question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )

    # Check assignment
    if question.ocr_editor_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not assigned to this question"
        )

    updated_question = await QuestionService.update_ocr_draft(
        db,
        question,
        draft_question=content.draft_original_question,
        draft_answer=content.draft_original_answer
    )

    return APIResponse(
        success=True,
        message="OCR draft updated successfully",
        data=QuestionSchema.model_validate(updated_question)
    )


@router.post("/{question_id}/ocr/submit", response_model=APIResponse[QuestionSchema])
async def submit_ocr_edit(
    question_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_ocr_editor)
) -> APIResponse[QuestionSchema]:
    """
    Submit OCR edit for review.

    Args:
        question_id: Question ID
        db: Database session
        current_user: Current OCR editor

    Returns:
        Updated question
    """
    question = await QuestionService.get_by_id(db, question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )

    # Check assignment
    if question.ocr_editor_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not assigned to this question"
        )

    # Validate draft content exists
    if not question.draft_original_question or not question.draft_original_answer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Draft content must be completed before submission"
        )

    updated_question = await QuestionService.submit_ocr_edit(db, question)

    return APIResponse(
        success=True,
        message="OCR edit submitted for review",
        data=QuestionSchema.model_validate(updated_question)
    )


@router.post("/{question_id}/ocr/review", response_model=APIResponse[QuestionSchema])
async def submit_ocr_review(
    question_id: int,
    review: OCRReviewSubmit,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_ocr_reviewer)
) -> APIResponse[QuestionSchema]:
    """
    Submit OCR review.

    Args:
        question_id: Question ID
        review: Review submission data
        db: Database session
        current_user: Current OCR reviewer

    Returns:
        Updated question
    """
    question = await QuestionService.get_by_id(db, question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )

    # Check assignment
    if question.ocr_reviewer_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not assigned to this question"
        )

    # Check status
    if question.status != QuestionStatus.OCR_REVIEWING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question is not ready for OCR review"
        )

    updated_question = await QuestionService.submit_ocr_review(
        db,
        question,
        review_status=review.review_status,
        review_comment=review.review_comment,
        final_question=review.original_question,
        final_answer=review.original_answer
    )

    # If approved, trigger LLM rewrite task
    if review.review_status == ReviewStatus.APPROVED:
        from app.tasks.llm_tasks import generate_rewrites
        generate_rewrites.delay(question.id)
        logger.info(f"Triggered LLM rewrite task for question {question.id}")

    return APIResponse(
        success=True,
        message="OCR review submitted successfully",
        data=QuestionSchema.model_validate(updated_question)
    )


# ==================== Rewrite Endpoints ====================

@router.put("/{question_id}/rewrite/{index}", response_model=APIResponse[QuestionSchema])
async def update_rewrite_draft(
    question_id: int,
    index: int,
    content: RewritePairUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_rewrite_editor)
) -> APIResponse[QuestionSchema]:
    """
    Update rewrite draft for a specific index (1-5).

    Args:
        question_id: Question ID
        index: Rewrite index (1-5)
        content: Rewrite content update
        db: Database session
        current_user: Current rewrite editor

    Returns:
        Updated question
    """
    if index < 1 or index > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Index must be between 1 and 5"
        )

    question = await QuestionService.get_by_id(db, question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )

    # Check assignment
    if question.rewrite_editor_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not assigned to this question"
        )

    updated_question = await QuestionService.update_rewrite_draft(
        db,
        question,
        index=index,
        draft_question=content.draft_question,
        draft_answer=content.draft_answer,
        edit_comment=content.edit_comment
    )

    return APIResponse(
        success=True,
        message=f"Rewrite draft {index} updated successfully",
        data=QuestionSchema.model_validate(updated_question)
    )


@router.post("/{question_id}/rewrite/{index}/submit", response_model=APIResponse[QuestionSchema])
async def submit_rewrite_edit(
    question_id: int,
    index: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_rewrite_editor)
) -> APIResponse[QuestionSchema]:
    """
    Submit rewrite edit for review.

    Args:
        question_id: Question ID
        index: Rewrite index (1-5)
        db: Database session
        current_user: Current rewrite editor

    Returns:
        Updated question
    """
    if index < 1 or index > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Index must be between 1 and 5"
        )

    question = await QuestionService.get_by_id(db, question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )

    # Check assignment
    if question.rewrite_editor_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not assigned to this question"
        )

    # Validate draft content exists
    draft_q = getattr(question, f"draft_rewrite_question_{index}")
    draft_a = getattr(question, f"draft_rewrite_answer_{index}")

    if not draft_q or not draft_a:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Rewrite draft {index} must be completed before submission"
        )

    updated_question = await QuestionService.submit_rewrite_edit(db, question, index)

    return APIResponse(
        success=True,
        message=f"Rewrite {index} submitted for review",
        data=QuestionSchema.model_validate(updated_question)
    )


@router.post("/{question_id}/rewrite/submit-all", response_model=APIResponse[QuestionSchema])
async def submit_all_rewrite_edits(
    question_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_rewrite_editor)
) -> APIResponse[QuestionSchema]:
    """
    Submit all rewrite edits (all 5 versions) for review.

    Args:
        question_id: Question ID
        db: Database session
        current_user: Current rewrite editor

    Returns:
        Updated question
    """
    question = await QuestionService.get_by_id(db, question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )

    # Check assignment
    if question.rewrite_editor_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not assigned to this question"
        )

    # Validate that at least one version has content
    has_content = False
    for index in range(1, 6):
        draft_q = getattr(question, f"draft_rewrite_question_{index}")
        draft_a = getattr(question, f"draft_rewrite_answer_{index}")
        if draft_q and draft_a:
            has_content = True
            break

    if not has_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one rewrite version must be completed before submission"
        )

    updated_question = await QuestionService.submit_all_rewrite_edits(db, question)

    return APIResponse(
        success=True,
        message="All rewrite versions submitted for review",
        data=QuestionSchema.model_validate(updated_question)
    )


@router.post("/{question_id}/rewrite/{index}/review", response_model=APIResponse[QuestionSchema])
async def submit_rewrite_review(
    question_id: int,
    index: int,
    review: RewriteReviewSubmit,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_rewrite_reviewer)
) -> APIResponse[QuestionSchema]:
    """
    Submit rewrite review for a specific index.

    Args:
        question_id: Question ID
        index: Rewrite index (1-5)
        review: Review submission data
        db: Database session
        current_user: Current rewrite reviewer

    Returns:
        Updated question
    """
    if index < 1 or index > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Index must be between 1 and 5"
        )

    question = await QuestionService.get_by_id(db, question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )

    # Check assignment
    if question.rewrite_reviewer_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not assigned to this question"
        )

    updated_question = await QuestionService.submit_rewrite_review(
        db,
        question,
        index=index,
        review_status=review.review_status,
        review_comment=review.review_comment,
        final_question=review.question,
        final_answer=review.answer
    )

    return APIResponse(
        success=True,
        message=f"Rewrite {index} review submitted successfully",
        data=QuestionSchema.model_validate(updated_question)
    )


@router.post("/{question_id}/rewrite/{index}/regenerate", response_model=APIResponse[dict])
async def regenerate_rewrite(
    question_id: int,
    index: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_rewrite_editor)
) -> APIResponse[dict]:
    """
    Regenerate a single rewrite version using LLM.

    Args:
        question_id: Question ID
        index: Rewrite index (1-5)
        db: Database session
        current_user: Current rewrite editor user

    Returns:
        Task info
    """
    question = await QuestionService.get_by_id(db, question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )

    # Validate index
    if index < 1 or index > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Index must be between 1 and 5"
        )

    # Check question status - allow regeneration during editing or reviewing
    if question.status not in [
        QuestionStatus.REWRITE_EDITING,
        QuestionStatus.REWRITE_REVIEWING
    ]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot regenerate rewrite in status: {question.status}"
        )

    # Trigger regeneration task
    from app.tasks.llm_tasks import regenerate_single_rewrite
    task = regenerate_single_rewrite.delay(question_id, index)

    logger.info(f"Triggered rewrite regeneration for question {question_id}, index {index}, task_id: {task.id}")

    return APIResponse(
        success=True,
        message=f"Rewrite {index} regeneration started",
        data={"task_id": task.id}
    )


# ==================== Assignment Endpoints ====================

@router.put("/{question_id}/assign", response_model=APIResponse[QuestionSchema])
async def assign_question(
    question_id: int,
    assignment: AssignmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin)
) -> APIResponse[QuestionSchema]:
    """
    Assign users to question (admin only).

    Args:
        question_id: Question ID
        assignment: Assignment data
        db: Database session
        current_user: Current admin user

    Returns:
        Updated question
    """
    question = await QuestionService.get_by_id(db, question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )

    updated_question = await QuestionService.assign_users(
        db,
        question,
        ocr_editor_id=assignment.ocr_editor_id,
        ocr_reviewer_id=assignment.ocr_reviewer_id,
        rewrite_editor_id=assignment.rewrite_editor_id,
        rewrite_reviewer_id=assignment.rewrite_reviewer_id
    )

    return APIResponse(
        success=True,
        message="Question assigned successfully",
        data=QuestionSchema.model_validate(updated_question)
    )


# ==================== My Tasks Endpoints ====================

@router.get("/my/tasks", response_model=APIResponse[QuestionListResponse])
async def get_my_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> APIResponse[QuestionListResponse]:
    """
    Get tasks assigned to current user.

    Args:
        page: Page number
        page_size: Items per page
        db: Database session
        current_user: Current authenticated user

    Returns:
        Paginated task list
    """
    skip = (page - 1) * page_size
    questions, total = await QuestionService.get_paginated(
        db,
        skip=skip,
        limit=page_size,
        assigned_to=current_user.id
    )

    total_pages = (total + page_size - 1) // page_size

    return APIResponse(
        success=True,
        data=QuestionListResponse(
            items=[QuestionSummary.model_validate(q) for q in questions],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    )


# ==================== Dashboard Endpoints ====================

@router.get("/stats/dashboard", response_model=APIResponse[DashboardStats])
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> APIResponse[DashboardStats]:
    """
    Get dashboard statistics.

    Args:
        db: Database session
        current_user: Current authenticated user

    Returns:
        Dashboard statistics
    """
    stats = await QuestionService.get_dashboard_stats(db, user_id=current_user.id)

    return APIResponse(
        success=True,
        data=DashboardStats(**stats)
    )
