import os
from pymongo import MongoClient

# Отримуємо URI з docker-compose, або використовуємо локальний для розробки
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/library_db")

client = MongoClient(MONGO_URI)
db = client.get_default_database()
books_collection = db.get_collection("books")