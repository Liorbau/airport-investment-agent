"""Tool: everything about specific airports: statistics, the KPI, delays and live FAA status."""

from app.modules.chat.schemas import AirportDetails
from app.modules.chat.tools.tool import CODES, Tool
from app.modules.live_status.service import get_live_status
from app.modules.rankings.service import get_profiles


def _details(codes: list[str]) -> AirportDetails:
    return AirportDetails(statistics=get_profiles(codes), live_status=get_live_status(codes))


TOOL = Tool(
    name="airport_details",
    handler=_details,
    progress="Reading airport statistics",
    description="Everything about specific airports: passengers, growth, load factor, delays and "
    "their causes, short/medium/long-haul flights, the KPI, and live FAA events right now.",
    properties={"codes": CODES},
)
