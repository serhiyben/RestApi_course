import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.database import get_books_collection
import motor.motor_asyncio
import os

MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo_admin:password@db:27017")

# МАГІЯ ТУТ: Створюємо нове ізольоване підключення для тестів
async def override_get_collection():
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
    try:
        # Можемо навіть використовувати окрему базу для тестів, щоб не смітити в основній
        yield client.library_test_db.get_collection("books")
    finally:
        client.close() # Закриваємо з'єднання після кожного запиту

# Підміняємо оригінальну функцію бази на нашу тестову
app.dependency_overrides[get_books_collection] = override_get_collection

@pytest.fixture
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_create_book_mongo(async_client):
    response = await async_client.post("/books/", json={
        "title": "The Martian",
        "author": "Andy Weir",
        "year": 2011,
        "description": "Survival on Mars"
    })
    assert response.status_code == 201
    assert "_id" in response.json()

@pytest.mark.asyncio
async def test_get_books_pagination_mongo(async_client):
    response = await async_client.get("/books/", params={"limit": 1, "offset": 0})
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data

@pytest.mark.asyncio
async def test_get_book_by_id_mongo(async_client):
    create_res = await async_client.post("/books/", json={
        "title": "Unique Book", "author": "Auth", "year": 2024
    })
    book_id = create_res.json()["_id"]
    
    response = await async_client.get(f"/books/{book_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Unique Book"

@pytest.mark.asyncio
async def test_delete_book_mongo(async_client):
    create_res = await async_client.post("/books/", json={
        "title": "To Delete", "author": "Auth", "year": 2024
    })
    book_id = create_res.json()["_id"]
    
    del_res = await async_client.delete(f"/books/{book_id}")
    assert del_res.status_code == 204
    
    get_res = await async_client.get(f"/books/{book_id}")
    assert get_res.status_code == 404