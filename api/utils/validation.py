"""
Validation utilities for API
"""
import re
import html
from typing import Optional
from email_validator import validate_email as validate_email_lib, EmailNotValidError


def validate_email(email: str) -> bool:
    """
    Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        True if valid, False otherwise
    """
    try:
        validate_email_lib(email)
        return True
    except EmailNotValidError:
        return False


def validate_password(password: str) -> dict:
    """
    Validate password strength.

    Args:
        password: Password to validate

    Returns:
        Dictionary with validation results
    """
    result = {
        "valid": True,
        "errors": [],
        "strength": "weak"
    }

    # Length check
    if len(password) < 8:
        result["valid"] = False
        result["errors"].append("Password must be at least 8 characters long")

    # Character type checks
    has_lower = bool(re.search(r'[a-z]', password))
    has_upper = bool(re.search(r'[A-Z]', password))
    has_digit = bool(re.search(r'\d', password))
    has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))

    strength_score = sum([has_lower, has_upper, has_digit, has_special])

    if not has_lower:
        result["errors"].append("Password must contain at least one lowercase letter")
    if not has_upper:
        result["errors"].append("Password must contain at least one uppercase letter")
    if not has_digit:
        result["errors"].append("Password must contain at least one digit")

    # Determine strength
    if strength_score >= 4:
        result["strength"] = "strong"
    elif strength_score >= 3:
        result["strength"] = "medium"
    else:
        result["strength"] = "weak"

    if result["errors"]:
        result["valid"] = False

    return result


def validate_username(username: str) -> dict:
    """
    Validate username format.

    Args:
        username: Username to validate

    Returns:
        Dictionary with validation results
    """
    result = {
        "valid": True,
        "errors": []
    }

    # Length check
    if len(username) < 3:
        result["valid"] = False
        result["errors"].append("Username must be at least 3 characters long")
    elif len(username) > 50:
        result["valid"] = False
        result["errors"].append("Username cannot be longer than 50 characters")

    # Character check (alphanumeric + underscore + hyphen)
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        result["valid"] = False
        result["errors"].append("Username can only contain letters, numbers, underscores, and hyphens")

    # Cannot start/end with special characters
    if username.startswith(('_', '-')) or username.endswith(('_', '-')):
        result["valid"] = False
        result["errors"].append("Username cannot start or end with underscore or hyphen")

    return result


def sanitize_string(text: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize string input by removing HTML and limiting length.

    Args:
        text: Text to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized string
    """
    if not text:
        return ""

    # Remove HTML tags and decode HTML entities
    sanitized = html.escape(text.strip())

    # Remove extra whitespace
    sanitized = re.sub(r'\s+', ' ', sanitized)

    # Limit length if specified
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length].rstrip()

    return sanitized


def validate_file_extension(filename: str, allowed_extensions: list) -> bool:
    """
    Validate file extension.

    Args:
        filename: Name of the file
        allowed_extensions: List of allowed extensions (with dots)

    Returns:
        True if extension is allowed, False otherwise
    """
    if not filename:
        return False

    file_extension = filename.lower().split('.')[-1]
    return f".{file_extension}" in [ext.lower() for ext in allowed_extensions]


def validate_quiz_name(name: str) -> dict:
    """
    Validate quiz name.

    Args:
        name: Quiz name to validate

    Returns:
        Dictionary with validation results
    """
    result = {
        "valid": True,
        "errors": []
    }

    if not name or not name.strip():
        result["valid"] = False
        result["errors"].append("Quiz name is required")
        return result

    name = name.strip()

    if len(name) < 2:
        result["valid"] = False
        result["errors"].append("Quiz name must be at least 2 characters long")
    elif len(name) > 200:
        result["valid"] = False
        result["errors"].append("Quiz name cannot be longer than 200 characters")

    return result


def validate_difficulty(difficulty: int) -> bool:
    """
    Validate difficulty level.

    Args:
        difficulty: Difficulty level to validate

    Returns:
        True if valid (1-5), False otherwise
    """
    return isinstance(difficulty, int) and 1 <= difficulty <= 5


def validate_score(score: int) -> bool:
    """
    Validate test score.

    Args:
        score: Score to validate

    Returns:
        True if valid (0-100), False otherwise
    """
    return isinstance(score, int) and 0 <= score <= 100