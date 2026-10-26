"""Reads the committed data tables, built by scripts/build_snapshots.py (D-020)."""

import csv
from functools import cache
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[2] / "data"


@cache
def read_table(name: str) -> dict[str, dict[str, str]]:
    """Rows of `data/<name>.csv`, keyed by airport code. Read once per process."""
    with open(DATA_DIR / f"{name}.csv", newline="") as file:
        return {row.get("iata") or row["airport"]: row for row in csv.DictReader(file)}
