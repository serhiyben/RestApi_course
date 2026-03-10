import pytest
from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)

def test_create_book():
    """Тест створення книги (POST)"""
    payload = {
        "title": "Solaris",
        "author": "Stanislaw Lem",
        "description": "Science fiction classic",
        "status": "наявна",
        "year": 1961
    }
    response = client.post("/books/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Solaris"
    assert "id" in data  

def test_get_all_books():
    """Тест отримання списку всіх книг (GET)"""
    response = client.get("/books/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_book_by_id():
    """Тест отримання книги за конкретним ID"""
    
    create_res = client.post("/books/", json={
        "title": "Test ID", "author": "Tester", "year": 2024, "status": "наявна"
    })
    book_id = create_res.json()["id"]

    
    response = client.get(f"/books/{book_id}")
    assert response.status_code == 200
    assert response.json()["id"] == book_id

def test_delete_book_idempotent():
    """Тест видалення книги (DELETE) - має бути ідемпотентним"""
    random_id = str(uuid.uuid4())
    
    response1 = client.delete(f"/books/{random_id}")
    assert response1.status_code == 204
    
    response2 = client.delete(f"/books/{random_id}")
    assert response2.status_code == 204

def test_filter_and_sort():
    """Тест фільтрації за автором та сортування за роком"""

    client.post("/books/", json={
        "title": "Filter Test", "author": "UniqueAuthor", "year": 1999, "status": "наявна"
    })
    
    response = client.get("/books/?author=UniqueAuthor&sort_by=year")
    assert response.status_code == 200
    books = response.json()
    assert len(books) >= 1
    assert "UniqueAuthor" in books[0]["author"]