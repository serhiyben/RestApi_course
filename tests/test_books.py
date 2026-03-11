import pytest
import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def book_id():
    """Створює книгу і повертає її ID для тестів видалення"""
    response = client.post(
        "/books/",
        json={"title": "Test Book", "author": "Tester", "year": 2024}
    )
    return response.json()["id"]

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200

def test_create_book():
    response = client.post(
        "/books/",
        json={"title": "New Python Book", "author": "Guido", "year": 2021}
    )
    assert response.status_code == 201

def test_get_books_pagination():
    # Перевіряємо вимогу лаби: Limit-Offset пагінація
    response = client.get("/books/", params={"limit": 1, "offset": 0})
    assert response.status_code == 200
    assert len(response.json()) <= 1

def test_delete_existing_book(book_id):
    """Видалення існуючої книги — очікуємо 204"""
    response = client.delete(f"/books/{book_id}")
    assert response.status_code == 204

def test_delete_missing_book():
    """Видалення неіснуючої книги — очікуємо 404 (це правильна поведінка твого API)"""
    random_id = str(uuid.uuid4())
    response = client.delete(f"/books/{random_id}")
    assert response.status_code == 404