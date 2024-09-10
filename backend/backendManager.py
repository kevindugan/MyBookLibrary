from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.router import categorization, books

api = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
]

api.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router Endpoints
api.include_router(categorization.router)
api.include_router(books.router)
