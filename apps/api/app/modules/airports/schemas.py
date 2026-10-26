"""Airport info (name, city, state, position, runways)."""

from pydantic import BaseModel


class Airport(BaseModel):
    iata: str
    name: str
    city: str
    state: str
    lat: float
    lon: float
    runways: int
