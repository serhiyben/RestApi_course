from fastapi import FastAPI
from app.database import engine, Base
from app.api.router import router as book_router


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Library API with PostgreSQL")

app.include_router(book_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Library API with PostgreSQL & Docker!"}