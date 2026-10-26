"""Active FAA events for the requested airports, right now."""

from datetime import UTC, datetime

from app.modules.live_status import repository
from app.modules.live_status.repository import SourceUnavailableError
from app.modules.live_status.schemas import LiveStatus

SOURCE = "FAA NAS Status (live)"


def get_live_status(codes: list[str]) -> LiveStatus:
    """Events for `codes`, or an empty status that names the error when the feed is down."""
    now = datetime.now(UTC).isoformat(timespec="minutes")
    wanted = {code.upper() for code in codes}
    try:
        events = [event for event in repository.fetch_events() if event.airport in wanted]
    except SourceUnavailableError as error:
        return LiveStatus(
            fetched_at=now, events=[], no_active_events=[], source=SOURCE, error=str(error)
        )
    return LiveStatus(
        fetched_at=now,
        events=events,
        no_active_events=sorted(wanted - {event.airport for event in events}),
        source=SOURCE,
    )
