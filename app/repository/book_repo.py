from pydantic_mongo import PydanticObjectId


async def get_books(collection, limit: int, offset: int):

    total = await collection.count_documents({})

    cursor = collection.find({}).skip(offset).limit(limit)
    books = await cursor.to_list(length=limit)
    return books, total


async def get_book_by_id(collection, book_id: str):

    return await collection.find_one({"_id": PydanticObjectId(book_id)})


async def create_book(collection, book_data: dict):

    result = await collection.insert_one(book_data)

    return await collection.find_one({"_id": result.inserted_id})


async def delete_book(collection, book_id: str):

    result = await collection.delete_one({"_id": PydanticObjectId(book_id)})

    return result.deleted_count > 0
