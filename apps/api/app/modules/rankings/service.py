"""Profiles and ranks airports by the KPI or any other metric. Every result names its sources."""

from collections.abc import Callable

from app.modules.airports import repository as airports_repository
from app.modules.rankings import repository
from app.modules.rankings.kpi import compute_kpi
from app.modules.rankings.schemas import AirportProfile, Profiles, RankBy, Ranking, RankingRow

# % metrics from fewer flights are noise (one late flight can be 100%).
MIN_FLIGHTS = 1000
SOURCES = {
    "traffic": "BTS T-100 Segment, by origin airport (data.bts.gov)",
    "delays": "BTS On-Time Performance, large US carriers, domestic flights",
    "airport_info": "OurAirports",
}
CAVEATS = [
    "Departures include cargo flights, so passengers per departure is understated at cargo "
    "hubs (e.g. ANC).",
    "Delay and flight-length data cover domestic flights of large US carriers only.",
    "Long-haul means a scheduled flight time over 6 hours (medium 3-6, short under 3); "
    "international flights are not in this data.",
    f"Rankings by a % or ratio skip airports with fewer than {MIN_FLIGHTS} flights a year.",
]


def _enough_flights(p: AirportProfile) -> bool:
    return p.delays is not None and p.delays.flights >= MIN_FLIGHTS


def _busy(p: AirportProfile) -> bool:
    return p.traffic.departures >= MIN_FLIGHTS


# Rows carry the KPI only when ranked by it, so the model cannot table it under another metric.
KPI_SORTS = ("score",)
SORTS: dict[RankBy, Callable[[AirportProfile], float | None]] = {
    "score": lambda p: p.kpi.score,
    "passengers": lambda p: p.traffic.passengers,
    "growth": lambda p: p.kpi.passenger_increase,
    "crowding": lambda p: p.kpi.crowding if _busy(p) else None,
    "load_factor": lambda p: p.kpi.load_factor_pct if _busy(p) else None,
    "late_departures": lambda p: p.delays.late_departure_pct if _enough_flights(p) else None,
    "long_haul_flights": lambda p: p.delays.long_haul_flights if p.delays else None,
    "long_haul_pct": lambda p: p.delays.long_haul_pct if _enough_flights(p) else None,
}
METHOD = (
    "score = passengers added (latest 12 months minus the 12 before; 0 if shrinking) x "
    "crowding. Crowding = the airport's load factor (passengers / seats) / the US load factor; "
    "above 1 means fuller than the US average."
)


def _profile(code: str) -> AirportProfile | None:
    traffic = repository.get_traffic(code)
    if traffic is None:
        return None
    delays = repository.get_delays(code)
    info = airports_repository.get_airport(code)
    return AirportProfile(
        airport=code,
        name=info.name if info else None,
        state=info.state if info else None,
        runways=info.runways if info else None,
        traffic=traffic,
        delays=delays,
        kpi=compute_kpi(traffic, repository.us_load_factor_pct()),
        notes=[] if delays else ["No delay data: not served by large reporting carriers."],
    )


def get_profiles(codes: list[str]) -> Profiles:
    profiles = {code.upper(): _profile(code.upper()) for code in codes}
    return Profiles(
        profiles=[profile for profile in profiles.values() if profile],
        unknown_airports=[code for code, profile in profiles.items() if profile is None],
        caveats=CAVEATS,
        sources=SOURCES,
    )


def _codes_in(states: list[str]) -> list[str]:
    traffic = repository.passengers_by_airport()
    wanted = {state.upper() for state in states}
    return [
        airport.iata
        for airport in airports_repository.all_airports()
        if airport.iata in traffic and (not wanted or airport.state in wanted)
    ]


def _scope(codes: list[str] | None, states: list[str] | None) -> str:
    if codes:
        return "airports " + ", ".join(codes)
    if states:
        return "states " + ", ".join(states)
    return "whole US"


def rank_airports(
    codes: list[str] | None = None,
    states: list[str] | None = None,
    by: RankBy = "score",
    top: int | None = None,
    lowest: bool = False,
) -> Ranking:
    """Ranks the given airports, else every airport in `states`, else the whole US."""
    scope = _scope(codes, states)
    result = get_profiles(codes or _codes_in(states or []))
    value = SORTS[by]
    direction = 1 if lowest else -1
    ranked = sorted(result.profiles, key=lambda p: (value(p) is None, direction * (value(p) or 0)))
    rows = [
        RankingRow(
            rank=position,
            airport=profile.airport,
            name=profile.name,
            passengers=profile.traffic.passengers,
            late_departure_pct=profile.delays.late_departure_pct if profile.delays else None,
            sort_value=value(profile),
            kpi=profile.kpi if by in KPI_SORTS else None,
        )
        for position, profile in enumerate(ranked[:top], start=1)
    ]
    return Ranking(
        scope=scope,
        sorted_by=by,
        airports_ranked=len(ranked),
        airports_growing=sum(p.kpi.score > 0 for p in ranked),
        ranking=rows,
        period=ranked[0].traffic.period if ranked else None,
        method=METHOD,
        caveats=CAVEATS,
        unknown_airports=result.unknown_airports,
        sources=SOURCES,
    )
