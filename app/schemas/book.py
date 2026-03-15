from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from typing import List, Optional
from enum import Enum

class BookStatus(str, Enum):
    AVAILABLE = "наявна"
    BORROWED = "видана"

class BookBase(BaseModel):
    title: str = Field(..., min_length=1, json_schema_extra={"example": "All Quiet on the Western Front"})
    author: str = Field(..., min_length=1, json_schema_extra={"example": "Erich Maria Remarque"})
    description: Optional[str] = Field(None, json_schema_extra={"example": "depicting the extreme..."})
    status: BookStatus = BookStatus.AVAILABLE
    year: int = Field(..., gt=0, le=2026)

class BookCreate(BookBase):
    pass

class Book(BookBase):
    id: UUID = Field(default_factory=uuid4)

class PaginatedBooksResponse(BaseModel):
    items: List[Book]
    next_cursor: Optional[UUID] = None