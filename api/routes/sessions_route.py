"""
Session API routes
"""
import datetime
from collections import defaultdict
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query  # pylint: disable=import-error
from sqlalchemy.orm import Session as DBSession  # pylint: disable=import-error

from api.api_schemas import (
    Session, SessionCreate, SessionUpdate, SessionResponse, SessionsResponse,
    SessionStats, SessionStatsResponse, PaginationParams, SessionFilters,
    TestSubmission, TestResults, TestResultsResponse, CardResult,
    LearningSessionUpdate, SessionMode, AnswerEvaluation as ApiAnswerEvaluation
)
from api.dependencies.auth import get_current_user
from api.utils.responses import create_response
from core.db.crud.repository.session_repository import SessionRepository
from core.db.crud.repository.user_repository import UserRepository
from core.db.database import get_db
from core.learning.sessions.answer_evaluator import TypedAnswerEvaluator, AnswerEvaluation
from core.learning.sessions.quiz_session import TestSessionConfig
from core.services.quiz_service import QuizService
from core.services.user_service import UserService

router = APIRouter()


@router.get("/", response_model=SessionsResponse)
async def get_sessions(
    db: DBSession = Depends(get_db),
    pagination: PaginationParams = Depends(),
    filters: SessionFilters = Depends(),
):
    """Get sessions with optional filtering and pagination."""
    try:
        session_repo = SessionRepository(db)

        # Get sessions based on filters
        if filters.user_id and filters.quiz_id:
            sessions = session_repo.get_user_quiz_sessions(filters.user_id, filters.quiz_id)
        elif filters.user_id:
            sessions = session_repo.get_by_user_id(filters.user_id)
        elif filters.quiz_id:
            sessions = session_repo.get_by_quiz_id(filters.quiz_id)
        else:
            # Get all sessions (you might want to limit this)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either user_id or quiz_id filter is required"
            )

        # Apply additional filters
        if filters.mode:
            sessions = [s for s in sessions if s.mode == filters.mode.value]

        if filters.score_min is not None:
            sessions = [s for s in sessions if s.score is not None and s.score >= filters.score_min]

        if filters.score_max is not None:
            sessions = [s for s in sessions if s.score is not None and s.score <= filters.score_max]

        if filters.started_after:
            sessions = [s for s in sessions if s.started_at >= filters.started_after]

        if filters.started_before:
            sessions = [s for s in sessions if s.started_at <= filters.started_before]

        # Apply pagination
        start = (pagination.page - 1) * pagination.limit
        end = start + pagination.limit
        paginated_sessions = sessions[start:end]

        # Convert to response format
        session_data = []
        for session in paginated_sessions:
            session_dict = {
                "id": session.id,
                "user_id": session.user_id,
                "quiz_id": session.quiz_id,
                "mode": session.mode,
                "started_at": session.started_at,
                "score": session.score,
                "completed_at": getattr(session, 'completed_at', None),
                "completed": getattr(session, 'completed', False)
            }
            session_data.append(Session(**session_dict))

        return create_response(
            data=session_data,
            message=f"Retrieved {len(session_data)} sessions"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve sessions: {str(e)}"
        ) from e


