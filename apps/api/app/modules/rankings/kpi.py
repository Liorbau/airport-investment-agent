"""The score: passengers added × crowding (load factor ÷ the US load factor) (D-022)."""

from app.modules.rankings.schemas import Kpi, Traffic


def compute_kpi(traffic: Traffic, us_load_factor_pct: float) -> Kpi:
    increase = traffic.passengers - traffic.prior_passengers
    growth = increase / traffic.prior_passengers if traffic.prior_passengers else None
    load_factor = 100 * traffic.passengers / traffic.seats if traffic.seats else None
    crowding = None if load_factor is None else round(load_factor / us_load_factor_pct, 3)
    return Kpi(
        passenger_increase=increase,
        growth_pct=None if growth is None else round(100 * growth, 1),
        load_factor_pct=None if load_factor is None else round(load_factor, 1),
        us_load_factor_pct=round(us_load_factor_pct, 1),
        crowding=crowding,
        score=0 if crowding is None else round(max(increase, 0) * crowding),
    )
