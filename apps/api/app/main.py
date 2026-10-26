"""Application wiring: routers and the health check."""

from fastapi import FastAPI

from app.modules.airports.router import router as airports_router
from app.modules.chat.router import router as chat_router

app = FastAPI(title="Airport Investment Agent")
app.include_router(chat_router)
app.include_router(airports_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
