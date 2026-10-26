"""Live FAA events (ground stops, delay programs, closures)."""

from pydantic import BaseModel


class LiveEvent(BaseModel):
    event: str
    airport: str
    details: dict[str, str]


class LiveStatus(BaseModel):
    fetched_at: str
    events: list[LiveEvent]
    no_active_events: list[str]
    source: str
    error: str | None = None
