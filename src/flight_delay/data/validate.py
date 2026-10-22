"""Data-quality checks for the raw flights table.

Every function is read-only: it reports problems and never mutates the input.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from flight_delay.data.load import RAW_COLUMNS, hhmm_to_minutes

TIME_COLUMNS = ["dep_time", "sched_dep_time", "arr_time", "sched_arr_time"]
NATURAL_KEY = ["year", "month", "day", "carrier", "flight", "origin", "sched_dep_time"]


def validate_schema(df: pd.DataFrame) -> list[str]:
    """Return a list of schema problems (empty list means the schema is as expected)."""
    problems = []
    missing = set(RAW_COLUMNS) - set(df.columns)
    if missing:
        problems.append(f"missing columns: {sorted(missing)}")
    extra = set(df.columns) - set(RAW_COLUMNS) - {"date", "sched_dep_dt"}
    if extra:
        problems.append(f"unexpected columns: {sorted(extra)}")
    for col in ["year", "month", "day", "sched_dep_time", "sched_arr_time", "distance"]:
        if col in df and not pd.api.types.is_integer_dtype(df[col]):
            problems.append(f"{col} should be integer, got {df[col].dtype}")
    return problems


def missing_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Count and percentage of missing values per column, sorted descending."""
    n = df.isna().sum()
    out = pd.DataFrame({"n_missing": n, "pct_missing": (100 * n / len(df)).round(3)})
    return out.sort_values("n_missing", ascending=False)


