"""The live FAA NAS status feed (XML), fetched on every call (D-020)."""

import urllib.request
import xml.etree.ElementTree as ElementTree

from app.modules.live_status.schemas import LiveEvent

FAA_STATUS_URL = "https://nasstatus.faa.gov/api/airport-status-information"


class SourceUnavailableError(Exception):
    """The FAA feed could not be reached or parsed."""


def fetch_events() -> list[LiveEvent]:
    try:
        with urllib.request.urlopen(FAA_STATUS_URL, timeout=20) as response:
            root = ElementTree.fromstring(response.read())
    except (OSError, ElementTree.ParseError) as error:
        raise SourceUnavailableError(f"FAA status feed unavailable: {error}") from error

    events = []
    for delay_type in root.iter("Delay_type"):
        for element in delay_type.iter():
            if element.find("ARPT") is not None:
                leaves = {
                    child.tag: (child.text or "").strip() for child in element if not len(child)
                }
                events.append(
                    LiveEvent(
                        event=delay_type.findtext("Name", ""),
                        airport=leaves.pop("ARPT"),
                        details=leaves,
                    )
                )
    return events
