from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from app.database import get_users_collection
from app.auth import (
    get_password_hash, verify_password, create_access_token, 
    create_refresh_token, REFRESH_SECRET_KEY, ALGORITHM, get_current_user
)
import jwt


from app.api.router import router as books_router

app = FastAPI(title="Library API with JWT Authentication")

class UserCreate(BaseModel):
    username: str
    password: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

# ================= РОУТИ АВТЕНТИФІКАЦІЇ =================

@app.post("/register", status_code=status.HTTP_201_CREATED, tags=["Auth"])
async def register(user: UserCreate):
    users_col = get_users_collection()
    
    # Перевіряємо, чи є вже такий юзер
    existing_user = await users_col.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user.password)
    await users_col.insert_one({"username": user.username, "hashed_password": hashed_password})
    return {"message": "User created successfully"}

@app.post("/token", tags=["Auth"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    users_col = get_users_collection()
    user = await users_col.find_one({"username": form_data.username})
    
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    access_token = create_access_token(data={"sub": user["username"]})
    refresh_token = create_refresh_token(data={"sub": user["username"]})
    
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

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


# ================= РОУТИ КОРИСТУВАЧА =================

@app.get("/users/me", tags=["Users"])
async def read_users_me(current_user: str = Depends(get_current_user)):
    """Отримати інформацію про поточного авторизованого користувача"""
    return {"username": current_user, "message": "You are successfully authenticated!"}

@app.delete("/users/me", status_code=status.HTTP_204_NO_CONTENT, tags=["Users"])
async def delete_user_me(current_user: str = Depends(get_current_user)):
    """Видалити свій власний акаунт"""
    users_col = get_users_collection()
    await users_col.delete_one({"username": current_user})
    return None

# ================= ПІДКЛЮЧЕННЯ РОУТІВ КНИГ =================

app.include_router(books_router)