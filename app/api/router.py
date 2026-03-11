from fastapi import APIRouter, HTTPException, status, Query, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.book import Book, BookCreate
from app.services import book_service
from uuid import UUID
from typing import List, Optional

router = APIRouter(prefix="/books", tags=["Books"])

@router.get("/", response_model=List[Book])
async def get_all_books(
    limit: int = Query(10, ge=1, le=100, description="Кількість книг на сторінку"),
    offset: int = Query(0, ge=0, description="Скільки книг пропустити"),
    status: Optional[str] = None,
    author: Optional[str] = None,
    sort_by: Optional[str] = Query(None, pattern="^(title|year)$"),
    db: Session = Depends(get_db)
):
    """Отримання списку книг з підтримкою пагінації Limit-Offset"""
    return await book_service.list_books(db, limit, offset, status, author, sort_by)

@router.get("/{book_id}", response_model=Book)
async def get_book_by_id(book_id: UUID, db: Session = Depends(get_db)):
    """Отримання однієї книги за її UUID"""
    book = await book_service.get_book(db, book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Книгу з таким ID не знайдено"
        )
    return book

@router.post("/", response_model=Book, status_code=status.HTTP_201_CREATED)
async def create_book(book: BookCreate, db: Session = Depends(get_db)):
    """Додавання нової книги в базу даних"""
    new_book_data = book.model_dump() 
    return await book_service.create_book(db, new_book_data)

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: UUID, db: Session = Depends(get_db)):
    """Видалення книги за ID"""
    success = await book_service.delete_book(db, book_id)
    if not success:
         
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Книгу не знайдено для видалення"
        )
    return None