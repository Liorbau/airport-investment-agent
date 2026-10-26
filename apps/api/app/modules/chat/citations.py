"""Checks every number in an answer against the tool outputs of its turn (D-012)."""

import re

from app.modules.chat.schemas import NumberCheck, ToolCall

ANSWER_NUMBER = re.compile(r"\d[\d,]*(?:\.\d+)?")
OUTPUT_NUMBER = re.compile(r"\d+(?:\.\d+)?")
ROUNDING_TOLERANCE = 0.05
WHOLE_NUMBER_TOLERANCE = 0.5
# The data window itself, not a data value.
WINDOW = re.compile(r"\b12[- ]months?\b")


def _in_data(number: str, known: set[float]) -> bool:
    """A whole number may be a rounding of the data (19 for 19.4); decimals must match."""
    value = float(number.replace(",", ""))
    tolerance = ROUNDING_TOLERANCE if "." in number else WHOLE_NUMBER_TOLERANCE
    return any(abs(value - known_value) <= tolerance for known_value in known)


def check_numbers(text: str, calls: list[ToolCall]) -> NumberCheck:
    known = {float(value) for call in calls for value in OUTPUT_NUMBER.findall(call.output)}
    numbers = ANSWER_NUMBER.findall(WINDOW.sub("", text))
    unverified = [number for number in numbers if not _in_data(number, known)]
    return NumberCheck(numbers_checked=len(numbers), unverified_numbers=unverified)
