"""
Flashcard API routes
"""
import random
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status  # pylint: disable=import-error
from sqlalchemy.orm import Session  # pylint: disable=import-error

from api.api_schemas import (
    AnswerType,
    BulkFlashcardCreate,
    BulkOperationResponse,
    BulkOperationResult,
    Flashcard,
    FlashcardCreate,
    FlashcardFilters,
    FlashcardResponse,
    FlashcardsResponse,
    FlashcardUpdate,
    PaginationParams,
)
from api.dependencies.auth import get_current_user
from api.utils.responses import create_response
from core.db.crud.repository.flashcard_repository import FlashcardRepository
from core.db.database import get_db
from core.services.quiz_service import QuizService

router = APIRouter()


@router.get("/", response_model=FlashcardsResponse)
async def get_flashcards(  # pylint: disable=too-many-locals
    quiz_id: Optional[int] = Query(None, description="Filter by quiz ID"),
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(),
    filters: FlashcardFilters = Depends(),
    current_user=Depends(get_current_user)  # pylint: disable=unused-argument,
):
    """Get flashcards with optional filtering and pagination."""
    try:
        quiz_service = QuizService(db)

        if quiz_id:
            # Get flashcards for specific quiz
            quiz = quiz_service.get_quiz_by_id(quiz_id)
            if not quiz:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Quiz with ID {quiz_id} not found")
            flashcards = quiz_service.get_quiz_flashcards(quiz_id)
        else:
            # Get all flashcards (you'd need to implement this in quiz_service)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="quiz_id parameter is required")

        # Apply filters
        filtered_cards = flashcards

        if filters.difficulty:
            filtered_cards = [c for c in filtered_cards if c.question_difficulty == filters.difficulty]

        if filters.question_lang:
            filtered_cards = [c for c in filtered_cards if c.question_lang == filters.question_lang]

        if filters.answer_lang:
            filtered_cards = [c for c in filtered_cards if c.answer_lang == filters.answer_lang]

        if filters.answer_type:
            filtered_cards = [
                c for c in filtered_cards if getattr(c, "answer_type", "text") == filters.answer_type.value
            ]

        if filters.search_text:
            search_lower = filters.search_text.lower()
            filtered_cards = [
                c
                for c in filtered_cards
                if search_lower in c.question_text.lower() or search_lower in c.answer_text.lower()
            ]

        # Apply pagination
        start = (pagination.page - 1) * pagination.limit
        end = start + pagination.limit
        paginated_cards = filtered_cards[start:end]

        # Convert to response format
        card_data = []
        for card in paginated_cards:
            card_dict = {
                "id": card.id,
                "quiz_id": card.quiz_id,
                "question_title": card.question_title,
                "question_text": card.question_text,
                "question_lang": card.question_lang,
                "question_difficulty": card.question_difficulty,
                "question_emoji": card.question_emoji,
                "question_image": card.question_image,
                "question_examples": getattr(card, "question_examples", None),
                "answer_text": card.answer_text,
                "answer_lang": card.answer_lang,
                "answer_type": getattr(card, "answer_type", "text"),
                "answer_options": getattr(card, "answer_options", None),
                "answer_metadata": getattr(card, "answer_metadata", None),
            }
            card_data.append(Flashcard(**card_dict))

        return create_response(data=card_data, message=f"Retrieved {len(card_data)} flashcards")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to retrieve flashcards: {str(e)}"
        ) from e


@router.get("/{flashcard_id}", response_model=FlashcardResponse)
async def get_flashcard(
    flashcard_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)  # pylint: disable=unused-argument
):
    """Get a specific flashcard by ID."""
    try:
        # Get flashcard from database

        flashcard_repo = FlashcardRepository(db)
        card = flashcard_repo.get_by_id(flashcard_id)

        if not card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Flashcard with ID {flashcard_id} not found"
            )

        card_dict = {
            "id": card.id,
            "quiz_id": card.quiz_id,
            "question_title": card.question_title,
            "question_text": card.question_text,
            "question_lang": card.question_lang,
            "question_difficulty": card.question_difficulty,
            "question_emoji": card.question_emoji,
            "question_image": card.question_image,
            "question_examples": getattr(card, "question_examples", None),
            "answer_text": card.answer_text,
            "answer_lang": card.answer_lang,
            "answer_type": getattr(card, "answer_type", "text"),
            "answer_options": getattr(card, "answer_options", None),
            "answer_metadata": getattr(card, "answer_metadata", None),
        }

        return create_response(data=Flashcard(**card_dict), message="Flashcard retrieved successfully")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to retrieve flashcard: {str(e)}"
        ) from e


