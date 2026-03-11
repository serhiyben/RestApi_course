from sqlalchemy.orm import Session
from app.models.book import BookModel
from uuid import UUID

async def get_books_from_db(db: Session, limit: int, offset: int, status: str = None, author: str = None, sort_by: str = None):
    query = db.query(BookModel)
    
    if status:
        query = query.filter(BookModel.status == status)
    if author:
        query = query.filter(BookModel.author.ilike(f"%{author}%"))
        
    if sort_by == "title":
        query = query.order_by(BookModel.title)
    elif sort_by == "year":
        query = query.order_by(BookModel.year)
        
    return query.offset(offset).limit(limit).all()

async def get_book_by_id(db: Session, book_id: UUID):
    return db.query(BookModel).filter(BookModel.id == book_id).first()

async def add_book_to_db(db: Session, book_data: dict):
    db_book = BookModel(**book_data)
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

async def delete_book_from_db(db: Session, book_id: UUID):
    db_book = db.query(BookModel).filter(BookModel.id == book_id).first()
    if db_book:
        db.delete(db_book)
        db.commit()
        return True
    return False