"""
Quiz API routes
"""
import base64
import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile  # pylint: disable=import-error
from fastapi.responses import JSONResponse  # pylint: disable=import-error
from sqlalchemy.orm import Session  # pylint: disable=import-error

from api.api_schemas import (
    Quiz, QuizCreate, QuizUpdate, QuizResponse, QuizzesResponse,
    QuizStats, QuizStatsResponse, QuizImportData, QuizFilters,
    PaginationParams, Tag
)
from api.dependencies.auth import get_current_user
from api.utils.responses import create_response
from core.db.crud.repository.flashcard_repository import FlashcardRepository
from core.db.database import get_db
from core.services.quiz_service import QuizService

router = APIRouter()

# Maximum image size in bytes (100KB)
MAX_IMAGE_SIZE = 102400


def validate_image_size(base64_image: Optional[str]) -> None:
    """
    Validate that a Base64 encoded image doesn't exceed the maximum size.

    Args:
        base64_image: Base64 encoded image string

    Raises:
        HTTPException: If image exceeds maximum size
    """
    if not base64_image:
        return

    try:
        # Decode Base64 to get actual binary size
        image_data = base64.b64decode(base64_image)
        image_size = len(image_data)

        if image_size > MAX_IMAGE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Image size ({image_size} bytes) exceeds maximum allowed size ({MAX_IMAGE_SIZE} bytes / 100KB)"
            )
    except base64.binascii.Error as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Base64 encoded image data"
        ) from e


def quiz_to_dict(quiz, flashcard_count=None, last_session_at=None):
    """Convert quiz model to dictionary with base64 encoded image."""
    return {
        "id": quiz.id,
        "name": quiz.name,
        "subject": quiz.subject,
        "category": quiz.category,
        "level": quiz.level,
        "description": quiz.description,
        "created_at": quiz.created_at,
        "favourite": quiz.favourite if hasattr(quiz, 'favourite') else False,
        "image": base64.b64encode(quiz.image).decode('utf-8') if quiz.image else None,
        "is_draft": quiz.is_draft if hasattr(quiz, 'is_draft') else True,
        "status": quiz.status if hasattr(quiz, 'status') else 'draft',
        "tag_ids": [tag.id for tag in quiz.tags] if hasattr(quiz, 'tags') else [],
        "flashcard_count": flashcard_count,
        "last_session_at": last_session_at
    }


@router.get("/", response_model=QuizzesResponse)
async def get_quizzes(
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(),
    filters: QuizFilters = Depends(),
    current_user = Depends(get_current_user)
):
    """Get all quizzes with optional filtering and pagination."""
    try:
        from core.db.crud.repository.session_repository import SessionRepository

        quiz_service = QuizService(db)
        session_repo = SessionRepository(db)

        # Get base query filtered by current user
        quizzes_query = quiz_service.get_all_quizzes(user_id=current_user.id)

        # Apply filters
        if filters.subject:
            quizzes_query = [q for q in quizzes_query if q.subject == filters.subject]

        if filters.category:
            quizzes_query = [q for q in quizzes_query if q.category == filters.category]

        if filters.level:
            quizzes_query = [q for q in quizzes_query if q.level == filters.level]

        if filters.name_contains:
            quizzes_query = [q for q in quizzes_query
                           if filters.name_contains.lower() in q.name.lower()]

        if filters.created_after:
            quizzes_query = [q for q in quizzes_query if q.created_at >= filters.created_after]

        if filters.created_before:
            quizzes_query = [q for q in quizzes_query if q.created_at <= filters.created_before]

        # Convert to quiz objects with flashcard count and last session
        quiz_data = []
        for quiz in quizzes_query:
            flashcards = quiz_service.get_quiz_flashcards(quiz.id)

            # Get last session for this quiz
            sessions = session_repo.get_by_quiz_id(quiz.id)
            last_session_at = None
            if sessions:
                # Get the most recent session
                latest_session = max(sessions, key=lambda s: s.started_at)
                last_session_at = latest_session.started_at

            quiz_dict = quiz_to_dict(quiz, flashcard_count=len(flashcards), last_session_at=last_session_at)
            quiz_data.append(Quiz(**quiz_dict))

        # Sort: favourites first, then by last_session_at (most recent first), nulls last
        from datetime import datetime
        quiz_data.sort(key=lambda q: (
            not q.favourite,  # False (favourite) comes before True (not favourite) with ascending sort
            q.last_session_at is None,  # False (has session) comes before True (no session)
            -(q.last_session_at.timestamp() if q.last_session_at else 0)  # Negative for descending order
        ))

        # Apply pagination
        start = (pagination.page - 1) * pagination.limit
        end = start + pagination.limit
        paginated_data = quiz_data[start:end]

        return create_response(
            data=paginated_data,
            message=f"Retrieved {len(paginated_data)} quizzes"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve quizzes: {str(e)}"
        ) from e