@router.post("/", response_model=FlashcardResponse, status_code=status.HTTP_201_CREATED)
async def create_flashcard(
    flashcard_data: FlashcardCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)  # pylint: disable=unused-argument
):
    """Create a new flashcard."""
    try:
        # Verify quiz exists
        quiz_service = QuizService(db)
        quiz = quiz_service.get_quiz_by_id(flashcard_data.quiz_id)

        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Quiz with ID {flashcard_data.quiz_id} not found"
            )

        # Create flashcard
        flashcard_repo = FlashcardRepository(db)
        question_dict = flashcard_data.question.model_dump()
        answer_dict = flashcard_data.answer.model_dump()

        card = flashcard_repo.create_flashcard(flashcard_data.quiz_id, question_dict, answer_dict)

        card_dict = {
            "id": card.id,
            "quiz_id": card.quiz_id,
            "question_title": card.question_title,
            "question_text": card.question_text,
            "question_lang": card.question_lang,
            "question_difficulty": card.question_difficulty,
            "question_emoji": card.question_emoji,
            "question_image": card.question_image,
            "question_examples": getattr(card, "question_examples", None),
            "answer_text": card.answer_text,
            "answer_lang": card.answer_lang,
            "answer_type": getattr(card, "answer_type", "text"),
            "answer_options": getattr(card, "answer_options", None),
            "answer_metadata": getattr(card, "answer_metadata", None),
        }

        return create_response(
            data=Flashcard(**card_dict), message="Flashcard created successfully", status_code=status.HTTP_201_CREATED
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create flashcard: {str(e)}"
        ) from e


@router.put("/{flashcard_id}", response_model=FlashcardResponse)
async def update_flashcard(
    flashcard_id: int,
    flashcard_data: FlashcardUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)  # pylint: disable=unused-argument,
):
    """Update an existing flashcard."""
    try:
        # Get existing flashcard

        flashcard_repo = FlashcardRepository(db)
        card = flashcard_repo.get_by_id(flashcard_id)

        if not card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Flashcard with ID {flashcard_id} not found"
            )

        # Update fields
        update_data = {}

        if flashcard_data.question:
            q = flashcard_data.question
            update_data.update(
                {
                    "question_title": q.title,
                    "question_text": q.text,
                    "question_lang": q.lang,
                    "question_difficulty": q.difficulty,
                    "question_emoji": q.emoji,
                    "question_image": q.image,
                }
            )

        if flashcard_data.answer:
            a = flashcard_data.answer
            update_data.update(
                {
                    "answer_text": a.text,
                    "answer_lang": a.lang,
                    "answer_type": a.type.value,
                    "answer_options": a.options,
                    "answer_metadata": a.metadata,
                }
            )

        # Apply updates
        updated_card = flashcard_repo.update(card, **update_data)

        card_dict = {
            "id": updated_card.id,
            "quiz_id": updated_card.quiz_id,
            "question_title": updated_card.question_title,
            "question_text": updated_card.question_text,
            "question_lang": updated_card.question_lang,
            "question_difficulty": updated_card.question_difficulty,
            "question_emoji": updated_card.question_emoji,
            "question_image": updated_card.question_image,
            "question_examples": getattr(updated_card, "question_examples", None),
            "answer_text": updated_card.answer_text,
            "answer_lang": updated_card.answer_lang,
            "answer_type": getattr(updated_card, "answer_type", "text"),
            "answer_options": getattr(updated_card, "answer_options", None),
            "answer_metadata": getattr(updated_card, "answer_metadata", None),
        }

        return create_response(data=Flashcard(**card_dict), message="Flashcard updated successfully")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update flashcard: {str(e)}"
        ) from e


@router.delete("/{flashcard_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_flashcard(
    flashcard_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)  # pylint: disable=unused-argument
):
    """Delete a flashcard."""
    try:
        # Get existing flashcard

        flashcard_repo = FlashcardRepository(db)
        card = flashcard_repo.get_by_id(flashcard_id)

        if not card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Flashcard with ID {flashcard_id} not found"
            )

        # Delete flashcard
        flashcard_repo.delete(card)

        return None

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete flashcard: {str(e)}"
        ) from e


