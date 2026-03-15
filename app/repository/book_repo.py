from sqlalchemy.orm import Session
from app.models.book import BookModel as Book
from uuid import UUID
from typing import Optional


async def get_books_cursor(
    db: Session,
    limit: int,
    cursor: Optional[UUID] = None,
    status: Optional[str] = None,
    author: Optional[str] = None,
):
    query = db.query(Book)

    if status:
        query = query.filter(Book.status == status)
    if author:
        query = query.filter(Book.author.ilike(f"%{author}%"))

    if cursor:
        query = query.filter(Book.id > cursor)

    books = query.order_by(Book.id).limit(limit).all()

    next_cursor = books[-1].id if len(books) == limit else None

    return books, next_cursor


async def get_book_by_id(db: Session, book_id: UUID):
    return db.query(Book).filter(Book.id == book_id).first()


async def create_book(db: Session, book_data: dict):
    db_book = Book(**book_data)
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


async def delete_book(db: Session, book_id: UUID):
    book = db.query(Book).filter(Book.id == book_id).first()
    if book:
        db.delete(book)
        db.commit()
        return True
    return False
