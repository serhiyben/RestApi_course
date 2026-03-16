import motor.motor_asyncio
import os


MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo_admin:password@db:27017")


client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)


database = client.library_db


def get_books_collection():
    return database.get_collection("books")
