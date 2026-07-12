from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    skip: int = Field(default=0, ge=0, description="Количество пропускаемых записей")
    limit: int = Field(default=20, ge=1, le=100, description="Количество записей на страницу")


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    skip: int
    limit: int
    has_next: bool
    has_previous: bool
