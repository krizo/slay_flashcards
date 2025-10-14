"""
Authentication API routes
"""
from datetime import datetime, timedelta
from typing import Optional

import jwt  # pylint: disable=import-error
from fastapi import APIRouter, Depends, HTTPException, status  # pylint: disable=import-error
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials  # pylint: disable=import-error
from sqlalchemy.orm import Session  # pylint: disable=import-error
import bcrypt  # pylint: disable=import-error

from core.db.database import get_db
from core.services.user_service import UserService
from api.api_schemas import (
    LoginRequest, RegisterRequest, Token, AuthResponse, UserResponse, User, UserCreate
)
from api.utils.responses import create_response

# CREATE THE ROUTER - This was missing!
router = APIRouter()
security = HTTPBearer()

# JWT Configuration
SECRET_KEY = "your-secret-key-change-in-production"  # Change this in production!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token."""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")

        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return {"username": username, "user_id": user_id}

    except jwt.PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


@router.post("/login", response_model=AuthResponse)
async def login(
        login_data: LoginRequest,
        db: Session = Depends(get_db)
):
    """Authenticate user and return access token. Accepts username or email."""
    try:
        user_service = UserService(db)

        # Try to find user by username first, then by email
        user = user_service.get_user_by_name(login_data.username)
        if not user:
            # Try finding by email if username lookup fails
            user = user_service.get_user_by_email(login_data.username)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password")

        # Password verification
        # TESTING MODE: Uncomment the lines below to skip password verification for testing
        # This is useful when you have users without password_hash in the database
        # if True:  # Skip password check for testing
        #     pass  # Skip to token creation
        # else:

        # PRODUCTION MODE: Verify password (comment out for testing without passwords)
        if not hasattr(user, 'password_hash') or not user.password_hash:
            # User has no password set (legacy data)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password")

        if not verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password")

        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.name, "user_id": user.id},
            expires_delta=access_token_expires
        )

        token = Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Convert to seconds
        )

        return create_response(
            data=token,
            message="Login successful"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        ) from e


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
        register_data: RegisterRequest,
        db: Session = Depends(get_db)
):
    """Register new user and return access token."""
    try:
        user_service = UserService(db)

        # Check if username already exists
        existing_user = user_service.get_user_by_name(register_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already exists"
            )

        # Check if email already exists
        existing_email = user_service.get_user_by_email(register_data.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email address already exists"
            )

        # Convert RegisterRequest to UserCreate (username -> name)
        user_create = UserCreate(
            name=register_data.username,
            password=register_data.password,
            email=register_data.email,
            language=register_data.language or 'pl'
        )

        # Create user
        user = user_service.create_user(user_create)

        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.name, "user_id": user.id},
            expires_delta=access_token_expires
        )

        token = Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

        return create_response(
            data=token,
            message="Registration successful",
            status_code=status.HTTP_201_CREATED
        )

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        ) from e


def get_current_user(
        token_data: dict = Depends(verify_token),
        db: Session = Depends(get_db)
):
    """Dependency to get current authenticated user."""
    try:
        user_service = UserService(db)
        user = user_service.get_user_by_name(token_data["username"])

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return user

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user information: {str(e)}"
        ) from e


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
        current_user = Depends(get_current_user)
):
    """Get current user information."""
    try:
        # Safely construct user dict, handling missing email
        user_dict = {
            "id": current_user.id,
            "name": current_user.name,
            "email": getattr(current_user, 'email', None),  # Handle missing email
            "language": getattr(current_user, 'language', 'pl'),  # User's preferred language
            "created_at": getattr(current_user, 'created_at', None)
        }

        return create_response(
            data=User(**user_dict),
            status_code=status.HTTP_200_OK,
            success=True,
            message="User information retrieved successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user information: {str(e)}"
        ) from e


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(
        token_data: dict = Depends(verify_token),
):
    """Refresh access token."""
    try:
        # Create new access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": token_data["username"], "user_id": token_data["user_id"]},
            expires_delta=access_token_expires
        )

        token = Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

        return create_response(
            data=token,
            message="Token refreshed successfully"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to refresh token: {str(e)}"
        ) from e


@router.post("/logout")
async def logout():
    """Logout user (client-side token removal)."""
    # In a production system, you might want to blacklist the token
    # For now, we'll just return a success message
    return {
        "success": True,
        "message": "Logout successful. Please remove the token from client storage."
    }


@router.get("/verify")
async def verify_authentication(
        token_data: dict = Depends(verify_token)
):
    """Verify if the current token is valid."""
    return {
        "success": True,
        "message": "Token is valid",
        "data": {
            "username": token_data["username"],
            "user_id": token_data["user_id"]
        }
    }
