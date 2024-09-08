import uvicorn
from fastapi.responses import RedirectResponse

from backend.backendManager import api

@api.get("/api/v1")
async def home() -> dict:
    return {"message": "Welcome to the Home Book API"}

@api.get("/")
async def redirect():
    return RedirectResponse("/api/v1")

if __name__ == "__main__":
    uvicorn.run(
        "runBackend:api",
        host="0.0.0.0",
        port=8530,
    )