@router.get("/statistics", response_model=SessionStatsResponse)
async def get_session_statistics(  # pylint: disable=too-many-locals
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    quiz_id: Optional[int] = Query(None, description="Filter by quiz ID"),
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: DBSession = Depends(get_db),
):
    """Get session statistics."""
    try:
        session_repo = SessionRepository(db)

        # Get sessions based on filters
        if user_id:
            sessions = session_repo.get_by_user_id(user_id)
        else:
            # Get all sessions (you might want to limit this)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="user_id parameter is required"
            )

        # Filter by date range and only include completed sessions
        since_date = datetime.datetime.now() - datetime.timedelta(days=days)
        recent_sessions = [s for s in sessions if s.started_at >= since_date and getattr(s, 'completed', False)]

        # Filter by quiz if specified
        if quiz_id:
            recent_sessions = [s for s in recent_sessions if s.quiz_id == quiz_id]

        # Calculate statistics
        learn_sessions = [s for s in recent_sessions if s.mode == "learn"]
        test_sessions = [s for s in recent_sessions if s.mode == "test"]
        test_scores = [s.score for s in test_sessions if s.score is not None]

        unique_quizzes = len(set(s.quiz_id for s in recent_sessions))

        # Calculate time-based stats
        now = datetime.datetime.now()
        week_ago = now - datetime.timedelta(days=7)
        month_ago = now - datetime.timedelta(days=30)

        sessions_this_week = len([s for s in recent_sessions if s.started_at >= week_ago])
        sessions_this_month = len([s for s in recent_sessions if s.started_at >= month_ago])

        stats = SessionStats(
            total_sessions=len(recent_sessions),
            learn_sessions=len(learn_sessions),
            test_sessions=len(test_sessions),
            average_score=sum(test_scores) / len(test_scores) if test_scores else None,
            best_score=max(test_scores) if test_scores else None,
            unique_quizzes=unique_quizzes,
            sessions_this_week=sessions_this_week,
            sessions_this_month=sessions_this_month
        )

        return create_response(
            data=stats,
            message=f"Statistics calculated for {days} days"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate session statistics: {str(e)}"
        ) from e


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: int,
    db: DBSession = Depends(get_db),
):
    """Get a specific session by ID."""
    try:
        session_repo = SessionRepository(db)
        session = session_repo.get_by_id(session_id)

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session with ID {session_id} not found"
            )

        session_dict = {
            "id": session.id,
            "user_id": session.user_id,
            "quiz_id": session.quiz_id,
            "mode": session.mode,
            "started_at": session.started_at,
            "score": session.score,
            "completed_at": getattr(session, 'completed_at', None),
            "completed": getattr(session, 'completed', False)
        }

        return create_response(
            data=Session(**session_dict),
            message="Session retrieved successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve session: {str(e)}"
        ) from e


@router.post("/", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: SessionCreate,
    db: DBSession = Depends(get_db),
    current_user = Depends(get_current_user)  # pylint: disable=unused-argument
):
    """Create a new learning or test session."""
    try:
        # Verify user and quiz exist
        user_service = UserService(db)
        quiz_service = QuizService(db)

        user = user_service.get_user_by_name(current_user) if isinstance(current_user, str) else None
        if not user:
            user_repo = UserRepository(db)
            user = user_repo.get_by_id(session_data.user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {session_data.user_id} not found"
            )

        quiz = quiz_service.get_quiz_by_id(session_data.quiz_id)
        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Quiz with ID {session_data.quiz_id} not found"
            )

        # Check for recent duplicate session (idempotency for React Strict Mode)
        session_repo = SessionRepository(db)
        recent_threshold = datetime.datetime.now() - datetime.timedelta(seconds=10)
        user_sessions = session_repo.get_user_quiz_sessions(session_data.user_id, session_data.quiz_id)

        # Find a session that matches user_id, quiz_id, mode and was created in the last 10 seconds
        for existing_session in user_sessions:
            if (existing_session.mode == session_data.mode.value and
                existing_session.started_at >= recent_threshold and
                not getattr(existing_session, 'completed', False)):
                # Return existing session instead of creating duplicate
                session = existing_session
                break
        else:
            # Create new session only if no recent duplicate found
            session = user_service.create_session(
                session_data.user_id,
                session_data.quiz_id,
                session_data.mode.value,
                session_data.score
            )

        session_dict = {
            "id": session.id,
            "user_id": session.user_id,
            "quiz_id": session.quiz_id,
            "mode": session.mode,
            "started_at": session.started_at,
            "score": session.score,
            "completed_at": getattr(session, 'completed_at', None),
            "completed": getattr(session, 'completed', False)
        }

        return create_response(
            data=Session(**session_dict),
            message="Session created successfully",
            status_code=status.HTTP_201_CREATED
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create session: {str(e)}"
        ) from e


