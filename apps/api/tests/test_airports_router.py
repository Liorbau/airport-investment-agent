"""GET /airports: positions for the map."""

from fastapi.testclient import TestClient

from app.main import app


def test_airports_have_positions() -> None:
    airports = {row["iata"]: row for row in TestClient(app).get("/airports").json()}
    assert round(airports["SFO"]["lat"]) == 38
    assert round(airports["SFO"]["lon"]) == -122
