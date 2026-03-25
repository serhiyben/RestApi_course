# Library API (FastAPI) — Лабораторна робота №5

Виконав студент групи ІПЗ-31 
Бень Сергій

## Що реалізовано в Лабі №
Здійсненно перехід до flask

### Основні зміни та досягнення:
1. Перехід на Flask-RESTful
2. Синхронна робота з MongoDB 
3. Ручна специфікація Swagger (Flasgger) 
4. Вбудоване тестування Flask


## Як запустити

1. **Збірка образів та запуск контейнерів у фоновому режимі:**
   ```bash
   docker-compose up -d --build

## Як запустити
1. Встановити залежності: `pip install -r requirements.txt`
2. Запустити сервер: `uvicorn app.main:app --reload`
3. Документація Swagger: `http://127.0.0.1:8000/docs`

## Документація Swagger (для тестування API):
Відкрийте у браузері: http://localhost:8000/docs

# Збірка образів та запуск контейнерів у фоновому режимі
docker-compose up -d --build

## Тестування
The tests can be executed inside a Docker container.

docker exec -it library_app python -m pytest
