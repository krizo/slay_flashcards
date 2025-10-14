"""
User API routes
"""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query  # pylint: disable=import-error
from sqlalchemy.orm import Session  # pylint: disable=import-error

from api.api_schemas import (
    User, UserCreate, UserUpdate, UserResponse, UsersResponse,
    UserStats, UserStatsResponse, PaginationParams
)
from api.dependencies.auth import get_current_user
from api.utils.responses import create_response
from core.db.crud.repository.session_repository import SessionRepository
from core.db.crud.repository.user_repository import UserRepository
from core.db.database import get_db
from core.services.user_service import UserService

router = APIRouter()


@router.get("/", response_model=UsersResponse)
async def get_users(
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(),
    name_contains: Optional[str] = Query(None, description="Filter users by name pattern"),
    has_sessions: Optional[bool] = Query(None, description="Filter users who have sessions"),
    current_user = Depends(get_current_user)  # pylint: disable=unused-argument
):
    """Get all users with optional filtering and pagination."""
    try:
        user_service = UserService(db)

        if has_sessions is True:
            # Get users who have at least one session
            user_repo = UserRepository(db)
            users = user_repo.get_users_with_sessions()
        elif name_contains:
            # Search users by name pattern
            user_repo = UserRepository(db)
            users = user_repo.search_by_name_pattern(name_contains)
        else:
            # Get all users
            users = user_service.get_all_users()

        # Apply pagination
        start = (pagination.page - 1) * pagination.limit
        end = start + pagination.limit
        paginated_users = users[start:end]

        # Convert to response format
        user_data = []
        for user in paginated_users:
            user_dict = {
                "id": user.id,
                "name": user.name,
                "email": getattr(user, 'email', None),
                "language": getattr(user, 'language', 'pl'),
                "created_at": getattr(user, 'created_at', None)
            }
            user_data.append(User(**user_dict))

        return create_response(
            data=user_data,
            message=f"Retrieved {len(user_data)} users"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve users: {str(e)}"
        ) from e


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)  # pylint: disable=unused-argument
):
    """Get a specific user by ID."""
    try:
        user_repo = UserRepository(db)
        user = user_repo.get_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )

        user_dict = {
            "id": user.id,
            "name": user.name,
            "email": getattr(user, 'email', None),
            "language": getattr(user, 'language', 'pl'),
            "created_at": getattr(user, 'created_at', None)
        }

        return create_response(
            data=User(**user_dict),
            message="User retrieved successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user: {str(e)}"
        ) from e


@router.get("/name/{username}", response_model=UserResponse)
async def get_user_by_name(
    username: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)  # pylint: disable=unused-argument
):
    """Get a user by username."""
    try:
        user_service = UserService(db)
        user = user_service.get_user_by_name(username)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with name '{username}' not found"
            )

        user_dict = {
            "id": user.id,
            "name": user.name,
            "email": getattr(user, 'email', None),
            "language": getattr(user, 'language', 'pl'),
            "created_at": getattr(user, 'created_at', None)
        }

        return create_response(
            data=User(**user_dict),
            message="User retrieved successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user: {str(e)}"
        ) from e


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)  # pylint: disable=unused-argument
):
    """Create a new user."""
    try:
        user_service = UserService(db)

        # Check if user already exists
        existing_user = user_service.get_user_by_name(user_data.name)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User with name '{user_data.name}' already exists"
            )

        user = user_service.create_user(user_data.name)

        user_dict = {
            "id": user.id,
            "name": user.name,
            "email": getattr(user, 'email', None),
            "language": getattr(user, 'language', 'pl'),
            "created_at": getattr(user, 'created_at', None)
        }

        return create_response(
            data=User(**user_dict),
            message="User created successfully",
            status_code=status.HTTP_201_CREATED
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        ) from e


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)  # pylint: disable=unused-argument
):
    """Update an existing user."""
    try:
        user_repo = UserRepository(db)

        # Get existing user
        user = user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )

        # Check if new name conflicts
        if user_data.name and user_data.name != user.name:
            existing_user = user_repo.get_by_name(user_data.name)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"User with name '{user_data.name}' already exists"
                )

        # Update user
        update_fields = user_data.model_dump(exclude_unset=True)
        updated_user = user_repo.update(user, **update_fields)

        user_dict = {
            "id": updated_user.id,
            "name": updated_user.name,
            "email": getattr(updated_user, 'email', None),
            "language": getattr(updated_user, 'language', 'pl'),
            "created_at": getattr(updated_user, 'created_at', None)
        }

        return create_response(
            data=User(**user_dict),
            message="User updated successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {str(e)}"
        ) from e


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    delete_sessions: bool = Query(False, description="Also delete all user sessions"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)  # pylint: disable=unused-argument
):
    """Delete a user and optionally their sessions."""
    try:
        user_repo = UserRepository(db)

        user = user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )

        if delete_sessions:
            # Delete user and all associated sessions
            success = user_repo.delete_user_and_sessions(user_id)
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to delete user and sessions"
                )
        else:
            # Just delete the user
            user_repo.delete(user)

        return None

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user: {str(e)}"
        ) from e


@router.get("/{user_id}/statistics", response_model=UserStatsResponse)
async def get_user_statistics(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)  # pylint: disable=unused-argument
):
    """Get comprehensive statistics for a user."""
    try:
        # Verify user exists
        user_repo = UserRepository(db)
        user = user_repo.get_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )

        # Get statistics using repository method
        session_repo = SessionRepository(db)
        stats = session_repo.get_session_statistics(user_id)

        return create_response(
            data=UserStats(**stats),
            message="User statistics retrieved successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user statistics: {str(e)}"
        ) from e