@router.post("/bulk", response_model=BulkOperationResponse, status_code=status.HTTP_201_CREATED)
async def bulk_create_flashcards(
    bulk_data: BulkFlashcardCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)  # pylint: disable=unused-argument
):
    """Create multiple flashcards at once."""
    try:
        # Verify quiz exists
        quiz_service = QuizService(db)
        quiz = quiz_service.get_quiz_by_id(bulk_data.quiz_id)

        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Quiz with ID {bulk_data.quiz_id} not found"
            )

        # Process flashcards
        successful = 0
        failed = 0
        errors = []

        try:
            flashcard_repo = FlashcardRepository(db)
            created_cards = flashcard_repo.bulk_create_flashcards(bulk_data.quiz_id, bulk_data.flashcards)
            successful = len(created_cards)

        except Exception as e:  # pylint: disable=broad-exception-caught
            failed = len(bulk_data.flashcards)
            errors.append(str(e))

        result = BulkOperationResult(
            total=len(bulk_data.flashcards), successful=successful, failed=failed, errors=errors
        )

        return create_response(
            data=result,
            message=f"Bulk operation completed: {successful} created, {failed} failed",
            status_code=status.HTTP_201_CREATED,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to bulk create flashcards: {str(e)}"
        ) from e


@router.get("/quiz/{quiz_id}/random", response_model=FlashcardsResponse)
async def get_random_flashcards(
    quiz_id: int,
    count: int = Query(5, ge=1, le=50, description="Number of random flashcards"),
    difficulty: Optional[int] = Query(None, ge=1, le=5, description="Filter by difficulty"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)  # pylint: disable=unused-argument,
):
    """Get random flashcards from a quiz."""
    try:
        quiz_service = QuizService(db)
        quiz = quiz_service.get_quiz_by_id(quiz_id)

        if not quiz:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Quiz with ID {quiz_id} not found")

        # Get flashcards
        if difficulty:
            flashcards = quiz_service.get_flashcards_by_difficulty(quiz_id, difficulty)
        else:
            flashcards = quiz_service.get_quiz_flashcards(quiz_id)

        if not flashcards:
            return create_response(data=[], message="No flashcards found")

        # Get random selection

        random_count = min(count, len(flashcards))
        random_cards = random.sample(flashcards, random_count)

        # Convert to response format
        card_data = []
        for card in random_cards:
            card_dict = {
                "id": card.id,
                "quiz_id": card.quiz_id,
                "question_title": card.question_title,
                "question_text": card.question_text,
                "question_lang": card.question_lang,
                "question_difficulty": card.question_difficulty,
                "question_emoji": card.question_emoji,
                "question_image": card.question_image,
                "question_examples": getattr(card, "question_examples", None),
                "answer_text": card.answer_text,
                "answer_lang": card.answer_lang,
                "answer_type": getattr(card, "answer_type", "text"),
                "answer_options": getattr(card, "answer_options", None),
                "answer_metadata": getattr(card, "answer_metadata", None),
            }
            card_data.append(Flashcard(**card_dict))

        return create_response(data=card_data, message=f"Retrieved {len(card_data)} random flashcards")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to get random flashcards: {str(e)}"
        ) from e


@router.get("/quiz/{quiz_id}/types", response_model=dict)
async def get_flashcard_answer_types(
    quiz_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)  # pylint: disable=unused-argument
):
    """Get answer type statistics for flashcards in a quiz."""
    try:
        quiz_service = QuizService(db)
        quiz = quiz_service.get_quiz_by_id(quiz_id)

        if not quiz:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Quiz with ID {quiz_id} not found")

        flashcards = quiz_service.get_quiz_flashcards(quiz_id)

        # Count answer types
        type_counts = {}
        for card in flashcards:
            answer_type = getattr(card, "answer_type", "text")
            type_counts[answer_type] = type_counts.get(answer_type, 0) + 1

        return {
            "success": True,
            "data": {
                "total_flashcards": len(flashcards),
                "answer_types": type_counts,
                "available_types": [t.value for t in AnswerType],
            },
            "message": f"Retrieved answer type statistics for {len(flashcards)} flashcards",
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to get answer type statistics: {str(e)}"
        ) from e