@router.get("/subjects", response_model=dict)
async def get_subjects(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all unique subjects with quiz counts."""
    try:
        quiz_service = QuizService(db)
        all_quizzes = quiz_service.get_all_quizzes(user_id=current_user.id)

        subjects = {}
        for quiz in all_quizzes:
            if quiz.subject:
                subjects[quiz.subject] = subjects.get(quiz.subject, 0) + 1

        return {
            "success": True,
            "data": subjects,
            "message": f"Found {len(subjects)} unique subjects"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve subjects: {str(e)}"
        ) from e


@router.get("/categories", response_model=dict)
async def get_categories(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all unique categories with quiz counts."""
    try:
        quiz_service = QuizService(db)
        all_quizzes = quiz_service.get_all_quizzes(user_id=current_user.id)

        categories = {}
        for quiz in all_quizzes:
            if quiz.category:
                categories[quiz.category] = categories.get(quiz.category, 0) + 1

        return {
            "success": True,
            "data": categories,
            "message": f"Found {len(categories)} unique categories"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve categories: {str(e)}"
        ) from e


@router.get("/levels", response_model=dict)
async def get_levels(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all unique levels with quiz counts."""
    try:
        quiz_service = QuizService(db)
        all_quizzes = quiz_service.get_all_quizzes(user_id=current_user.id)

        levels = {}
        for quiz in all_quizzes:
            if quiz.level:
                levels[quiz.level] = levels.get(quiz.level, 0) + 1

        return {
            "success": True,
            "data": levels,
            "message": f"Found {len(levels)} unique levels"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve levels: {str(e)}"
        ) from e


@router.get("/search", response_model=QuizzesResponse)
async def search_quizzes(
    q: str = Query(..., min_length=1, description="Search query"),
    subject: Optional[str] = Query(None, description="Filter by subject"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Search quizzes by name, subject, or description."""
    try:
        quiz_service = QuizService(db)
        all_quizzes = quiz_service.get_all_quizzes(user_id=current_user.id)

        # Filter by search query
        search_results = []
        q_lower = q.lower()

        for quiz in all_quizzes:
            # Check if query matches name, subject, or description
            matches = (
                q_lower in quiz.name.lower() or
                (quiz.subject and q_lower in quiz.subject.lower()) or
                (quiz.description and q_lower in quiz.description.lower())
            )

            # Apply subject filter if specified
            if subject and quiz.subject != subject:
                matches = False

            if matches:
                flashcards = quiz_service.get_quiz_flashcards(quiz.id)
                quiz_dict = quiz_to_dict(quiz, flashcard_count=len(flashcards))
                search_results.append(Quiz(**quiz_dict))

        # Limit results
        search_results = search_results[:limit]

        return create_response(
            data=search_results,
            message=f"Found {len(search_results)} quizzes matching '{q}'"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search quizzes: {str(e)}"
        ) from e


@router.get("/{quiz_id}", response_model=QuizResponse)
async def get_quiz(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)  # pylint: disable=unused-argument
):
    """Get a specific quiz by ID."""
    try:
        quiz_service = QuizService(db)
        quiz = quiz_service.get_quiz_by_id(quiz_id)

        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Quiz with ID {quiz_id} not found"
            )

        # Get flashcard count
        flashcards = quiz_service.get_quiz_flashcards(quiz.id)
        quiz_dict = quiz_to_dict(quiz, flashcard_count=len(flashcards))

        return create_response(
            data=Quiz(**quiz_dict),
            message="Quiz retrieved successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve quiz: {str(e)}"
        ) from e


