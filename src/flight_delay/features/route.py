"""Route, carrier and interaction categorical features."""

from __future__ import annotations

import numpy as np
import pandas as pd


def add_route_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add a route id and categorical crosses between carrier, airports and departure time.

    Cross features let additive models (Logistic Regression) represent the interactions seen
    in the EDA, such as the carrier x origin heatmap. Rare and unseen levels are collapsed
    later by ``FeatureEncoder``, which is fitted on the training split only.
    """
    out = df.copy()
    carrier, origin, dest = (out[c].astype(str) for c in ("carrier", "origin", "dest"))
    out["route"] = origin + "-" + dest
    out["carrier_origin"] = carrier + "|" + origin
    out["carrier_dest"] = carrier + "|" + dest
    out["carrier_route"] = carrier + "|" + out["route"]
    if "dep_bucket" not in out:
        raise KeyError("add_schedule_features() must run before add_route_features()")
    out["origin_dep_bucket"] = origin + "|" + out["dep_bucket"]
    out["carrier_dep_bucket"] = carrier + "|" + out["dep_bucket"]
    out["log_distance"] = np.log(out["distance"].astype(float).clip(lower=1))
    return out
