"""The number check: every number in an answer must appear in the turn's tool outputs."""

from app.modules.chat.citations import check_numbers
from app.modules.chat.schemas import ToolCall

CALLS = [
    ToolCall(name="airport_details", arguments="{}", output='{"load_factor_pct": 82.6}'),
    ToolCall(name="rank_airports", arguments="{}", output='{"passengers": 26642605}'),
]


def test_numbers_from_any_tool_output_pass() -> None:
    check = check_numbers("Load factor 82.6% with 26,642,605 passengers.", CALLS)
    assert check.numbers_checked == 2
    assert check.unverified_numbers == []


def test_a_number_not_in_the_data_is_flagged() -> None:
    assert check_numbers("Load factor is 85%.", CALLS).unverified_numbers == ["85"]


def test_rounding_within_tolerance_passes() -> None:
    assert check_numbers("Load factor is 82.62%.", CALLS).unverified_numbers == []


def test_an_answer_without_numbers_checks_nothing() -> None:
    assert check_numbers("SFO is crowded.", CALLS).numbers_checked == 0


def test_a_whole_number_rounded_from_the_data_passes() -> None:
    assert check_numbers("Load factor is about 83%.", CALLS).unverified_numbers == []


def test_a_miscopied_large_number_is_flagged() -> None:
    assert check_numbers("28,877,785 passengers", CALLS).unverified_numbers == ["28,877,785"]


def test_the_12_month_window_is_not_a_data_number() -> None:
    assert check_numbers("Over the latest 12 months.", []).numbers_checked == 0