@router.patch("/{quiz_id}/favourite", response_model=QuizResponse)
async def toggle_quiz_favourite(
    quiz_id: int,
    favourite: bool = Query(..., description="Favourite status"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)  # pylint: disable=unused-argument
):
    """Toggle quiz favourite status."""
    try:
        quiz_service = QuizService(db)
        quiz = quiz_service.get_quiz_by_id(quiz_id)

        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Quiz with ID {quiz_id} not found"
            )

        # Update favourite status
        quiz.favourite = favourite
        db.commit()
        db.refresh(quiz)

        flashcards = quiz_service.get_quiz_flashcards(quiz.id)
        quiz_dict = quiz_to_dict(quiz, flashcard_count=len(flashcards))

        return create_response(
            data=Quiz(**quiz_dict),
            message=f"Quiz {'added to' if favourite else 'removed from'} favourites"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update quiz favourite status: {str(e)}"
        ) from e


@router.post("/", response_model=QuizResponse, status_code=status.HTTP_201_CREATED)
async def create_quiz(
    quiz_data: QuizCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new quiz."""
    try:
        # Validate image size if provided
        validate_image_size(quiz_data.image)

        quiz_service = QuizService(db)
        quiz = quiz_service.create_quiz(
            name=quiz_data.name,
            user_id=current_user.id,
            subject=quiz_data.subject,
            category=quiz_data.category,
            level=quiz_data.level,
            description=quiz_data.description
        )

        # Handle additional fields not supported by quiz_service.create_quiz
        if quiz_data.image:
            quiz.image = base64.b64decode(quiz_data.image)

        if quiz_data.is_draft is not None:
            quiz.is_draft = quiz_data.is_draft

        if quiz_data.status:
            quiz.status = quiz_data.status

        # Handle tags
        if quiz_data.tag_ids:
            from core.db.models import Tag as TagModel
            tags = db.query(TagModel).filter(TagModel.id.in_(quiz_data.tag_ids)).all()
            quiz.tags = tags

        db.commit()
        db.refresh(quiz)

        quiz_dict = quiz_to_dict(quiz, flashcard_count=0)

        return create_response(
            data=Quiz(**quiz_dict),
            message="Quiz created successfully",
            status_code=status.HTTP_201_CREATED
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create quiz: {str(e)}"
        ) from e


@router.put("/{quiz_id}", response_model=QuizResponse)
async def update_quiz(
    quiz_id: int,
    quiz_data: QuizUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)  # pylint: disable=unused-argument
):
    """Update an existing quiz."""
    try:
        # Validate image size if provided
        validate_image_size(quiz_data.image)

        quiz_service = QuizService(db)
        quiz = quiz_service.get_quiz_by_id(quiz_id)

        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Quiz with ID {quiz_id} not found"
            )

        # Update quiz fields
        update_data = quiz_data.model_dump(exclude_unset=True)

        # Handle special fields
        tag_ids = update_data.pop('tag_ids', None)
        image_data = update_data.pop('image', None)

        # Update regular fields
        for field, value in update_data.items():
            setattr(quiz, field, value)

        # Handle image field - decode Base64 to binary
        if image_data is not None:
            if image_data:
                quiz.image = base64.b64decode(image_data)
            else:
                quiz.image = None

        # Handle tags
        if tag_ids is not None:
            from core.db.models import Tag as TagModel
            tags = db.query(TagModel).filter(TagModel.id.in_(tag_ids)).all()
            quiz.tags = tags

        db.commit()
        db.refresh(quiz)

        flashcards = quiz_service.get_quiz_flashcards(quiz.id)
        quiz_dict = quiz_to_dict(quiz, flashcard_count=len(flashcards))

        return create_response(
            data=Quiz(**quiz_dict),
            message="Quiz updated successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update quiz: {str(e)}"
        ) from e


@router.delete("/{quiz_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quiz(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)  # pylint: disable=unused-argument
):
    """Delete a quiz and all its flashcards."""
    try:
        quiz_service = QuizService(db)
        quiz = quiz_service.get_quiz_by_id(quiz_id)

        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Quiz with ID {quiz_id} not found"
            )

        success = quiz_service.delete_quiz(quiz_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete quiz"
            )
        return None

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete quiz: {str(e)}"
        ) from e


@router.get("/{quiz_id}/statistics", response_model=QuizStatsResponse)
async def get_quiz_statistics(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)  # pylint: disable=unused-argument
):
    """Get detailed statistics for a quiz."""
    try:
        quiz_service = QuizService(db)
        quiz = quiz_service.get_quiz_by_id(quiz_id)

        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Quiz with ID {quiz_id} not found"
            )

        stats = quiz_service.get_quiz_statistics(quiz_id)

        # Add answer types to statistics
        flashcards = quiz_service.get_quiz_flashcards(quiz_id)
        answer_types = {}
        for card in flashcards:
            answer_type = getattr(card, 'answer_type', 'text')
            answer_types[answer_type] = answer_types.get(answer_type, 0) + 1

        stats['answer_types'] = answer_types

        return create_response(
            data=QuizStats(**stats),
            message="Quiz statistics retrieved successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve quiz statistics: {str(e)}"
        ) from e


@router.post("/import", response_model=QuizResponse, status_code=status.HTTP_201_CREATED)
async def import_quiz(
    quiz_data: QuizImportData,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Import a quiz from JSON data."""
    try:
        quiz_service = QuizService(db)

        # Validate quiz data
        if not quiz_service.validate_quiz_data(quiz_data.model_dump()):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid quiz data format"
            )

        quiz = quiz_service.import_quiz_from_dict(quiz_data.model_dump(), current_user.id)

        flashcards = quiz_service.get_quiz_flashcards(quiz.id)
        quiz_dict = quiz_to_dict(quiz, flashcard_count=len(flashcards))

        return create_response(
            data=Quiz(**quiz_dict),
            message=f"Quiz imported successfully with {len(flashcards)} flashcards",
            status_code=status.HTTP_201_CREATED
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to import quiz: {str(e)}"
        ) from e


