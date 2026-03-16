from pydantic import BaseModel, Field, ConfigDict
from pydantic_mongo import PydanticObjectId
from typing import Optional, List


class BookBase(BaseModel):
    title: str
    author: str
    description: Optional[str] = None
    year: int


class BookCreate(BookBase):
    pass


class Book(BookBase):

    id: Optional[PydanticObjectId] = Field(None, alias="_id")

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)


class PaginatedBooksResponse(BaseModel):
    items: List[Book]
    total: int
