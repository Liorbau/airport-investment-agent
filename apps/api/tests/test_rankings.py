"""Profiling and ranking airports against the committed tables."""

from app.modules.rankings.service import get_profiles, rank_airports


def test_unknown_airport_is_reported_not_dropped() -> None:
    assert get_profiles(["SFO", "XXX"]).unknown_airports == ["XXX"]


def test_ranking_is_sorted_by_score() -> None:
    ranking = rank_airports(["LAX", "SNA", "SFO", "BOS", "PWM"]).ranking
    values = [row.kpi.score for row in ranking]
    assert values == sorted(values, reverse=True)
    assert [row.rank for row in ranking] == [1, 2, 3, 4, 5]
