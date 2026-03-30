from fastapi import APIRouter, Depends, HTTPException, status, Request  
from bson import ObjectId
from app.database import get_books_collection
from app.auth import get_current_user
from app.limiter import rate_limit

router = APIRouter(prefix="/books", tags=["Books"])


def serialize_mongo_doc(doc) -> dict:
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc


# ================= АНОНІМНИЙ РОУТ (Ліміт: 2 зап/хв) =================
@router.get("/public")
async def get_public_books(
    request: Request,
    limit: int = 10, 
    offset: int = 0
):
    """Публічний ендпоінт для всіх (перевірка анонімного ліміту з пагінацією)"""
    # Передаємо user_id=None, бо юзер не авторизований
    #await rate_limit(request, user_id=None)
    
    books_col = get_books_collection()
    cursor = books_col.find().skip(offset).limit(limit)
    books = await cursor.to_list(length=limit)
    
    return {
        "requested_by": "anonymous", # Вказуємо, що це анонімний запит
        "items": [serialize_mongo_doc(book) for book in books]
    }

# ================= АВТОРИЗОВАНИЙ РОУТ (Ліміт: 10 зап/хв) =================
@router.get("/")
async def get_all_books(
    request: Request,                                
    limit: int = 10, 
    offset: int = 0, 
    current_user: str = Depends(get_current_user)
):
    """Захищений ендпоінт (перевірка авторизованого ліміту)"""
    #await rate_limit(request, user_id=current_user)
    
    books_col = get_books_collection()
    cursor = books_col.find().skip(offset).limit(limit)
    books = await cursor.to_list(length=limit)
    
    return {
        "requested_by": current_user,
        "items": [serialize_mongo_doc(book) for book in books]
    }


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_book(
    book_data: dict, 
    current_user: str = Depends(get_current_user)  
):
    books_col = get_books_collection()
    result = await books_col.insert_one(book_data)
    new_book = await books_col.find_one({"_id": result.inserted_id})
    return serialize_mongo_doc(new_book)

@router.get("/{book_id}")
async def get_book_by_id(
    book_id: str, 
    current_user: str = Depends(get_current_user)  
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
    current_user: str = Depends(get_current_user)  
):
    books_col = get_books_collection()
    if not ObjectId.is_valid(book_id):
        raise HTTPException(status_code=400, detail="Invalid book ID format")
        
    result = await books_col.delete_one({"_id": ObjectId(book_id)})
    if result.deleted_count == 1:
        return None
    raise HTTPException(status_code=404, detail="Book not found")