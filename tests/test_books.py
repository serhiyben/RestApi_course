import pytest
from uuid import uuid4
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_create_book():
    response = client.post(
        "/books/", json={"title": "Mastering Docker", "author": "Serhii", "year": 2026}
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Mastering Docker"


def test_get_first_page():

    for i in range(3):
        client.post(
            "/books/", json={"title": f"Book {i}", "author": "Author", "year": 2026}
        )

    response = client.get("/books/", params={"limit": 2})
    data = response.json()
    assert len(data["items"]) == 2
    assert data["next_cursor"] is not None


def test_pagination_sequence():
    response = client.get("/books/", params={"limit": 1})
    first_page = response.json()
    cursor = first_page["next_cursor"]

    response = client.get("/books/", params={"limit": 1, "cursor": cursor})
    second_page = response.json()

    assert len(second_page["items"]) == 1
    assert second_page["items"][0]["id"] != first_page["items"][0]["id"]


def test_last_page_cursor_none():

    response = client.get("/books/", params={"limit": 100})
    data = response.json()
    assert data["next_cursor"] is None


def test_invalid_cursor():

    max_uuid = "ffffffff-ffff-ffff-ffff-ffffffffffff"
    response = client.get("/books/", params={"cursor": max_uuid})

    assert response.status_code == 200
    assert len(response.json()["items"]) == 0
    assert response.json()["next_cursor"] is None


def test_delete_book():
    create_res = client.post(
        "/books/", json={"title": "To Delete", "author": "Author", "year": 2026}
    )
    book_id = create_res.json()["id"]

    del_res = client.delete(f"/books/{book_id}")
    assert del_res.status_code == 204


def test_get_book_by_id():
    create_res = client.post(
        "/books/", json={"title": "Find Me", "author": "Author", "year": 2026}
    )
    book_id = create_res.json()["id"]

    get_res = client.get(f"/books/{book_id}")
    assert get_res.status_code == 200
    assert get_res.json()["title"] == "Find Me"


def test_get_nonexistent_book():
    response = client.get(f"/books/{uuid4()}")
    assert response.status_code == 404


def test_filter_and_pagination():
    client.post(
        "/books/", json={"title": "Unique", "author": "SpecialAuthor", "year": 2026}
    )
    response = client.get("/books/", params={"author": "SpecialAuthor", "limit": 1})
    data = response.json()
    assert len(data["items"]) >= 1
    assert data["items"][0]["author"] == "SpecialAuthor"


def test_negative_limit():
    response = client.get("/books/", params={"limit": -1})
    assert response.status_code == 422
