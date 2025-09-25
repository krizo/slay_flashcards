"""
Authentication API routes
"""
from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import bcrypt

from core.db.database import get_db
from core.services.user_service import UserService
from api.api_schemas import (
    LoginRequest, RegisterRequest, Token, AuthResponse, UserResponse, User
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
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

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

    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


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
    """Authenticate user and return access token."""
    try:
        user_service = UserService(db)

        # For this simple implementation, we'll just check if user exists
        # In production, you'd verify password against stored hash
        user = user_service.get_user_by_name(login_data.username)

        if not user:
            # Create user if doesn't exist (for demo purposes)
            # In production, you'd return authentication error
            user = user_service.create_user(login_data.username)

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

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    register_data: RegisterRequest,
    db: Session = Depends(get_db)
):
    """Register new user and return access token."""
    try:
        user_service = UserService(db)

        # Check if user already exists
        existing_user = user_service.get_user_by_name(register_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already exists"
            )

        # Create new user
        # In production, you'd hash the password and store it
        user = user_service.create_user(register_data.username)

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
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    token_data: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get current user information."""
    try:
        user_service = UserService(db)
        user = user_service.get_user_by_name(token_data["username"])

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        user_dict = {
            "id": user.id,
            "name": user.name,
            "created_at": getattr(user, 'created_at', None)
        }

        return create_response(
            data=User(**user_dict),
            message="User information retrieved successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user information: {str(e)}"
        )


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(
    token_data: dict = Depends(verify_token),
    db: Session = Depends(get_db)
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
        )


@router.post("/logout")
async def logout(
    token_data: dict = Depends(verify_token)
):
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