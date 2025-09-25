"""
Formatting utilities for API responses
"""
from datetime import datetime, timezone
from typing import Optional, Union


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format datetime object to string.

    Args:
        dt: Datetime object to format
        format_str: Format string for output

    Returns:
        Formatted datetime string
    """
    if not isinstance(dt, datetime):
        return ""

    # Ensure timezone aware
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    return dt.strftime(format_str)


def format_datetime_iso(dt: datetime) -> str:
    """
    Format datetime to ISO string format.

    Args:
        dt: Datetime object to format

    Returns:
        ISO formatted datetime string
    """
    if not isinstance(dt, datetime):
        return ""

    # Ensure timezone aware
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    return dt.isoformat()


def parse_datetime(dt_string: str) -> Optional[datetime]:
    """
    Parse datetime string to datetime object.

    Args:
        dt_string: Datetime string to parse

    Returns:
        Datetime object or None if parsing fails
    """
    if not dt_string:
        return None

    # Common datetime formats to try
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%m/%d/%Y"
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(dt_string, fmt)
            # Make timezone aware if not already
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue

    return None


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in bytes to human readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted file size string
    """
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0

    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1

    return f"{size_bytes:.1f} {size_names[i]}"


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human readable format.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        remaining_seconds = int(seconds % 60)
        return f"{minutes}m {remaining_seconds}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"


def format_score(score: Union[int, float]) -> str:
    """
    Format test score with percentage.

    Args:
        score: Score value (0-100)

    Returns:
        Formatted score string
    """
    if not isinstance(score, (int, float)):
        return "N/A"

    return f"{score:.0f}%"


def format_difficulty(difficulty: int) -> str:
    """
    Format difficulty level to descriptive text.

    Args:
        difficulty: Difficulty level (1-5)

    Returns:
        Descriptive difficulty text
    """
    difficulty_map = {
        1: "Very Easy",
        2: "Easy",
        3: "Medium",
        4: "Hard",
        5: "Very Hard"
    }

    return difficulty_map.get(difficulty, "Unknown")


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to specified length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix


def format_relative_time(dt: datetime) -> str:
    """
    Format datetime as relative time (e.g., "2 hours ago").

    Args:
        dt: Datetime object

    Returns:
        Relative time string
    """
    if not isinstance(dt, datetime):
        return "Unknown"

    now = datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    diff = now - dt
    seconds = diff.total_seconds()

    if seconds < 60:
        return "Just now"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif seconds < 86400:
        hours = int(seconds // 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif seconds < 2592000:  # 30 days
        days = int(seconds // 86400)
        return f"{days} day{'s' if days != 1 else ''} ago"
    elif seconds < 31536000:  # 365 days
        months = int(seconds // 2592000)
        return f"{months} month{'s' if months != 1 else ''} ago"
    else:
        years = int(seconds // 31536000)
        return f"{years} year{'s' if years != 1 else ''} ago"
