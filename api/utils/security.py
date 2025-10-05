"""
Security utilities for API
"""

import hashlib
import secrets
import string

import bcrypt  # pylint: disable=import-error


def hash_password(password: str) -> str:
    """
    Hash password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        Hashed password
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify password against hash.

    Args:
        password: Plain text password
        hashed_password: Hashed password

    Returns:
        True if password matches, False otherwise
    """
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:  # pylint: disable=broad-exception-caught
        return False


def generate_random_string(
    length: int = 32, include_letters: bool = True, include_digits: bool = True, include_punctuation: bool = False
) -> str:
    """
    Generate a random string.

    Args:
        length: Length of the string
        include_letters: Include letters
        include_digits: Include digits
        include_punctuation: Include punctuation

    Returns:
        Random string
    """
    characters = ""

    if include_letters:
        characters += string.ascii_letters
    if include_digits:
        characters += string.digits
    if include_punctuation:
        characters += string.punctuation

    if not characters:
        characters = string.ascii_letters + string.digits

    return "".join(secrets.choice(characters) for _ in range(length))


def generate_api_key(length: int = 32) -> str:
    """
    Generate a secure API key.

    Args:
        length: Length of the API key

    Returns:
        API key string
    """
    return secrets.token_urlsafe(length)


def generate_reset_token(length: int = 64) -> str:
    """
    Generate a password reset token.

    Args:
        length: Length of the token

    Returns:
        Reset token string
    """
    return secrets.token_urlsafe(length)


def hash_string(text: str, algorithm: str = "sha256") -> str:
    """
    Hash a string using specified algorithm.

    Args:
        text: Text to hash
        algorithm: Hash algorithm (md5, sha1, sha256, sha512)

    Returns:
        Hexadecimal hash string
    """
    if algorithm == "md5":
        return hashlib.md5(text.encode()).hexdigest()
    if algorithm == "sha1":
        return hashlib.sha1(text.encode()).hexdigest()
    if algorithm == "sha256":
        return hashlib.sha256(text.encode()).hexdigest()
    if algorithm == "sha512":
        return hashlib.sha512(text.encode()).hexdigest()
    raise ValueError(f"Unsupported algorithm: {algorithm}")


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal attacks.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    if not filename:
        return "unnamed_file"

    # Remove directory separators and dangerous characters
    sanitized = filename.replace("/", "").replace("\\", "")
    sanitized = "".join(char for char in sanitized if char.isalnum() or char in "._-")

    # Ensure filename is not empty
    if not sanitized:
        sanitized = "unnamed_file"

    # Limit length
    if len(sanitized) > 255:
        name, ext = sanitized.rsplit(".", 1) if "." in sanitized else (sanitized, "")
        max_name_len = 250 - len(ext)
        sanitized = name[:max_name_len] + ("." + ext if ext else "")

    return sanitized


def mask_sensitive_data(data: str, mask_char: str = "*", show_last: int = 4) -> str:
    """
    Mask sensitive data (e.g., email, phone, API keys).

    Args:
        data: Sensitive data to mask
        mask_char: Character to use for masking
        show_last: Number of characters to show at the end

    Returns:
        Masked data string
    """
    if not data or len(data) <= show_last:
        return mask_char * len(data) if data else ""

    masked_part = mask_char * (len(data) - show_last)
    visible_part = data[-show_last:]

    return masked_part + visible_part


def generate_otp(length: int = 6) -> str:
    """
    Generate one-time password (OTP).

    Args:
        length: Length of the OTP

    Returns:
        OTP string containing only digits
    """
    return "".join(secrets.choice(string.digits) for _ in range(length))
