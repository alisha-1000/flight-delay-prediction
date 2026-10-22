"""Column roles for the raw flights table, relative to the pre-departure decision time.

The post-departure set is imported from ``features.leakage`` so there is a single source
of truth for columns that must never become model inputs.
"""

from __future__ import annotations

import pandas as pd

from flight_delay.features.leakage import POST_DEPARTURE_COLUMNS

# Row identifier with no predictive meaning (not sorted by date).
IDENTIFIER_COLUMNS: frozenset[str] = frozenset({"id"})

# Raw column used only to build the target; it is also post-departure.
TARGET_SOURCE_COLUMN = "arr_delay"
TARGET_COLUMN = "is_delayed"

# Known from the published schedule before departure.
PRE_DEPARTURE_COLUMNS: frozenset[str] = frozenset(
    {
        "year",
        "month",
        "day",
        "sched_dep_time",
        "sched_arr_time",
        "hour",
        "minute",
        "time_hour",
        "carrier",
        "name",
        "flight",
        "origin",
        "dest",
        "distance",
    }
)

# Pre-departure in principle, but with caveats documented in docs/data_dictionary.md:
# tailnum — aircraft swaps can happen close to departure, and in this dataset it is
# missing *only* for cancelled flights, so its missingness encodes the outcome.
CAUTION_COLUMNS: frozenset[str] = frozenset({"tailnum"})

# Columns added by load_raw (derived from pre-departure columns only).
DERIVED_PRE_DEPARTURE_COLUMNS: frozenset[str] = frozenset({"date", "sched_dep_dt"})

ALL_RAW_COLUMNS = (
    IDENTIFIER_COLUMNS | PRE_DEPARTURE_COLUMNS | CAUTION_COLUMNS | POST_DEPARTURE_COLUMNS
)


def column_roles() -> pd.DataFrame:
    """Table of every raw column and its role (useful for documentation / notebooks)."""
    rows = []
    for col in sorted(ALL_RAW_COLUMNS):
        if col in POST_DEPARTURE_COLUMNS:
            role = (
                "target source (post-departure)"
                if col == TARGET_SOURCE_COLUMN
                else "post-departure"
            )
        elif col in IDENTIFIER_COLUMNS:
            role = "identifier"
        elif col in CAUTION_COLUMNS:
            role = "pre-departure (caution)"
        else:
            role = "pre-departure"
        rows.append(
            {"column": col, "role": role, "allowed_as_feature": role == "pre-departure"}
        )
    return pd.DataFrame(rows)


def pre_departure_view(
    df: pd.DataFrame, keep_target: bool = True, keep_caution: bool = False
) -> pd.DataFrame:
    """Return a copy with post-departure and identifier columns removed.

    Only pre-departure columns (and, optionally, the target and caution columns) are kept.
    """
    allowed = PRE_DEPARTURE_COLUMNS | DERIVED_PRE_DEPARTURE_COLUMNS
    if keep_caution:
        allowed = allowed | CAUTION_COLUMNS
    cols = [c for c in df.columns if c in allowed]
    if keep_target and TARGET_COLUMN in df.columns:
        cols.append(TARGET_COLUMN)
    out = df[cols].copy()
    leaked = POST_DEPARTURE_COLUMNS.intersection(out.columns)
    assert not leaked, f"post-departure columns leaked: {sorted(leaked)}"
    return out
