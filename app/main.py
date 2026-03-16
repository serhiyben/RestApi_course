from fastapi import FastAPI
from app.api.router import router as book_router

app = FastAPI(title="Library API with MongoDB")


app.include_router(book_router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Library API (MongoDB Edition)"}