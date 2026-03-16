import motor.motor_asyncio
import os

MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo_admin:password@db:27017")

# Клієнт спочатку порожній
_client = None

def get_db_client():
    global _client
    if _client is None:
        _client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
    return _client

def get_books_collection():
    client = get_db_client()
    database = client.library_db
    return database.get_collection("books")