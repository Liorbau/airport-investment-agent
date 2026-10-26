"""Live FAA status: a feed outage is reported in the result, never raised to the agent."""

import pytest

from app.modules.live_status import repository
from app.modules.live_status.repository import SourceUnavailableError
from app.modules.live_status.service import get_live_status


def test_unreachable_feed_is_reported(monkeypatch: pytest.MonkeyPatch) -> None:
    def down() -> list:
        raise SourceUnavailableError("FAA status feed unavailable")

    monkeypatch.setattr(repository, "fetch_events", down)
    assert get_live_status(["SFO"]).error == "FAA status feed unavailable"