def missing_patterns(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """Co-occurrence of missingness across ``cols`` (True = missing)."""
    pattern = df[cols].isna()
    return pattern.value_counts().rename("n_rows").reset_index()


def duplicate_summary(df: pd.DataFrame, key: list[str] | None = None) -> dict[str, int]:
    """Exact duplicate rows (ignoring ``id``) and duplicates on the natural flight key."""
    key = key or NATURAL_KEY
    content = [c for c in df.columns if c != "id"]
    return {
        "exact_duplicate_rows": int(df.duplicated(subset=content).sum()),
        "duplicate_natural_key": int(df.duplicated(subset=key).sum()),
        "duplicate_id": int(df["id"].duplicated().sum()) if "id" in df else 0,
    }


def _valid_hhmm(s: pd.Series) -> pd.Series:
    """True where an HHMM value is well-formed (0..2400, minutes < 60) or missing."""
    s = pd.to_numeric(s, errors="coerce")
    ok = s.between(0, 2400) & ((s % 100) < 60)
    return ok | s.isna()


def _clock_diff_matches(actual_hhmm, sched_hhmm, delay) -> pd.Series:
    """True where ``delay`` agrees with actual - scheduled clock time (mod 24 h).

    The modulo allows for flights that depart / arrive after midnight. Missing -> True.
    """
    diff = hhmm_to_minutes(actual_hhmm) - hhmm_to_minutes(sched_hhmm) - delay
    ok = (diff % 1440) == 0
    return ok | diff.isna()


def invalid_value_report(df: pd.DataFrame) -> pd.DataFrame:
    """Run rule-based validity checks; one row per rule with the number of violations.

    ``kind`` is ``error`` for impossible / inconsistent values and ``info`` for values
    that are plausible but unusual and worth knowing about.
    """
    n = len(df)
    checks: list[tuple[str, str, pd.Series]] = []

    for col in TIME_COLUMNS:
        checks.append((f"{col}: malformed HHMM", "error", ~_valid_hhmm(df[col])))

    checks += [
        ("month not in 1..12", "error", ~df["month"].between(1, 12)),
        (
            "invalid calendar date",
            "error",
            pd.to_datetime(
                dict(year=df["year"], month=df["month"], day=df["day"]), errors="coerce"
            ).isna(),
        ),
        (
            "hour/minute != sched_dep_time",
            "error",
            (df["hour"].astype(int) * 100 + df["minute"].astype(int)) != df["sched_dep_time"],
        ),
        ("distance <= 0", "error", df["distance"] <= 0),
        ("air_time <= 0", "error", df["air_time"] <= 0),
        ("origin == dest", "error", df["origin"] == df["dest"]),
        (
            "dep_delay inconsistent with dep_time - sched_dep_time",
            "error",
            ~_clock_diff_matches(df["dep_time"], df["sched_dep_time"], df["dep_delay"]),
        ),
        (
            "arr_delay inconsistent with arr_time - sched_arr_time",
            "error",
            ~_clock_diff_matches(df["arr_time"], df["sched_arr_time"], df["arr_delay"]),
        ),
        (
            "dep_time missing but arrival recorded",
            "error",
            df["dep_time"].isna() & (df["arr_time"].notna() | df["arr_delay"].notna()),
        ),
        (
            "arr_time recorded but arr_delay missing",
            "info",
            df["arr_time"].notna() & df["arr_delay"].isna(),
        ),
        ("dep_time == 2400 (midnight encoding)", "info", df["dep_time"] == 2400),
        ("arr_time == 2400 (midnight encoding)", "info", df["arr_time"] == 2400),
        ("dep_delay > 12 h", "info", df["dep_delay"] > 720),
        ("arr_delay > 10 h", "info", df["arr_delay"] > 600),
        ("arr_delay < -60 min (> 1 h early)", "info", df["arr_delay"] < -60),
    ]

    speed_mph = df["distance"] / (df["air_time"] / 60)
    checks += [
        ("implied speed < 150 mph", "info", speed_mph < 150),
        ("implied speed > 650 mph", "info", speed_mph > 650),
    ]

    route_dist = df.groupby(["origin", "dest"])["distance"].transform("nunique")
    checks.append(("route has >1 distinct distance", "info", route_dist > 1))

    name_per_carrier = df.groupby("carrier")["name"].transform("nunique")
    checks.append(("carrier code maps to >1 name", "error", name_per_carrier > 1))

    rows = [
        {
            "check": name,
            "kind": kind,
            "n_violations": int(mask.fillna(False).sum()),
            "pct": round(100 * float(mask.fillna(False).sum()) / n, 4),
        }
        for name, kind, mask in checks
    ]
    return pd.DataFrame(rows)


def class_balance(y: pd.Series) -> pd.DataFrame:
    """Counts and shares of each label, including missing labels."""
    counts = y.value_counts(dropna=False)
    out = pd.DataFrame({"n": counts, "share": (counts / counts.sum()).round(4)})
    out.index = out.index.map(lambda v: "missing" if pd.isna(v) else v)
    return out


def wilson_interval(k: np.ndarray, n: np.ndarray, z: float = 1.96) -> tuple[np.ndarray, np.ndarray]:
    """95% Wilson score interval for a binomial proportion k/n (vectorised)."""
    k = np.asarray(k, dtype=float)
    n = np.asarray(n, dtype=float)
    p = np.divide(k, n, out=np.zeros_like(k), where=n > 0)
    denom = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / denom
    half = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
    return centre - half, centre + half


def rate_table(
    df: pd.DataFrame, by: str | list[str], target: str = "is_delayed", min_n: int = 1
) -> pd.DataFrame:
    """Delay rate per group with sample size and 95% Wilson interval.

    ``n`` counts only rows with a non-missing label, so rows whose target is missing
    (e.g. cancelled flights before a missing-label policy is applied) do not dilute the rate.
    Groups with no labelled rows are dropped.
    """
    g = df.groupby(by, observed=True)[target].agg(n="count", n_delayed="sum")
    g = g[g["n"] >= max(min_n, 1)].copy()
    g["delay_rate"] = g["n_delayed"] / g["n"]
    g["ci_low"], g["ci_high"] = wilson_interval(g["n_delayed"].to_numpy(), g["n"].to_numpy())
    return g
