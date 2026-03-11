from sqlalchemy.orm import Session
from app.repository import book_repo
from uuid import UUID

async def list_books(db: Session, limit: int, offset: int, status: str = None, author: str = None, sort_by: str = None):
    return await book_repo.get_books_from_db(db, limit, offset, status, author, sort_by)

async def get_book(db: Session, book_id: UUID):
    return await book_repo.get_book_by_id(db, book_id)

async def create_book(db: Session, book_data: dict):
    return await book_repo.add_book_to_db(db, book_data)

async def delete_book(db: Session, book_id: UUID):
    return await book_repo.delete_book_from_db(db, book_id)