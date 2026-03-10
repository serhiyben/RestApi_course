from app.models.storage import books_db
from uuid import UUID

async def get_books_from_db():
    return books_db

async def add_book_to_db(book_data: dict):
    books_db.append(book_data)
    return book_data

async def delete_book_from_db(book_id: UUID):
    global books_db
    books_db[:] = [b for b in books_db if b["id"] != book_id]