@router.post("/import-file", response_model=QuizResponse, status_code=status.HTTP_201_CREATED)
async def import_quiz_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Import a quiz from uploaded JSON file."""
    try:
        # Validate file type
        if not file.filename.endswith('.json'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only JSON files are supported"
            )

        # Read and parse file
        content = await file.read()
        try:
            quiz_data = json.loads(content.decode('utf-8'))
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON format"
            ) from e

        quiz_service = QuizService(db)

        # Validate quiz data
        if not quiz_service.validate_quiz_data(quiz_data):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid quiz data structure"
            )

        quiz = quiz_service.import_quiz_from_dict(quiz_data, current_user.id)

        flashcards = quiz_service.get_quiz_flashcards(quiz.id)
        quiz_dict = quiz_to_dict(quiz, flashcard_count=len(flashcards))

        return create_response(
            data=Quiz(**quiz_dict),
            message=f"Quiz imported from file successfully with {len(flashcards)} flashcards",
            status_code=status.HTTP_201_CREATED
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to import quiz file: {str(e)}"
        ) from e


@router.get("/{quiz_id}/export")
async def export_quiz(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)  # pylint: disable=unused-argument
):
    """Export a quiz as JSON data."""
    try:
        quiz_service = QuizService(db)
        quiz = quiz_service.get_quiz_by_id(quiz_id)

        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Quiz with ID {quiz_id} not found"
            )

        flashcards = quiz_service.get_quiz_flashcards(quiz_id)

        # Build export data structure
        export_data = {
            "quiz": {
                "name": quiz.name,
                "subject": quiz.subject,
                "category": quiz.category,
                "level": quiz.level,
                "description": quiz.description,
                "created_at": quiz.created_at.isoformat() if quiz.created_at else None
            },
            "flashcards": []
        }

        for card in flashcards:
            card_data = {
                "question": {
                    "title": card.question_title,
                    "text": card.question_text,
                    "lang": card.question_lang,
                    "difficulty": card.question_difficulty,
                    "emoji": card.question_emoji,
                    "image": card.question_image
                },
                "answer": {
                    "text": card.answer_text,
                    "lang": card.answer_lang,
                    "type": getattr(card, 'answer_type', 'text'),
                    "options": getattr(card, 'answer_options', None),
                    "metadata": getattr(card, 'answer_metadata', None)
                }
            }
            # Remove None values
            card_data["question"] = {k: v for k, v in card_data["question"].items() if v is not None}
            card_data["answer"] = {k: v for k, v in card_data["answer"].items() if v is not None}
            export_data["flashcards"].append(card_data)

        return JSONResponse(
            content=export_data,
            headers={
                "Content-Disposition": f"attachment; filename={quiz.name.replace(' ', '_')}_export.json"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export quiz: {str(e)}"
        ) from e


@router.post("/{quiz_id}/duplicate", response_model=QuizResponse, status_code=status.HTTP_201_CREATED)
async def duplicate_quiz(
    quiz_id: int,
    new_name: Optional[str] = Query(None, description="New name for duplicated quiz"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)  # pylint: disable=unused-argument
):
    """Duplicate an existing quiz with all its flashcards."""
    try:
        quiz_service = QuizService(db)
        original_quiz = quiz_service.get_quiz_by_id(quiz_id)

        if not original_quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Quiz with ID {quiz_id} not found"
            )

        # Create new quiz
        duplicate_name = new_name or f"{original_quiz.name} (Copy)"
        new_quiz = quiz_service.create_quiz(
            name=duplicate_name,
            user_id=current_user.id,
            subject=original_quiz.subject,
            category=original_quiz.category,
            level=original_quiz.level,
            description=original_quiz.description
        )

        # Copy all flashcards
        original_flashcards = quiz_service.get_quiz_flashcards(quiz_id)

        # Build flashcard data for bulk import
        flashcard_data = []
        for card in original_flashcards:
            card_dict = {
                "question": {
                    "title": card.question_title,
                    "text": card.question_text,
                    "lang": card.question_lang,
                    "difficulty": card.question_difficulty,
                    "emoji": card.question_emoji,
                    "image": card.question_image
                },
                "answer": {
                    "text": card.answer_text,
                    "lang": card.answer_lang,
                    "type": getattr(card, 'answer_type', 'text'),
                    "options": getattr(card, 'answer_options', None),
                    "metadata": getattr(card, 'answer_metadata', None)
                }
            }
            flashcard_data.append(card_dict)

        # Import flashcards to new quiz
        flashcard_repo = FlashcardRepository(db)
        flashcard_repo.bulk_create_flashcards(new_quiz.id, flashcard_data)

        quiz_dict = quiz_to_dict(new_quiz, flashcard_count=len(flashcard_data))

        return create_response(
            data=Quiz(**quiz_dict),
            message=f"Quiz duplicated successfully with {len(flashcard_data)} flashcards",
            status_code=status.HTTP_201_CREATED
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to duplicate quiz: {str(e)}"
        ) from e
