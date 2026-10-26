"""The score: passengers added × crowding."""

from app.modules.rankings.kpi import compute_kpi
from app.modules.rankings.schemas import Traffic

US_LOAD_FACTOR_PCT = 80.0


def _traffic(passengers: int, prior: int, seats: int, departures: int = 10) -> Traffic:
    return Traffic(
        period="x",
        passengers=passengers,
        prior_passengers=prior,
        seats=seats,
        departures=departures,
    )


def test_shrinking_airport_scores_zero() -> None:
    kpi = compute_kpi(_traffic(900, 1000, 1000), US_LOAD_FACTOR_PCT)
    assert kpi.growth_pct == -10
    assert kpi.score == 0


def test_score_is_passengers_added_times_crowding() -> None:
    kpi = compute_kpi(_traffic(1100, 1000, 1250), US_LOAD_FACTOR_PCT)
    assert kpi.passenger_increase == 100
    assert kpi.crowding == 1.1
    assert kpi.score == 110


def test_airport_with_no_seats_has_no_crowding() -> None:
    kpi = compute_kpi(_traffic(1100, 1000, 0), US_LOAD_FACTOR_PCT)
    assert kpi.crowding is None
    assert kpi.score == 0


def test_new_service_does_not_explode() -> None:
    kpi = compute_kpi(_traffic(58_777, 7, 85_608), US_LOAD_FACTOR_PCT)
    assert kpi.score == round(58_770 * kpi.crowding)