@router.put("/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: int,
    session_data: SessionUpdate,
    db: DBSession = Depends(get_db),
):
    """Update an existing session."""
    try:
        session_repo = SessionRepository(db)

        session = session_repo.get_by_id(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session with ID {session_id} not found"
            )

        # Update fields
        update_fields = session_data.model_dump(exclude_unset=True)
        updated_session = session_repo.update(session, **update_fields)

        session_dict = {
            "id": updated_session.id,
            "user_id": updated_session.user_id,
            "quiz_id": updated_session.quiz_id,
            "mode": updated_session.mode,
            "started_at": updated_session.started_at,
            "score": updated_session.score,
            "completed_at": getattr(updated_session, 'completed_at', None),
            "completed": getattr(updated_session, 'completed', False)
        }

        return create_response(
            data=Session(**session_dict),
            message="Session updated successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update session: {str(e)}"
        ) from e


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: int,
    db: DBSession = Depends(get_db),
):
    """Delete a session."""
    try:
        session_repo = SessionRepository(db)

        session = session_repo.get_by_id(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session with ID {session_id} not found"
            )

        session_repo.delete(session)
        return None

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete session: {str(e)}"
        ) from e


@router.post("/test/submit", response_model=TestResultsResponse)
async def submit_test(  # pylint: disable=too-many-locals
    test_data: TestSubmission,
    db: DBSession = Depends(get_db),
):
    """Submit test answers and get results."""
    try:
        # Get session
        session_repo = SessionRepository(db)
        session = session_repo.get_by_id(test_data.session_id)

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session with ID {test_data.session_id} not found"
            )

        if session.mode != "test":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session is not a test session"
            )

        # Get quiz and flashcards
        quiz_service = QuizService(db)
        flashcards = quiz_service.get_quiz_flashcards(session.quiz_id)

        # Create evaluator
        config = TestSessionConfig(
            audio_enabled=False,
            strict_matching=False,
            case_sensitive=False,
            similarity_threshold=0.8,
            allow_partial_credit=True
        )
        evaluator = TypedAnswerEvaluator(config)

        # Evaluate answers
        results = []
        total_score = 0
        correct_count = 0
        partial_count = 0
        incorrect_count = 0

        for answer in test_data.answers:
            # Find corresponding flashcard
            flashcard = next((c for c in flashcards if c.id == answer.flashcard_id), None)
            if not flashcard:
                continue

            # Evaluate answer
            evaluation, score = evaluator.evaluate_answer(answer.user_answer, flashcard)

            # Convert evaluation enum
            if evaluation == AnswerEvaluation.CORRECT:
                api_evaluation = ApiAnswerEvaluation.CORRECT
                correct_count += 1
            elif evaluation == AnswerEvaluation.PARTIAL:
                api_evaluation = ApiAnswerEvaluation.PARTIAL
                partial_count += 1
            else:
                api_evaluation = ApiAnswerEvaluation.INCORRECT
                incorrect_count += 1

            total_score += score

            # Create card result
            card_result = CardResult(
                flashcard_id=flashcard.id,
                question=flashcard.question_title,
                user_answer=answer.user_answer,
                correct_answer=flashcard.answer_text,
                evaluation=api_evaluation,
                score=score,
                time_taken=answer.time_taken
            )
            results.append(card_result)

        # Calculate final score
        final_score = int((total_score / len(test_data.answers)) * 100) if test_data.answers else 0

        # Update session with score and mark as completed
        session_repo.update(session, score=final_score, completed_at=datetime.datetime.now(), completed=True)

        # Calculate total time
        total_time = sum(r.time_taken for r in results if r.time_taken) if any(r.time_taken for r in results) else None

        test_results = TestResults(
            session_id=test_data.session_id,
            total_questions=len(test_data.answers),
            correct=correct_count,
            partial=partial_count,
            incorrect=incorrect_count,
            final_score=final_score,
            time_taken=total_time,
            breakdown=results
        )

        return create_response(
            data=test_results,
            message=f"Test completed with score: {final_score}%"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit test: {str(e)}"
        ) from e


