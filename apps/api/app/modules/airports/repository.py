"""Airport info (name, city, state, runways) from the OurAirports table."""

from app.common.tables import read_table
from app.modules.airports.schemas import Airport


def get_airport(code: str) -> Airport | None:
    row = read_table("airports").get(code)
    return Airport.model_validate(row) if row else None


def all_airports() -> list[Airport]:
    return [Airport.model_validate(row) for row in read_table("airports").values()]
