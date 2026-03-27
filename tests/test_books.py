from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from app.database import get_users_collection
from app.auth import (
    get_password_hash, verify_password, create_access_token, 
    create_refresh_token, REFRESH_SECRET_KEY, ALGORITHM
)
import jwt
# Імпортуємо твій роутер з книгами
from app.api.router import router as book_router

app = FastAPI(title="Library API with JWT Authentication")

# Схеми для авторизації
class UserCreate(BaseModel):
    username: str
    password: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

# ================= РОУТИ АВТЕНТИФІКАЦІЇ =================

@app.post("/register", status_code=status.HTTP_201_CREATED, tags=["Auth"])
async def register(user: UserCreate):
    users_col = get_users_collection()
    
    # Перевірка чи юзер вже існує
    existing_user = await users_col.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Зберігаємо хеш пароля, а не сам пароль
    hashed_password = get_password_hash(user.password)
    await users_col.insert_one({"username": user.username, "hashed_password": hashed_password})
    return {"message": "User created successfully"}

@app.post("/token", tags=["Auth"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    users_col = get_users_collection()
    user = await users_col.find_one({"username": form_data.username})
    
    # Перевірка логіну та пароля
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    # Видача токенів
    access_token = create_access_token(data={"sub": user["username"]})
    refresh_token = create_refresh_token(data={"sub": user["username"]})
    
    return {
        "access_token": access_token, 
        "refresh_token": refresh_token, 
        "token_type": "bearer"
    }

@app.post("/refresh", tags=["Auth"])
async def refresh_access_token(request: RefreshTokenRequest):
    try:
        payload = jwt.decode(request.refresh_token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
            
        new_access_token = create_access_token(data={"sub": username})
        return {"access_token": new_access_token, "token_type": "bearer"}
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

# ================= ПІДКЛЮЧЕННЯ РОУТІВ КНИГ =================
app.include_router(book_router)