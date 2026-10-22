"""Assemble the full feature matrix."""

import pandas as pd


def build_features(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """TODO: chain calendar, schedule, route, congestion and historical features,
    then call `assert_no_leakage` on the result."""
    raise NotImplementedError
