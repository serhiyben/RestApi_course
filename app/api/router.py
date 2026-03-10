from fastapi import APIRouter, HTTPException, status, Query
from app.schemas.book import Book, BookCreate
from app.services import book_service
from app.repository import book_repo
from uuid import UUID, uuid4
from typing import List, Optional

router = APIRouter(prefix="/books", tags=["Books"])

@router.get("/", response_model=List[Book])
async def get_all_books(
    status: Optional[str] = None,
    author: Optional[str] = None,
    sort_by: Optional[str] = Query(None, pattern="^(title|year)$")
):
    return await book_service.list_books(status, author, sort_by)

@router.get("/{book_id}", response_model=Book)
async def get_book_by_id(book_id: UUID):
    books = await book_repo.get_books_from_db()
    for book in books:
        if book["id"] == book_id:
            return book
    raise HTTPException(status_code=404, detail="Книгу не знайдено")

@router.post("/", response_model=Book, status_code=status.HTTP_201_CREATED)
async def create_book(book: BookCreate):
    new_book = book.model_dump() 
    new_book["id"] = uuid4()
    return await book_repo.add_book_to_db(new_book)

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: UUID):
    
    await book_repo.delete_book_from_db(book_id)
    return None