from fastapi import FastAPI
from app.api.router import router as book_router

app = FastAPI(title="Library API")

app.include_router(book_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Library API!"}