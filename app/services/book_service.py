from app.repository import book_repo

# Ми прибрали імпорт Session та UUID, бо в Монго вони не потрібні в такому вигляді

async def get_all_books(collection, limit: int, offset: int):
    """Сервіс для отримання списку книг з пагінацією Limit-Offset"""
    return await book_repo.get_books(collection, limit, offset)

async def get_book(collection, book_id: str):
    """Сервіс для пошуку однієї книги за її рядковим ID"""
    return await book_repo.get_book_by_id(collection, book_id)

async def create_book(collection, book_data: dict):
    """Сервіс для створення нової книги"""
    return await book_repo.create_book(collection, book_data)

async def delete_book(collection, book_id: str):
    """Сервіс для видалення книги"""
    return await book_repo.delete_book(collection, book_id)