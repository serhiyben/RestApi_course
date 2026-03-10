from app.repository import book_repo

async def list_books(status=None, author=None, sort_by=None):
    books = await book_repo.get_books_from_db()

    if status:
        books = [b for b in books if b["status"] == status]
    if author:
        books = [b for b in books if author.lower() in b["author"].lower()]

    if sort_by == "title":
        books = sorted(books, key=lambda x: x["title"])
    elif sort_by == "year":
        books = sorted(books, key=lambda x: x["year"])

    return books
