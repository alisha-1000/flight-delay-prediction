"""Schedule features derived from planned times only."""

from __future__ import annotations

import pandas as pd

from flight_delay.data.load import hhmm_to_minutes
from flight_delay.features.timebase import scheduled_block_minutes

# Departure time-of-day buckets (scheduled local hour, inclusive lower bound).
DEP_BUCKETS = [
    (0, "night"),
    (5, "early_morning"),
    (9, "midday"),
    (14, "afternoon"),
    (18, "evening"),
    (22, "night"),
]


def dep_bucket(hour: pd.Series) -> pd.Series:
    """Map scheduled departure hour (0-23) to a coarse time-of-day bucket."""
    edges = [b for b, _ in DEP_BUCKETS] + [24]
    labels = [name for _, name in DEP_BUCKETS]
    return pd.cut(hour, bins=edges, right=False, labels=labels, ordered=False).astype(str)


def add_schedule_features(df: pd.DataFrame) -> pd.DataFrame:
    """Scheduled departure/arrival minutes, scheduled block time, overnight flag, bucket.

    ``sched_block_min`` is the scheduled gate-to-gate duration on a common UTC time basis. It
    converts the origin-local departure and destination-local arrival with each airport's IANA
    time zone (DST aware) and resolves the missing arrival date (see ``timebase.py``). It uses
    only the published schedule and static airport time zones. The earlier local-clock
    difference was not a duration: it mixed block time with the destination's time-zone offset.
    """
    out = df.copy()
    dep = hhmm_to_minutes(out["sched_dep_time"])
    arr = hhmm_to_minutes(out["sched_arr_time"])
    out["sched_dep_min"] = dep.astype("int16")
    out["sched_arr_min"] = (arr % 1440).astype("int16")  # destination local clock
    out["sched_block_min"] = scheduled_block_minutes(out)
    # Clock rule; verified to match the true local arrival date for every row (notebook 03).
    out["overnight_arrival"] = (arr < dep).astype("int8")
    out["dep_bucket"] = dep_bucket(out["hour"].astype(int))
    return out
