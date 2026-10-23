"""Airport congestion from the published *schedule* (never realised delays).

Counts must be computed on the FULL raw table, before the missing-label policy drops
cancelled flights and flights without an arrival-delay record: those flights were still in the
schedule known before departure. This is the same definition as in notebooks/02_eda.ipynb.
"""

from __future__ import annotations

import pandas as pd

# (feature name, grouping keys)
CONGESTION_SLOTS: dict[str, list[str]] = {
    "sched_dep_origin_hour": ["origin", "date", "hour"],  # same origin, date, scheduled hour
    "sched_dep_origin_day": ["origin", "date"],
    "sched_dep_carrier_origin_day": ["carrier", "origin", "date"],
}


def add_congestion_features(raw: pd.DataFrame) -> pd.DataFrame:
    """Add scheduled-departure counts per slot. Call on the raw table, before any row filtering."""
    out = raw.copy()
    for name, keys in CONGESTION_SLOTS.items():
        out[name] = out.groupby(keys, observed=True)["id"].transform("size").astype("int32")
    out["sched_dep_origin_hour_share"] = (
        out["sched_dep_origin_hour"] / out["sched_dep_origin_day"]
    ).astype("float32")
    return out
