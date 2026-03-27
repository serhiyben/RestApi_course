from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from app.database import get_books_collection
from app.auth import get_current_user

router = APIRouter(prefix="/books", tags=["Books"])

# Допоміжна функція, щоб MongoDB ObjectId не ламав JSON
def serialize_mongo_doc(doc) -> dict:
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc

@router.get("/")
async def get_all_books(
    limit: int = 10, 
    offset: int = 0, 
    current_user: str = Depends(get_current_user)  # <--- ЗАХИСТ
):
    books_col = get_books_collection()
    cursor = books_col.find().skip(offset).limit(limit)
    books = await cursor.to_list(length=limit)
    
    return {
        "requested_by": current_user,  # Показуємо, який юзер зробив запит
        "items": [serialize_mongo_doc(book) for book in books]
    }

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_book(
    book_data: dict, 
    current_user: str = Depends(get_current_user)  # <--- ЗАХИСТ
):
    books_col = get_books_collection()
    result = await books_col.insert_one(book_data)
    new_book = await books_col.find_one({"_id": result.inserted_id})
    return serialize_mongo_doc(new_book)

@router.get("/{book_id}")
async def get_book_by_id(
    book_id: str, 
    current_user: str = Depends(get_current_user)  # <--- ЗАХИСТ
):
    books_col = get_books_collection()
    if not ObjectId.is_valid(book_id):
        raise HTTPException(status_code=400, detail="Invalid book ID format")
        
    book = await books_col.find_one({"_id": ObjectId(book_id)})
    if book:
        return serialize_mongo_doc(book)
    raise HTTPException(status_code=404, detail="Book not found")

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: str, 
    current_user: str = Depends(get_current_user)  # <--- ЗАХИСТ
):
    books_col = get_books_collection()
    if not ObjectId.is_valid(book_id):
        raise HTTPException(status_code=400, detail="Invalid book ID format")
        
    result = await books_col.delete_one({"_id": ObjectId(book_id)})
    if result.deleted_count == 1:
        return None
    raise HTTPException(status_code=404, detail="Book not found")