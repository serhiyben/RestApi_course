import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_create_book_mongo():
    response = client.post(
        "/books/",
        json={
            "title": "The Martian",
            "author": "Andy Weir",
            "year": 2011,
            "description": "Survival on Mars",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "The Martian"
    assert "id" in data


def test_get_books_pagination_mongo():

    client.post("/books/", json={"title": "Book 1", "author": "A1", "year": 2020})
    client.post("/books/", json={"title": "Book 2", "author": "A2", "year": 2021})

    response = client.get("/books/", params={"limit": 2, "offset": 0})
    assert response.status_code == 200
    data = response.json()

    assert "items" in data
    assert "total" in data
    assert len(data["items"]) == 2
    assert data["total"] >= 3


def test_get_book_by_id_mongo():

    create_res = client.post(
        "/books/", json={"title": "Find Me", "author": "Auth", "year": 2024}
    )
    book_id = create_res.json()["id"]

    response = client.get(f"/books/{book_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Find Me"


def test_delete_book_mongo():
    create_res = client.post(
        "/books/", json={"title": "Delete Me", "author": "Auth", "year": 2024}
    )
    book_id = create_res.json()["id"]

    del_res = client.delete(f"/books/{book_id}")
    assert del_res.status_code == 204

    get_res = client.get(f"/books/{book_id}")
    assert get_res.status_code == 404
