"""Question service for business logic."""
from datetime import datetime
from typing import Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.question import Question
from app.models.enums import QuestionStatus, ReviewStatus
from app.schemas.question import QuestionCreate, QuestionUpdate
from app.utils.markdown_converter import markdown_to_required_format


class QuestionService:
    """Question service for managing questions."""

    @staticmethod
    async def get_by_id(db: AsyncSession, question_id: int) -> Optional[Question]:
        """
        Get question by ID.

        Args:
            db: Database session
            question_id: Question ID

        Returns:
            Question or None
        """
        result = await db.execute(
            select(Question).where(Question.id == question_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, question_in: QuestionCreate) -> Question:
        """
        Create a new question.

        Args:
            db: Database session
            question_in: Question creation data

        Returns:
            Created question
        """
        question = Question(
            subject=question_in.subject,
            grade=question_in.grade,
            question_type=question_in.question_type,
            source=question_in.source,
            tags=question_in.tags,
            original_images=question_in.original_images,
            status=QuestionStatus.NEW,
            ocr_progress=0,
            rewrite_progress=0,
        )
        db.add(question)
        await db.commit()
        await db.refresh(question)
        return question

    @staticmethod
    async def update(
        db: AsyncSession,
        question: Question,
        question_in: QuestionUpdate
    ) -> Question:
        """
        Update question metadata.

        Args:
            db: Database session
            question: Question to update
            question_in: Update data

        Returns:
            Updated question
        """
        update_data = question_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(question, field, value)

        question.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(question)
        return question

    @staticmethod
    async def save_ocr_result(
        db: AsyncSession,
        question: Question,
        ocr_question: str,
        ocr_answer: str
    ) -> Question:
        """
        Save MinerU OCR result to both raw (read-only) and draft (editable) fields.

        Args:
            db: Database session
            question: Question to update
            ocr_question: OCR question markdown from MinerU
            ocr_answer: OCR answer markdown from MinerU

        Returns:
            Updated question
        """
        # Save to raw fields (永不修改，仅供参考)
        question.ocr_raw_question = ocr_question
        question.ocr_raw_answer = ocr_answer

        # Save to draft fields (编辑员可修改)
        question.draft_original_question = ocr_question
        question.draft_original_answer = ocr_answer

        # Update status if needed
        if question.status == QuestionStatus.NEW:
            question.status = QuestionStatus.OCR_EDITING

        question.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(question)
        return question

    async def update_ocr_draft(
        db: AsyncSession,
        question: Question,
        draft_question: Optional[str] = None,
        draft_answer: Optional[str] = None
    ) -> Question:
        """
        Update OCR draft content (only draft fields, not raw).

        Used when OCR editor manually edits the draft.
        Raw OCR fields remain unchanged for reference.

        Args:
            db: Database session
            question: Question to update
            draft_question: Draft question markdown (edited by user)
            draft_answer: Draft answer markdown (edited by user)

        Returns:
            Updated question
        """
        if draft_question is not None:
            question.draft_original_question = draft_question

        if draft_answer is not None:
            question.draft_original_answer = draft_answer

        # Update status if needed
        if question.status == QuestionStatus.NEW:
            question.status = QuestionStatus.OCR_EDITING

        question.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(question)
        return question

    @staticmethod
    async def submit_ocr_edit(
        db: AsyncSession,
        question: Question
    ) -> Question:
        """
        Submit OCR edit - convert markdown to required format.

        Args:
            db: Database session
            question: Question to submit

        Returns:
            Updated question
        """
        # Convert markdown to required format
        if question.draft_original_question:
            question.original_question = markdown_to_required_format(
                question.draft_original_question
            )

        if question.draft_original_answer:
            question.original_answer = markdown_to_required_format(
                question.draft_original_answer
            )

        # Update status and progress
        question.status = QuestionStatus.OCR_REVIEWING
        question.ocr_progress = 50  # 50% after edit submission
        question.updated_at = datetime.utcnow()

        # Auto-assign to first OCR reviewer
        from app.services.user_service import UserService
        from app.models.enums import UserRole
        ocr_reviewers = await UserService.get_users_by_role(db, UserRole.OCR_REVIEWER)
        if ocr_reviewers and not question.ocr_reviewer_id:
            question.ocr_reviewer_id = ocr_reviewers[0].id

        await db.commit()
        await db.refresh(question)
        return question

    @staticmethod
    async def submit_ocr_review(
        db: AsyncSession,
        question: Question,
        review_status: ReviewStatus,
        review_comment: Optional[str] = None,
        final_question: Optional[str] = None,
        final_answer: Optional[str] = None
    ) -> Question:
        """
        Submit OCR review.

        Args:
            db: Database session
            question: Question to review
            review_status: Review status
            review_comment: Review comment
            final_question: Final question text (if modified)
            final_answer: Final answer text (if modified)

        Returns:
            Updated question
        """
        question.original_review_status = review_status
        question.original_review_comment = review_comment

        # Update final text if provided
        if final_question:
            question.original_question = final_question
        if final_answer:
            question.original_answer = final_answer

        if review_status == ReviewStatus.APPROVED:
            question.status = QuestionStatus.OCR_APPROVED
            question.ocr_progress = 100
            question.ocr_completed_at = datetime.utcnow()

            # Auto-assign to first rewrite editor
            from app.services.user_service import UserService
            from app.models.enums import UserRole
            rewrite_editors = await UserService.get_users_by_role(db, UserRole.REWRITE_EDITOR)
            if rewrite_editors and not question.rewrite_editor_id:
                question.rewrite_editor_id = rewrite_editors[0].id
                # Update status to rewrite editing
                question.status = QuestionStatus.REWRITE_EDITING
        elif review_status == ReviewStatus.CHANGES_REQUESTED:
            question.status = QuestionStatus.OCR_EDITING
            # Progress stays at 50%

        question.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(question)
        return question

    @staticmethod
    async def update_rewrite_draft(
        db: AsyncSession,
        question: Question,
        index: int,
        draft_question: Optional[str] = None,
        draft_answer: Optional[str] = None,
        edit_comment: Optional[str] = None
    ) -> Question:
        """
        Update rewrite draft for a specific index (1-5).

        Args:
            db: Database session
            question: Question to update
            index: Rewrite index (1-5)
            draft_question: Draft question markdown
            draft_answer: Draft answer markdown
            edit_comment: Editor comment

        Returns:
            Updated question
        """
        if index < 1 or index > 5:
            raise ValueError("Index must be between 1 and 5")

        if draft_question is not None:
            setattr(question, f"draft_rewrite_question_{index}", draft_question)

        if draft_answer is not None:
            setattr(question, f"draft_rewrite_answer_{index}", draft_answer)

        if edit_comment is not None:
            setattr(question, f"rewrite_edit_comment_{index}", edit_comment)

        # Update status if needed
        if question.status == QuestionStatus.REWRITE_GENERATING:
            question.status = QuestionStatus.REWRITE_EDITING

        question.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(question)
        return question

    @staticmethod
    async def submit_rewrite_edit(
        db: AsyncSession,
        question: Question,
        index: int
    ) -> Question:
        """
        Submit rewrite edit - convert markdown to required format.

        Args:
            db: Database session
            question: Question to submit
            index: Rewrite index (1-5)

        Returns:
            Updated question
        """
        if index < 1 or index > 5:
            raise ValueError("Index must be between 1 and 5")

        # Convert markdown to required format
        draft_q = getattr(question, f"draft_rewrite_question_{index}")
        draft_a = getattr(question, f"draft_rewrite_answer_{index}")

        if draft_q:
            setattr(question, f"rewrite_question_{index}",
                   markdown_to_required_format(draft_q))

        if draft_a:
            setattr(question, f"rewrite_answer_{index}",
                   markdown_to_required_format(draft_a))

        # Update progress - each pair is 20%
        completed_pairs = QuestionService._count_completed_rewrite_pairs(question)
        question.rewrite_progress = min(completed_pairs * 20, 100)

        # Auto-assign to first rewrite reviewer
        from app.services.user_service import UserService
        from app.models.enums import UserRole
        rewrite_reviewers = await UserService.get_users_by_role(db, UserRole.REWRITE_REVIEWER)
        if rewrite_reviewers and not question.rewrite_reviewer_id:
            question.rewrite_reviewer_id = rewrite_reviewers[0].id
            # Update status to rewrite reviewing
            question.status = QuestionStatus.REWRITE_REVIEWING

        question.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(question)
        return question

    @staticmethod
    async def submit_all_rewrite_edits(
        db: AsyncSession,
        question: Question
    ) -> Question:
        """
        Submit all rewrite edits (all 5 versions) - convert markdown to required format.

        Args:
            db: Database session
            question: Question to submit

        Returns:
            Updated question
        """
        # Convert markdown to required format for all 5 versions
        for index in range(1, 6):
            draft_q = getattr(question, f"draft_rewrite_question_{index}")
            draft_a = getattr(question, f"draft_rewrite_answer_{index}")

            if draft_q:
                setattr(question, f"rewrite_question_{index}",
                       markdown_to_required_format(draft_q))

            if draft_a:
                setattr(question, f"rewrite_answer_{index}",
                       markdown_to_required_format(draft_a))

            # Reset review status to PENDING for re-review (重新提交时重置审核状态为待审核)
            from app.models.enums import ReviewStatus
            setattr(question, f"rewrite_review_status_{index}", ReviewStatus.PENDING)
            setattr(question, f"rewrite_review_comment_{index}", None)

        # Update progress - all 5 pairs = 100%
        completed_pairs = QuestionService._count_completed_rewrite_pairs(question)
        question.rewrite_progress = min(completed_pairs * 20, 100)

        # Auto-assign to first rewrite reviewer if not assigned
        from app.services.user_service import UserService
        from app.models.enums import UserRole
        rewrite_reviewers = await UserService.get_users_by_role(db, UserRole.REWRITE_REVIEWER)
        if rewrite_reviewers and not question.rewrite_reviewer_id:
            question.rewrite_reviewer_id = rewrite_reviewers[0].id

        # Always update status to rewrite reviewing when submitting
        question.status = QuestionStatus.REWRITE_REVIEWING

        question.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(question)
        return question

    @staticmethod
    async def submit_rewrite_review(
        db: AsyncSession,
        question: Question,
        index: int,
        review_status: ReviewStatus,
        review_comment: Optional[str] = None,
        final_question: Optional[str] = None,
        final_answer: Optional[str] = None
    ) -> Question:
        """
        Submit rewrite review for a specific index.

        Args:
            db: Database session
            question: Question to review
            index: Rewrite index (1-5)
            review_status: Review status
            review_comment: Review comment
            final_question: Final question text (if modified)
            final_answer: Final answer text (if modified)

        Returns:
            Updated question
        """
        if index < 1 or index > 5:
            raise ValueError("Index must be between 1 and 5")

        # Update review status and comment
        setattr(question, f"rewrite_review_status_{index}", review_status)
        if review_comment:
            setattr(question, f"rewrite_review_comment_{index}", review_comment)

        # Update final text if provided
        if final_question:
            setattr(question, f"rewrite_question_{index}", final_question)
        if final_answer:
            setattr(question, f"rewrite_answer_{index}", final_answer)

        # Determine question status based on review results
        # Check if any version was rejected (changes requested)
        has_changes_requested = False
        all_approved = True

        for i in range(1, 6):
            status = getattr(question, f"rewrite_review_status_{i}", None)
            if status == ReviewStatus.CHANGES_REQUESTED:
                has_changes_requested = True
                all_approved = False
                break
            elif status != ReviewStatus.APPROVED:
                all_approved = False

        # Update question status accordingly
        if has_changes_requested:
            # If any version needs changes, send back to editing
            question.status = QuestionStatus.REWRITE_EDITING
        elif all_approved:
            # If all versions approved, mark as done
            question.status = QuestionStatus.DONE
            question.rewrite_progress = 100
            question.rewrite_completed_at = datetime.utcnow()
        else:
            # Otherwise, keep in reviewing status
            question.status = QuestionStatus.REWRITE_REVIEWING

        question.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(question)
        return question

    @staticmethod
    def _count_completed_rewrite_pairs(question: Question) -> int:
        """Count how many rewrite pairs have been completed."""
        count = 0
        for i in range(1, 6):
            q = getattr(question, f"rewrite_question_{i}")
            a = getattr(question, f"rewrite_answer_{i}")
            if q and a:
                count += 1
        return count

    @staticmethod
    async def assign_users(
        db: AsyncSession,
        question: Question,
        ocr_editor_id: Optional[int] = None,
        ocr_reviewer_id: Optional[int] = None,
        rewrite_editor_id: Optional[int] = None,
        rewrite_reviewer_id: Optional[int] = None
    ) -> Question:
        """
        Assign users to question.

        Args:
            db: Database session
            question: Question to assign
            ocr_editor_id: OCR editor user ID
            ocr_reviewer_id: OCR reviewer user ID
            rewrite_editor_id: Rewrite editor user ID
            rewrite_reviewer_id: Rewrite reviewer user ID

        Returns:
            Updated question
        """
        if ocr_editor_id is not None:
            question.ocr_editor_id = ocr_editor_id
        if ocr_reviewer_id is not None:
            question.ocr_reviewer_id = ocr_reviewer_id
        if rewrite_editor_id is not None:
            question.rewrite_editor_id = rewrite_editor_id
        if rewrite_reviewer_id is not None:
            question.rewrite_reviewer_id = rewrite_reviewer_id

        question.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(question)
        return question

    @staticmethod
    async def get_paginated(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        status: Optional[QuestionStatus] = None,
        assigned_to: Optional[int] = None
    ) -> tuple[list[Question], int]:
        """
        Get paginated questions.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records
            status: Filter by status
            assigned_to: Filter by assigned user ID

        Returns:
            Tuple of (questions list, total count)
        """
        query = select(Question)

        # Apply filters
        if status:
            query = query.where(Question.status == status)

        if assigned_to:
            from sqlalchemy import or_
            query = query.where(
                or_(
                    Question.ocr_editor_id == assigned_to,
                    Question.ocr_reviewer_id == assigned_to,
                    Question.rewrite_editor_id == assigned_to,
                    Question.rewrite_reviewer_id == assigned_to
                )
            )

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_query)).scalar_one()

        # Get paginated results
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        questions = list(result.scalars().all())

        return questions, total

    @staticmethod
    async def get_dashboard_stats(
        db: AsyncSession,
        user_id: Optional[int] = None
    ) -> dict:
        """
        Get dashboard statistics.

        Args:
            db: Database session
            user_id: Optional user ID for personalized stats

        Returns:
            Dashboard statistics dictionary
        """
        # Total questions
        total_result = await db.execute(select(func.count(Question.id)))
        total_questions = total_result.scalar_one()

        # Completed questions (status = DONE)
        completed_result = await db.execute(
            select(func.count(Question.id)).where(
                Question.status == QuestionStatus.DONE
            )
        )
        completed_questions = completed_result.scalar_one()

        # In progress questions (not NEW, not DONE, not ARCHIVED)
        in_progress_result = await db.execute(
            select(func.count(Question.id)).where(
                Question.status.notin_([QuestionStatus.NEW, QuestionStatus.DONE, QuestionStatus.ARCHIVED])
            )
        )
        in_progress_questions = in_progress_result.scalar_one()

        # My tasks (if user_id provided)
        my_tasks = 0
        if user_id:
            from sqlalchemy import or_
            my_tasks_result = await db.execute(
                select(func.count(Question.id)).where(
                    or_(
                        Question.ocr_editor_id == user_id,
                        Question.ocr_reviewer_id == user_id,
                        Question.rewrite_editor_id == user_id,
                        Question.rewrite_reviewer_id == user_id
                    )
                )
            )
            my_tasks = my_tasks_result.scalar_one()

        return {
            "total_questions": total_questions,
            "completed_questions": completed_questions,
            "in_progress_questions": in_progress_questions,
            "my_tasks": my_tasks
        }

    @staticmethod
    async def delete(db: AsyncSession, question: Question) -> None:
        """
        Delete a question (admin only).

        Args:
            db: Database session
            question: Question to delete
        """
        await db.delete(question)
        await db.commit()
