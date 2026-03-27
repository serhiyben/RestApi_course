import pytest
from fastapi.testclient import TestClient
from app.main import app

# Глобальні змінні для стану тестів
TEST_USER = {"username": "test_auto_user", "password": "super_password_123"}
AUTH_HEADERS = {}


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_authentication_flow(client):
    """Тестуємо реєстрацію, логін та рефреш токена"""
    
    # 1. Реєстрація
    res_reg = client.post("/register", json=TEST_USER)
    assert res_reg.status_code in [201, 400]

    # 2. Логін
    res_login = client.post("/token", data={
        "username": TEST_USER["username"], 
        "password": TEST_USER["password"]
    })
    assert res_login.status_code == 200
    tokens = res_login.json()
    
    # Зберігаємо токен
    AUTH_HEADERS["Authorization"] = f"Bearer {tokens['access_token']}"

    # 3. Перевірка профілю (/users/me)
    res_me = client.get("/users/me", headers=AUTH_HEADERS)
    assert res_me.status_code == 200
    assert res_me.json()["username"] == TEST_USER["username"]

    # 4. Перевірка рефрешу
    res_refresh = client.post("/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert res_refresh.status_code == 200


def test_protected_books_flow(client):
    """Тестуємо CRUD операції з книгами, використовуючи токен"""
    
    # 1. Спроба доступу без токена
    res_unauth = client.get("/books/")
    assert res_unauth.status_code == 401

    # 2. Створення книги з токеном
    book_data = {
        "title": "JWT Protected Book", 
        "author": "Pytest Bot", 
        "year": 2026
    }
    res_create = client.post("/books/", json=book_data, headers=AUTH_HEADERS)
    assert res_create.status_code == 201
    book_id = res_create.json()["_id"]

    # 3. Отримання списку книг
    res_get = client.get("/books/", headers=AUTH_HEADERS)
    assert res_get.status_code == 200
    assert "items" in res_get.json()
    
    # 4. Отримання однієї книги
    res_get_one = client.get(f"/books/{book_id}", headers=AUTH_HEADERS)
    assert res_get_one.status_code == 200

    # 5. Видалення книги
    res_delete = client.delete(f"/books/{book_id}", headers=AUTH_HEADERS)
    assert res_delete.status_code == 204

def test_negative_auth_flows(client):
    """Тестуємо обробку помилок при авторизації"""
    
    # 1. Спроба зареєструвати юзера, який ВЖЕ існує (створений у першому тесті)
    res_dup_reg = client.post("/register", json=TEST_USER)
    assert res_dup_reg.status_code == 400
    assert "already registered" in res_dup_reg.json()["detail"]

    # 2. Логін з неправильним паролем
    res_bad_login = client.post("/token", data={
        "username": TEST_USER["username"], 
        "password": "wrong_password_123!"
    })
    assert res_bad_login.status_code == 401

    # 3. Спроба оновити токен за допомогою фейкового рефреш-токена
    res_bad_refresh = client.post("/refresh", json={"refresh_token": "fake_and_invalid_token_string"})
    assert res_bad_refresh.status_code == 401


def test_negative_books_flows(client):
    """Тестуємо обробку помилок при роботі з книгами"""
    
    # 1. Пошук книги з невалідним форматом ID (MongoDB вимагає 24 символи)
    res_bad_format = client.get("/books/12345", headers=AUTH_HEADERS)
    assert res_bad_format.status_code == 400
    assert "Invalid book ID format" in res_bad_format.json()["detail"]

    # 2. Пошук книги, якої не існує (валідна довжина, але фейковий ID)
    fake_mongo_id = "507f1f77bcf86cd799439011"
    res_not_found = client.get(f"/books/{fake_mongo_id}", headers=AUTH_HEADERS)
    assert res_not_found.status_code == 404

    # 3. Спроба видалити книгу, якої не існує
    res_del_not_found = client.delete(f"/books/{fake_mongo_id}", headers=AUTH_HEADERS)
    assert res_del_not_found.status_code == 404