"""Traffic, delays, the KPI, and airport profiles and rankings built from them."""

from typing import Literal

from pydantic import BaseModel, computed_field

RankBy = Literal[
    "score",
    "passengers",
    "growth",
    "crowding",
    "load_factor",
    "late_departures",
    "long_haul_flights",
    "long_haul_pct",
]


class Traffic(BaseModel):
    period: str
    passengers: int
    prior_passengers: int
    seats: int
    departures: int


class Delays(BaseModel):
    flights: int
    late_departure_pct: float
    avg_departure_delay_min: float
    cancelled_pct: float
    cause_carrier_pct: float
    cause_weather_pct: float
    cause_nas_pct: float
    cause_security_pct: float
    cause_lateaircraft_pct: float
    short_haul_flights: int
    medium_haul_flights: int
    long_haul_flights: int

    @computed_field
    def long_haul_pct(self) -> float:
        timed = self.short_haul_flights + self.medium_haul_flights + self.long_haul_flights
        return round(100 * self.long_haul_flights / timed, 1) if timed else 0.0


class Kpi(BaseModel):
    passenger_increase: int
    growth_pct: float | None
    load_factor_pct: float | None
    us_load_factor_pct: float
    crowding: float | None
    score: int


class AirportProfile(BaseModel):
    airport: str
    name: str | None
    state: str | None
    runways: int | None
    traffic: Traffic
    delays: Delays | None
    kpi: Kpi
    notes: list[str]


class Profiles(BaseModel):
    profiles: list[AirportProfile]
    unknown_airports: list[str]
    caveats: list[str]
    sources: dict[str, str]


class RankingRow(BaseModel):
    rank: int
    airport: str
    name: str | None
    passengers: int
    late_departure_pct: float | None
    sort_value: int | float | None
    kpi: Kpi | None


class Ranking(BaseModel):
    scope: str
    sorted_by: RankBy
    airports_ranked: int
    airports_growing: int
    ranking: list[RankingRow]
    period: str | None
    method: str
    caveats: list[str]
    unknown_airports: list[str]
    sources: dict[str, str]