@router.put("/learning/{session_id}/progress", response_model=SessionResponse)
async def update_learning_progress(
    session_id: int,
    progress_data: LearningSessionUpdate,
    db: DBSession = Depends(get_db),
):
    """Update progress for a learning session."""
    try:
        session_repo = SessionRepository(db)

        session = session_repo.get_by_id(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session with ID {session_id} not found"
            )

        if session.mode != "learn":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session is not a learning session"
            )

        # Store progress data (you might want to create a separate table for this)
        # For now, we'll just mark the session as completed
        # total_time = sum(p.time_spent for p in progress_data.progress if p.time_spent)  # Unused
        completed_count = len([p for p in progress_data.progress if p.reviewed])

        # You could store more detailed progress data here
        session_repo.update(session, completed_at=datetime.datetime.now(), completed=True)

        session_dict = {
            "id": session.id,
            "user_id": session.user_id,
            "quiz_id": session.quiz_id,
            "mode": session.mode,
            "started_at": session.started_at,
            "score": session.score,
            "completed_at": getattr(session, 'completed_at', None),
            "completed": getattr(session, 'completed', False)
        }

        return create_response(
            data=Session(**session_dict),
            message=f"Learning progress updated: {completed_count} cards reviewed"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update learning progress: {str(e)}"
        ) from e



@router.post("/{session_id}/complete", response_model=SessionResponse)
async def complete_session(
    session_id: int,
    db: DBSession = Depends(get_db),
):
    """Mark a session as completed."""
    try:
        session_repo = SessionRepository(db)

        session = session_repo.get_by_id(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session with ID {session_id} not found"
            )

        # Mark session as completed
        session_repo.update(
            session,
            completed=True,
            completed_at=datetime.datetime.now()
        )

        session_dict = {
            "id": session.id,
            "user_id": session.user_id,
            "quiz_id": session.quiz_id,
            "mode": session.mode,
            "started_at": session.started_at,
            "score": session.score,
            "completed_at": session.completed_at,
            "completed": True
        }

        return create_response(
            data=Session(**session_dict),
            message="Session marked as completed"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete session: {str(e)}"
        ) from e


@router.get("/user/{user_id}/recent", response_model=SessionsResponse)
async def get_user_recent_sessions(
    user_id: int,
    limit: int = Query(10, ge=1, le=50, description="Number of recent sessions"),
    mode: Optional[SessionMode] = Query(None, description="Filter by session mode"),
    db: DBSession = Depends(get_db),
):
    """Get recent sessions for a user."""
    try:
        # Verify user exists
        user_repo = UserRepository(db)
        user = user_repo.get_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )

        # Get recent sessions
        session_repo = SessionRepository(db)
        quiz_service = QuizService(db)

        if mode:
            sessions = session_repo.get_by_mode(user_id, mode.value)
        else:
            # Get many more sessions to account for filtering incomplete test sessions
            # Increase limit significantly as user may have many incomplete test sessions
            sessions = session_repo.get_recent_sessions(user_id, 100)

        # Filter by completed sessions (test sessions MUST be completed, learn sessions can be incomplete)
        # For test sessions: only show completed ones with scores
        # For learn sessions: show all (completed or not)
        filtered_sessions = []
        for s in sessions:
            if s.mode == 'learn':
                # Include all learn sessions
                filtered_sessions.append(s)
            elif s.mode == 'test' and getattr(s, 'completed', False):
                # Only include completed test sessions
                filtered_sessions.append(s)

        # Limit results after filtering
        sessions = filtered_sessions[:limit]

        # Convert to response format with quiz info
        session_data = []
        for session in sessions:
            # Get quiz details
            quiz = quiz_service.get_quiz_by_id(session.quiz_id)

            session_dict = {
                "id": session.id,
                "user_id": session.user_id,
                "quiz_id": session.quiz_id,
                "mode": session.mode,
                "started_at": session.started_at,
                "score": session.score,
                "completed_at": getattr(session, 'completed_at', None),
                "completed": getattr(session, 'completed', False),
                "quiz_name": quiz.name if quiz else None,
                "quiz_category": quiz.category if quiz else None,
                "quiz_level": quiz.level if quiz else None,
            }
            session_data.append(Session(**session_dict))

        return create_response(
            data=session_data,
            message=f"Retrieved {len(session_data)} recent sessions"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve recent sessions: {str(e)}"
        ) from e


