"""
Pagination utilities
"""
from typing import List, TypeVar
from math import ceil

T = TypeVar('T')


def paginate_query(items: List[T], page: int, limit: int) -> dict:
    """
    Paginate a list of items.

    Args:
        items: List of items to paginate
        page: Page number (1-based)
        limit: Number of items per page

    Returns:
        Dictionary with paginated data and metadata
    """
    # Calculate pagination metadata
    total = len(items)
    total_pages = ceil(total / limit) if total > 0 else 1
    has_next = page < total_pages
    has_prev = page > 1

    # Calculate start and end indices
    start = (page - 1) * limit
    end = start + limit

    # Get paginated items
    paginated_items = items[start:end]

    return {
        "items": paginated_items,
        "pagination": {
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
            "has_next": has_next,
            "has_prev": has_prev,
            "start": start + 1 if paginated_items else 0,
            "end": start + len(paginated_items)
        }
    }


def get_pagination_params(page: int = 1, limit: int = 20) -> dict:
    """
    Get standardized pagination parameters.

    Args:
        page: Page number (minimum 1)
        limit: Items per page (minimum 1, maximum 100)

    Returns:
        Dictionary with validated pagination parameters
    """
    # Validate and constrain parameters
    page = max(1, page)
    limit = max(1, min(100, limit))

    return {
        "page": page,
        "limit": limit,
        "offset": (page - 1) * limit
    }


class PaginationHelper:
    """Helper class for handling pagination logic."""

    def __init__(self, page: int = 1, limit: int = 20):
        self.page = max(1, page)
        self.limit = max(1, min(100, limit))
        self.offset = (self.page - 1) * self.limit

    def paginate(self, items: List[T]) -> dict:
        """Paginate items using instance parameters."""
        return paginate_query(items, self.page, self.limit)

    def get_slice(self, items: List[T]) -> List[T]:
        """Get just the paginated slice of items."""
        start = self.offset
        end = start + self.limit
        return items[start:end]

    def create_metadata(self, total: int) -> dict:
        """Create pagination metadata for a given total count."""
        total_pages = ceil(total / self.limit) if total > 0 else 1
        has_next = self.page < total_pages
        has_prev = self.page > 1

        return {
            "total": total,
            "page": self.page,
            "limit": self.limit,
            "total_pages": total_pages,
            "has_next": has_next,
            "has_prev": has_prev,
            "start": self.offset + 1 if total > 0 else 0,
            "end": min(self.offset + self.limit, total)
        }


def create_page_links(base_url: str, page: int, total_pages: int) -> dict:
    """
    Create navigation links for pagination.

    Args:
        base_url: Base URL for the API endpoint
        page: Current page number
        total_pages: Total number of pages

    Returns:
        Dictionary with navigation links
    """
    links = {
        "self": f"{base_url}?page={page}",
        "first": f"{base_url}?page=1",
        "last": f"{base_url}?page={total_pages}"
    }

    if page > 1:
        links["prev"] = f"{base_url}?page={page - 1}"

    if page < total_pages:
        links["next"] = f"{base_url}?page={page + 1}"

    return links