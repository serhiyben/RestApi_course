import pytest
from app.main import app
from app.database import books_collection
from bson.objectid import ObjectId


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def clean_db():
    books_collection.delete_many({})
    yield


def test_create_book(client):
    response = client.post(
        "/books", json={"title": "The Martian", "author": "Andy Weir", "year": 2011}
    )
    assert response.status_code == 201
    assert "_id" in response.get_json()


def test_get_books(client):
    client.post("/books", json={"title": "Book 1", "author": "A1"})
    response = client.get("/books")
    assert response.status_code == 200
    assert len(response.get_json()) == 1


def test_get_nonexistent_book(client):
    """Тест 1: Запит книги, якої точно немає в базі (Помилка 404)"""

    fake_id = str(ObjectId())

    response = client.get(f"/books/{fake_id}")
    assert response.status_code == 404
    assert response.get_json()["message"] == "Book not found"


def test_invalid_objectid_format(client):
    """Тест 2: Передача неправильного формату ID (Помилка 400)"""

    bad_id = "just_some_random_text"

    response = client.get(f"/books/{bad_id}")
    assert response.status_code == 400
    assert response.get_json()["message"] == "Invalid book ID format"


def test_delete_nonexistent_book(client):
    """Тест 3: Спроба видалити книгу, якої немає (Помилка 404)"""
    fake_id = str(ObjectId())

    response = client.delete(f"/books/{fake_id}")
    assert response.status_code == 404
    assert response.get_json()["message"] == "Book not found"


def test_bulk_create_and_data_integrity(client):
    """Тест 4: Масове створення книг і перевірка цілісності даних"""

    for i in range(10):
        client.post(
            "/books",
            json={"title": f"Volume {i}", "author": "System", "year": 2000 + i},
        )

    response = client.get("/books")
    assert response.status_code == 200
    data = response.get_json()

    assert len(data) == 10

    last_book = data[9]
    assert last_book["title"] == "Volume 9"
    assert last_book["year"] == 2009
