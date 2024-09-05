import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from router import categorization, books

api = FastAPI()

# Router Endpoints
api.include_router(categorization.router)
api.include_router(books.router)

@api.get("/api/v1")
async def home() -> dict:
    return {"message": "Welcome to the Home Book API"}

@api.get("/")
async def redirect():
    return RedirectResponse("/api/v1")

if __name__ == "__main__":
    uvicorn.run(
        "booksApp:api",
        host="0.0.0.0",
        port=8530,
    )
