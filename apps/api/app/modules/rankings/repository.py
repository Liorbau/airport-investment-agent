"""Passenger traffic (BTS T-100) and delays (BTS On-Time) per airport."""

from functools import cache

from app.common.tables import read_table
from app.modules.rankings.schemas import Delays, Traffic


def get_traffic(code: str) -> Traffic | None:
    row = read_table("airport_traffic").get(code)
    return Traffic.model_validate(row) if row else None


def get_delays(code: str) -> Delays | None:
    row = read_table("airport_delays").get(code)
    return Delays.model_validate(row) if row else None


def passengers_by_airport() -> dict[str, int]:
    return {code: int(row["passengers"]) for code, row in read_table("airport_traffic").items()}


@cache
def us_load_factor_pct() -> float:
    rows = read_table("airport_traffic").values()
    return 100 * sum(int(r["passengers"]) for r in rows) / sum(int(r["seats"]) for r in rows)
