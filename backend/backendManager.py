from fastapi import FastAPI
from backend.router import categorization, books

api = FastAPI()

# Router Endpoints
api.include_router(categorization.router)
api.include_router(books.router)