@router.get("/quiz/{quiz_id}/performance", response_model=dict)
async def get_quiz_performance_stats(  # pylint: disable=too-many-locals,too-many-branches
    quiz_id: int,
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: DBSession = Depends(get_db),
):
    """Get performance statistics for a specific quiz."""
    try:
        # Verify quiz exists
        quiz_service = QuizService(db)
        quiz = quiz_service.get_quiz_by_id(quiz_id)

        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Quiz with ID {quiz_id} not found"
            )

        # Get quiz sessions
        session_repo = SessionRepository(db)

        since_date = datetime.datetime.now() - datetime.timedelta(days=days)
        all_quiz_sessions = session_repo.get_by_quiz_id(quiz_id)
        # Only include completed sessions
        recent_sessions = [s for s in all_quiz_sessions if s.started_at >= since_date and getattr(s, 'completed', False)]

        # Analyze performance
        test_sessions = [s for s in recent_sessions if s.mode == "test" and s.score is not None]
        learn_sessions = [s for s in recent_sessions if s.mode == "learn"]

        performance_data = {
            "quiz_id": quiz_id,
            "quiz_name": quiz.name,
            "total_sessions": len(recent_sessions),
            "test_sessions": len(test_sessions),
            "learn_sessions": len(learn_sessions),
            "unique_users": len(set(s.user_id for s in recent_sessions)),
            "days_analyzed": days,
            "scores": {
                "average": sum(s.score for s in test_sessions) / len(test_sessions) if test_sessions else None,
                "highest": max(s.score for s in test_sessions) if test_sessions else None,
                "lowest": min(s.score for s in test_sessions) if test_sessions else None,
                "distribution": {}
            },
            "activity_trend": {}
        }

        # Score distribution
        if test_sessions:
            score_ranges = {
                "90-100": 0, "80-89": 0, "70-79": 0,
                "60-69": 0, "50-59": 0, "0-49": 0
            }

            for session in test_sessions:
                score = session.score
                if score >= 90:
                    score_ranges["90-100"] += 1
                elif score >= 80:
                    score_ranges["80-89"] += 1
                elif score >= 70:
                    score_ranges["70-79"] += 1
                elif score >= 60:
                    score_ranges["60-69"] += 1
                elif score >= 50:
                    score_ranges["50-59"] += 1
                else:
                    score_ranges["0-49"] += 1

            performance_data["scores"]["distribution"] = score_ranges

        # Activity trend (daily activity over the period)
        daily_activity = defaultdict(lambda: {"sessions": 0, "average_score": None, "scores": []})

        for session in recent_sessions:
            date_str = session.started_at.strftime("%Y-%m-%d")
            daily_activity[date_str]["sessions"] += 1
            if session.mode == "test" and session.score is not None:
                daily_activity[date_str]["scores"].append(session.score)

        # Calculate daily averages
        for date_data in daily_activity.values():
            if date_data["scores"]:
                date_data["average_score"] = sum(date_data["scores"]) / len(date_data["scores"])
            # Remove the scores list from output
            del date_data["scores"]

        performance_data["activity_trend"] = dict(daily_activity)

        return {
            "success": True,
            "data": performance_data,
            "message": f"Performance statistics retrieved for quiz '{quiz.name}'"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve quiz performance stats: {str(e)}"
        ) from e
