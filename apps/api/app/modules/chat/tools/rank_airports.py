"""Tool: rank airports by the KPI or another metric: specific airports, some states, or the US."""

from typing import get_args

from app.modules.chat.tools.tool import CODES, Tool
from app.modules.rankings.schemas import RankBy, Ranking
from app.modules.rankings.service import rank_airports

DEFAULT_LIMIT = 10
STATES = {
    "type": "array",
    "items": {"type": "string"},
    "description": "Two-letter state codes, e.g. ['MA', 'ME'] for part of New England",
}


def _rank(
    codes: list[str] | None = None,
    states: list[str] | None = None,
    sort_by: RankBy = "score",
    limit: int = DEFAULT_LIMIT,
    lowest: bool = False,
) -> Ranking:
    return rank_airports(codes, states, sort_by, top=limit, lowest=lowest)


TOOL = Tool(
    name="rank_airports",
    handler=_rank,
    progress="Ranking airports",
    description="Rank airports. Give codes for specific airports, states for a region "
    "(translate names like 'East Coast' into state codes yourself), or neither for the whole "
    "US. sort_by: 'score' (default: passengers added × crowding), or any metric: "
    "'passengers', 'growth' (passengers added), 'crowding' (load factor ÷ US load factor), "
    "'load_factor', 'late_departures', 'long_haul_flights', 'long_haul_pct'. Each row has its "
    "sort_value. lowest=true ranks the smallest values first (airports with no data stay last).",
    properties={
        "codes": CODES,
        "states": STATES,
        "sort_by": {"type": "string", "enum": list(get_args(RankBy))},
        "limit": {"type": "integer", "description": "Rows to return (default 10)"},
        "lowest": {"type": "boolean", "description": "Smallest values first (default false)"},
    },
    required=(),
)
