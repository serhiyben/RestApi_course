import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app
from app.auth import get_current_user

# МАГІЧНА ФІКСТУРА З 6-Ї ЛАБИ (Тримає один Event Loop для бази даних)
@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

# ================= ТЕСТИ ДЛЯ АНОНІМНОГО ЮЗЕРА =================

@patch("app.limiter.r")
def test_anonymous_under_limit(mock_redis, client):  
    """Тест 1: Анонімний юзер ще не досяг ліміту (має бути 200 OK)"""
    mock_redis.zcard = AsyncMock(return_value=0)
    mock_redis.zremrangebyscore = AsyncMock()
    mock_redis.zadd = AsyncMock()
    mock_redis.expire = AsyncMock()

    response = client.get("/books/public")
    assert response.status_code == 200


@patch("app.limiter.r")
def test_anonymous_limit_reached(mock_redis, client): 
    """Тест 2: Анонімний юзер досяг ліміту 2 зап/хв (має бути 429)"""
    mock_redis.zcard = AsyncMock(return_value=2)
    mock_redis.zremrangebyscore = AsyncMock()

    response = client.get("/books/public")
    assert response.status_code == 429
    assert response.json()["detail"] == "Too many requests"


# ================= ТЕСТИ ДЛЯ АВТОРИЗОВАНОГО ЮЗЕРА =================

def override_get_current_user():
    return "test_rate_limit_user"

@patch("app.limiter.r")
def test_authenticated_under_limit(mock_redis, client): 
    """Тест 3: Авторизований юзер ще не досяг ліміту (має бути 200 OK)"""
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    mock_redis.zcard = AsyncMock(return_value=5)
    mock_redis.zremrangebyscore = AsyncMock()
    mock_redis.zadd = AsyncMock()
    mock_redis.expire = AsyncMock()

    response = client.get("/books/")
    assert response.status_code == 200
    
    app.dependency_overrides = {}


@patch("app.limiter.r")
def test_authenticated_limit_reached(mock_redis, client): 
    """Тест 4: Авторизований юзер досяг ліміту 10 зап/хв (має бути 429)"""
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    mock_redis.zcard = AsyncMock(return_value=10)
    mock_redis.zremrangebyscore = AsyncMock()

    response = client.get("/books/")
    assert response.status_code == 429
    assert response.json()["detail"] == "Too many requests"
    
    app.dependency_overrides = {}