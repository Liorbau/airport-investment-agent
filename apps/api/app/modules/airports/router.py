"""GET /airports: every airport with its position, for the map of top picks."""

from fastapi import APIRouter

from app.modules.airports.repository import all_airports
from app.modules.airports.schemas import Airport

router = APIRouter()


@router.get("/airports")
def airports() -> list[Airport]:
    return all_airports()
