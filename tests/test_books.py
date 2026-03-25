import pytest
from app.main import app
from app.database import books_collection

# Створюємо тестовий клієнт Flask
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# Очищаємо базу перед кожним тестом, щоб вони були незалежними
@pytest.fixture(autouse=True)
def clean_db():
    books_collection.delete_many({})
    yield

def test_create_book(client):
    response = client.post("/books", json={
        "title": "The Martian",
        "author": "Andy Weir",
        "year": 2011
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data["title"] == "The Martian"
    assert "_id" in data

def test_get_books(client):
    # Спочатку додаємо книгу
    client.post("/books", json={"title": "Book 1", "author": "A1", "year": 2020})
    
    # Потім отримуємо список
    response = client.get("/books")
    assert response.status_code == 200
    data = response.get_json()
    assert type(data) == list
    assert len(data) == 1

def test_get_book_by_id(client):
    create_res = client.post("/books", json={
        "title": "Unique Book", "author": "Auth", "year": 2024
    })
    book_id = create_res.get_json()["_id"]

    response = client.get(f"/books/{book_id}")
    assert response.status_code == 200
    assert response.get_json()["title"] == "Unique Book"

def test_delete_book(client):
    create_res = client.post("/books", json={
        "title": "To Delete", "author": "Auth", "year": 2024
    })
    book_id = create_res.get_json()["_id"]

    del_res = client.delete(f"/books/{book_id}")
    assert del_res.status_code == 204
    
    get_res = client.get(f"/books/{book_id}")
    assert get_res.status_code == 404