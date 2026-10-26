"""The ranking tool: specific airports, some states, or the whole US, all resolved in code."""

import json

from app.modules.chat.tools.registry import run_tool
from app.modules.rankings.service import MIN_FLIGHTS, get_profiles

NEW_ENGLAND = ["CT", "ME", "MA", "NH", "RI", "VT"]


def _rank(arguments: dict) -> dict:
    return json.loads(run_tool("rank_airports", json.dumps(arguments)))


def test_no_filter_ranks_the_whole_us() -> None:
    ranking = _rank({})
    assert ranking["scope"] == "whole US"
    assert ranking["airports_ranked"] > 600
    assert len(ranking["ranking"]) == 10


def test_states_rank_only_airports_in_them() -> None:
    ranking = _rank({"states": NEW_ENGLAND, "limit": 30})
    assert {"BOS", "PWM"} <= {row["airport"] for row in ranking["ranking"]}


def test_default_sort_is_score_in_descending_order() -> None:
    ranking = _rank({})
    assert ranking["sorted_by"] == "score"
    scores = [row["kpi"]["score"] for row in ranking["ranking"]]
    assert scores == sorted(scores, reverse=True)


def test_no_matching_airports_is_an_empty_ranking() -> None:
    assert _rank({"states": ["ZZ"]})["airports_ranked"] == 0


def test_ranking_by_another_metric_reports_its_value() -> None:
    ranking = _rank({"codes": ["SFO", "JFK", "PWM"], "sort_by": "long_haul_flights"})
    assert ranking["ranking"][0]["airport"] == "JFK"
    assert ranking["ranking"][0]["sort_value"] > ranking["ranking"][1]["sort_value"]
    assert ranking["ranking"][0]["kpi"] is None


def test_lowest_ranks_the_smallest_values_first() -> None:
    rows = _rank({"sort_by": "load_factor", "lowest": True, "limit": 3})["ranking"]
    values = [row["sort_value"] for row in rows]
    assert values == sorted(values)


def test_percent_rankings_skip_airports_with_few_flights() -> None:
    first = _rank({"sort_by": "late_departures", "limit": 1})["ranking"][0]["airport"]
    profile = get_profiles([first]).profiles[0]
    assert profile.delays.flights >= MIN_FLIGHTS
