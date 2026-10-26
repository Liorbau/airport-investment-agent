"""Builds the committed data tables for the newest 12 months BTS has published (D-020)."""

import bisect
import csv
import io
import json
import urllib.parse
import urllib.request
import zipfile
from collections import defaultdict
from collections.abc import Iterator
from pathlib import Path

API_DIR = Path(__file__).resolve().parent.parent
CACHE_DIR = API_DIR / ".cache"
DATA_DIR = API_DIR / "data"

T100_URL = "https://data.bts.gov/resource/r495-tyji.json"
ONTIME_URL = (
    "https://transtats.bts.gov/PREZIP/"
    "On_Time_Reporting_Carrier_On_Time_Performance_1987_present_{year}_{month}.zip"
)
OURAIRPORTS_URL = "https://davidmegginson.github.io/ourairports-data/{name}.csv"

TRAFFIC_FIELDS = ["passengers", "seats", "departures"]
HAUL_EDGES_MIN = [180, 360]
HAUL_COLUMNS = ["short_haul_flights", "medium_haul_flights", "long_haul_flights"]
CAUSES = ["CarrierDelay", "WeatherDelay", "NASDelay", "SecurityDelay", "LateAircraftDelay"]

Month = tuple[int, int]


def _t100(params: dict[str, str]) -> list[dict[str, str]]:
    url = f"{T100_URL}?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url, timeout=120) as response:
        return json.load(response)


def _newest_t100_month() -> Month:
    newest = _t100({"$select": "max(reporting_month) as newest"})[0]["newest"]
    return int(newest[:4]), int(newest[5:7])


def _window(end: Month, months_back: int = 0) -> list[Month]:
    last = end[0] * 12 + end[1] - 1 - months_back
    return [(index // 12, index % 12 + 1) for index in range(last - 11, last + 1)]


def _period(months: list[Month]) -> str:
    (first_year, first_month), (last_year, last_month) = months[0], months[-1]
    return f"{first_year}-{first_month:02d}..{last_year}-{last_month:02d}"


def _built_period() -> str | None:
    path = DATA_DIR / "airport_traffic.csv"
    if not path.exists():
        return None
    with open(path, newline="") as file:
        return next(csv.DictReader(file))["period"]


def _traffic_totals(months: list[Month]) -> dict[str, list[int]]:
    start, end = (f"{year}-{month:02d}-01" for year, month in (months[0], months[-1]))
    rows = _t100(
        {
            "$select": "origin_airport_code as airport, "
            + ", ".join(f"sum(total_{field}) as {field}" for field in TRAFFIC_FIELDS),
            "$where": f"reporting_month between '{start}' and '{end}'",
            "$group": "origin_airport_code",
            "$limit": "50000",
        }
    )
    return {row["airport"]: [round(float(row[field])) for field in TRAFFIC_FIELDS] for row in rows}


def build_traffic(months: list[Month]) -> int:
    current, prior = _traffic_totals(months), _traffic_totals(_window(months[-1], 12))
    with open(DATA_DIR / "airport_traffic.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(
            ["airport", "period", *TRAFFIC_FIELDS, *(f"prior_{f}" for f in TRAFFIC_FIELDS)]
        )
        for airport in sorted(current):
            prior_values = prior.get(airport, [0] * len(TRAFFIC_FIELDS))
            writer.writerow([airport, _period(months), *current[airport], *prior_values])
    return len(current)


def _download(url: str, path: Path) -> Path:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        partial = path.with_suffix(".part")
        urllib.request.urlretrieve(url, partial)
        partial.rename(path)
    return path


def _flight_rows(year: int, month: int) -> Iterator[dict[str, str]]:
    url = ONTIME_URL.format(year=year, month=month)
    with zipfile.ZipFile(_download(url, CACHE_DIR / "ontime" / Path(url).name)) as archive:
        member = next(name for name in archive.namelist() if name.endswith(".csv"))
        with archive.open(member) as file:
            yield from csv.DictReader(io.TextIOWrapper(file, encoding="latin-1"))


def build_delays(months: list[Month]) -> int:
    stats: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for year, month in months:
        for row in _flight_rows(year, month):
            origin = stats[row["Origin"]]
            origin["flights"] += 1
            if row["CRSElapsedTime"]:
                haul = bisect.bisect_left(HAUL_EDGES_MIN, float(row["CRSElapsedTime"]))
                origin[HAUL_COLUMNS[haul]] += 1
            if float(row["Cancelled"]) == 1:
                origin["cancelled"] += 1
                continue
            origin["operated"] += 1
            if float(row["DepDel15"] or 0) == 1:
                origin["late"] += 1
            origin["delay_minutes"] += float(row["DepDelay"] or 0)
            # BTS assigns delay causes to the arrival airport, so they are summed under Dest.
            for cause in CAUSES:
                stats[row["Dest"]][cause] += float(row[cause] or 0)

    with open(DATA_DIR / "airport_delays.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "airport",
                "period",
                "flights",
                "late_departure_pct",
                "avg_departure_delay_min",
                "cancelled_pct",
            ]
            + [f"cause_{c.removesuffix('Delay').lower()}_pct" for c in CAUSES]
            + HAUL_COLUMNS
        )
        departing = {airport: s for airport, s in sorted(stats.items()) if s["flights"]}
        for airport, s in departing.items():
            cause_total = sum(s[c] for c in CAUSES) or 1
            writer.writerow(
                [
                    airport,
                    _period(months),
                    int(s["flights"]),
                    round(100 * s["late"] / max(s["operated"], 1), 1),
                    round(s["delay_minutes"] / max(s["operated"], 1), 1),
                    round(100 * s["cancelled"] / s["flights"], 1),
                ]
                + [round(100 * s[c] / cause_total, 1) for c in CAUSES]
                + [int(s[b]) for b in HAUL_COLUMNS]
            )
    return len(departing)


def _ourairports(name: str) -> Iterator[dict[str, str]]:
    with urllib.request.urlopen(OURAIRPORTS_URL.format(name=name), timeout=120) as response:
        yield from csv.DictReader(io.TextIOWrapper(response, encoding="utf-8"))


def build_airports() -> int:
    runways: dict[str, int] = defaultdict(int)
    for runway in _ourairports("runways"):
        if runway["closed"] == "0":
            runways[runway["airport_ident"]] += 1

    rows = [
        [
            a["iata_code"],
            a["name"],
            a["municipality"],
            a["iso_region"].removeprefix("US-"),
            a["latitude_deg"],
            a["longitude_deg"],
            a["type"],
            runways[a["ident"]],
        ]
        for a in _ourairports("airports")
        if a["iso_country"] == "US" and a["iata_code"] and a["scheduled_service"] == "yes"
    ]
    with open(DATA_DIR / "airports.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["iata", "name", "city", "state", "lat", "lon", "type", "runways"])
        writer.writerows(sorted(rows))
    return len(rows)


if __name__ == "__main__":
    months = _window(_newest_t100_month())
    period = _period(months)
    if _built_period() == period:
        print(f"Up to date: {period}")
        raise SystemExit
    DATA_DIR.mkdir(exist_ok=True)
    print(f"Building {period}")
    print(f"airport_traffic.csv: {build_traffic(months)} airports")
    print(f"airports.csv: {build_airports()} airports")
    print(f"airport_delays.csv: {build_delays(months)} airports")
