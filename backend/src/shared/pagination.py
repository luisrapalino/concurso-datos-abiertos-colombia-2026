from __future__ import annotations

from pydantic import BaseModel, Field


class PaginatedResponse[T](BaseModel):
    """Paginated collection wrapper."""

    items: list[T]
    page: int
    page_size: int
    total_items: int
    total_pages: int

    @classmethod
    def from_items(
        cls,
        items: list[T],
        *,
        page: int,
        page_size: int,
        total_items: int,
    ) -> PaginatedResponse[T]:
        total_pages = max(1, (total_items + page_size - 1) // page_size)
        return cls(
            items=items,
            page=page,
            page_size=page_size,
            total_items=total_items,
            total_pages=total_pages,
        )


class PageParams(BaseModel):
    """Common pagination query parameters."""

    page: int = Field(default=1, ge=1, description="Page number (1-based).")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page.")
