# Library API (FastAPI) — Лабораторна робота №2

Виконав студент групи ІПЗ-31 
Бень Сергій

# У другій лабораторній роботі було реалізовано:

Контейнеризацію: Повний перехід на Docker (App + PostgreSQL).

Пагінацію: Реалізовано Limit-Offset пагінацію для списку книг.

Тестування: Написано автоматизовані тести з використанням pytest та фікстур.

Базу даних: Використання PostgreSQL замість SQLite.

## Як запустити
1. Встановити залежності: `pip install -r requirements.txt`
2. Запустити сервер: `uvicorn app.main:app --reload`
3. Документація Swagger: `http://127.0.0.1:8000/docs`

## Тестування
The tests can be executed inside a Docker container.

Запуск автоматичних тестів локально: `python -m pytest`
