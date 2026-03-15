from sqlalchemy.orm import Session
from app.repository import book_repo
from uuid import UUID
from typing import Optional

async def list_books_cursor(
    db: Session, 
    limit: int, 
    cursor: Optional[UUID] = None, 
    status: Optional[str] = None, 
    author: Optional[str] = None
):
    
    return await book_repo.get_books_cursor(db, limit, cursor, status, author)

async def get_book(db: Session, book_id: UUID):
    return await book_repo.get_book_by_id(db, book_id)

async def create_book(db: Session, book_data: dict):
    return await book_repo.create_book(db, book_data)

async def delete_book(db: Session, book_id: UUID):
    return await book_repo.delete_book(db, book_id)