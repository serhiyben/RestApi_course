from fastapi import APIRouter, Depends, Query, HTTPException, status
from app.database import get_books_collection
from app.schemas.book import Book, BookCreate, PaginatedBooksResponse
from app.repository import book_repo

router = APIRouter(prefix="/books", tags=["Books"])

@router.get("/", response_model=PaginatedBooksResponse)
async def list_books(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    collection = Depends(get_books_collection)
):
    """Отримання списку книг з MongoDB (Limit-Offset)"""
    books, total = await book_repo.get_books(collection, limit, offset)
    return {"items": books, "total": total}

@router.get("/{book_id}", response_model=Book)
async def get_book(book_id: str, collection = Depends(get_books_collection)):
    """Пошук книги за її ObjectID"""
    book = await book_repo.get_book_by_id(collection, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Книгу не знайдено")
    return book

@router.post("/", response_model=Book, status_code=status.HTTP_201_CREATED)
async def add_book(book: BookCreate, collection = Depends(get_books_collection)):
    """Додавання книги в MongoDB"""
    return await book_repo.create_book(collection, book.model_dump())

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_book(book_id: str, collection = Depends(get_books_collection)):
    """Видалення книги за її ObjectID"""
    if not await book_repo.delete_book(collection, book_id):
        raise HTTPException(status_code=404, detail="Книгу не знайдено для видалення")
    return None