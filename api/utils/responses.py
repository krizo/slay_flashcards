"""
API response utilities
"""

from datetime import datetime
from typing import Any, Optional

from fastapi import status  # pylint: disable=import-error


def create_response(
    data: Any = None, message: Optional[str] = None, success: bool = True, status_code: int = status.HTTP_200_OK
) -> dict:
    """Create standardized API response."""
    response = {"success": success, "timestamp": datetime.now(), "data": data, "status_code": status_code}

    if message:
        response["message"] = message

    return response


def create_error_response(
    error: str,
    message: str,
    details: Optional[list] = None,
    request_id: Optional[str] = None,
    status_code: int = status.HTTP_400_BAD_REQUEST,
) -> dict:
    """Create standardized error response."""
    response = {
        "success": False,
        "error": error,
        "message": message,
        "timestamp": datetime.now(),
        "status_code": status_code,
    }

    if details:
        response["details"] = details

    if request_id:
        response["request_id"] = request_id

    return response


def create_paginated_response(items: list, total: int, page: int, limit: int, message: Optional[str] = None) -> dict:
    """Create paginated response."""
    total_pages = (total + limit - 1) // limit  # Ceiling division
    has_next = page < total_pages
    has_prev = page > 1

    response = {
        "success": True,
        "timestamp": datetime.now(),
        "data": {
            "items": items,
            "pagination": {
                "total": total,
                "page": page,
                "limit": limit,
                "total_pages": total_pages,
                "has_next": has_next,
                "has_prev": has_prev,
            },
        },
    }

    if message:
        response["message"] = message

    return response


def create_bulk_response(
    total: int, successful: int, failed: int, errors: Optional[list] = None, message: Optional[str] = None
) -> dict:
    """Create bulk operation response."""
    response = {
        "success": failed == 0,
        "timestamp": datetime.now(),
        "data": {"total": total, "successful": successful, "failed": failed, "errors": errors or []},
    }

    if message:
        response["message"] = message
    else:
        response["message"] = f"Bulk operation completed: {successful} successful, {failed} failed"

    return response