@router.post("/ensure", response_model=UserResponse)
async def ensure_user_exists(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)  # pylint: disable=unused-argument
):
    """Get user if exists, create if not."""
    try:
        user_service = UserService(db)
        user = user_service.ensure_user_exists(user_data.name)

        user_dict = {
            "id": user.id,
            "name": user.name,
            "email": getattr(user, 'email', None),
            "language": getattr(user, 'language', 'pl'),
            "created_at": getattr(user, 'created_at', None)
        }

        return create_response(
            data=User(**user_dict),
            message="User retrieved or created successfully"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ensure user exists: {str(e)}"
        ) from e


@router.get("/{user_id}/progress", response_model=dict)
async def get_user_progress(
    user_id: int,
    quiz_id: Optional[int] = Query(None, description="Filter by specific quiz"),
    days: Optional[int] = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)  # pylint: disable=unused-argument
):
    """Get user learning progress over time."""
    try:
        # Verify user exists
        user_repo = UserRepository(db)
        user = user_repo.get_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )

        # Get sessions
        session_repo = SessionRepository(db)

        # Get sessions within date range
        since_date = datetime.now() - timedelta(days=days)
        sessions = session_repo.get_sessions_since_date(user_id, since_date)

        # Filter by completed sessions only
        sessions = [s for s in sessions if getattr(s, 'completed', False)]

        # Filter by quiz if specified
        if quiz_id:
            sessions = [s for s in sessions if s.quiz_id == quiz_id]

        # Analyze progress
        progress_data = {
            "total_sessions": len(sessions),
            "learn_sessions": len([s for s in sessions if s.mode == "learn"]),
            "test_sessions": len([s for s in sessions if s.mode == "test"]),
            "days_analyzed": days,
            "quiz_filter": quiz_id,
            "daily_activity": {}
        }

        # Group sessions by date
        for session in sessions:
            date_str = session.started_at.strftime("%Y-%m-%d")
            if date_str not in progress_data["daily_activity"]:
                progress_data["daily_activity"][date_str] = {
                    "learn_sessions": 0,
                    "test_sessions": 0,
                    "scores": []
                }

            progress_data["daily_activity"][date_str][f"{session.mode}_sessions"] += 1
            if session.mode == "test" and session.score is not None:
                progress_data["daily_activity"][date_str]["scores"].append(session.score)

        # Calculate daily averages
        for date_data in progress_data["daily_activity"].values():
            if date_data["scores"]:
                date_data["average_score"] = sum(date_data["scores"]) / len(date_data["scores"])
            else:
                date_data["average_score"] = None

        return {
            "success": True,
            "data": progress_data,
            "message": f"Retrieved progress data for {days} days"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user progress: {str(e)}"
        ) from e


@router.get("/leaderboard", response_model=dict)
async def get_user_leaderboard(  # pylint: disable=too-many-locals
    quiz_id: Optional[int] = Query(None, description="Filter by specific quiz"),
    mode: Optional[str] = Query("test", description="Filter by session mode"),
    limit: int = Query(10, ge=1, le=100, description="Number of top users"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)  # pylint: disable=unused-argument
):
    """Get user leaderboard based on performance."""
    try:
        user_repo = UserRepository(db)
        session_repo = SessionRepository(db)

        # Get most active users
        most_active = user_repo.get_most_active_users(limit)

        leaderboard_data = {
            "most_active": [],
            "best_performers": [],
            "criteria": {
                "quiz_id": quiz_id,
                "mode": mode,
                "limit": limit
            }
        }

        # Process most active users
        for user, session_count in most_active:
            leaderboard_data["most_active"].append({
                "user_id": user.id,
                "username": user.name,
                "session_count": session_count
            })

        # Get best performers (highest average scores)
        if mode == "test":
            all_users = user_repo.get_all()
            best_performers = []

            for user in all_users:
                if quiz_id:
                    sessions = session_repo.get_user_quiz_sessions(user.id, quiz_id)
                    test_sessions = [s for s in sessions if s.mode == "test" and s.score is not None and getattr(s, 'completed', False)]
                else:
                    test_sessions = [s for s in session_repo.get_by_user_id(user.id)
                                   if s.mode == "test" and s.score is not None and getattr(s, 'completed', False)]

                if test_sessions:
                    avg_score = sum(s.score for s in test_sessions) / len(test_sessions)
                    best_performers.append({
                        "user_id": user.id,
                        "username": user.name,
                        "average_score": round(avg_score, 2),
                        "test_count": len(test_sessions)
                    })

            # Sort by average score and limit
            best_performers.sort(key=lambda x: x["average_score"], reverse=True)
            leaderboard_data["best_performers"] = best_performers[:limit]

        return {
            "success": True,
            "data": leaderboard_data,
            "message": f"Retrieved leaderboard data for top {limit} users"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve leaderboard: {str(e)}"
        ) from e


@router.get("/search", response_model=UsersResponse)
async def search_users(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)  # pylint: disable=unused-argument
):
    """Search users by name."""
    try:
        user_repo = UserRepository(db)

        users = user_repo.search_by_name_pattern(q)

        # Limit results
        users = users[:limit]

        # Convert to response format
        user_data = []
        for user in users:
            user_dict = {
                "id": user.id,
                "name": user.name,
                "email": getattr(user, 'email', None),
                "language": getattr(user, 'language', 'pl'),
                "created_at": getattr(user, 'created_at', None)
            }
            user_data.append(User(**user_dict))

        return create_response(
            data=user_data,
            message=f"Found {len(user_data)} users matching '{q}'"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search users: {str(e)}"
        ) from e
