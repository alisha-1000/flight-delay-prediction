"""Cleaning and target construction."""

import pandas as pd


def handle_cancelled(df: pd.DataFrame, policy: str = "exclude") -> pd.DataFrame:
    """TODO: cancelled/diverted flights (missing arr_delay) — exclude or label as delayed."""
    raise NotImplementedError


def add_target(df: pd.DataFrame, threshold_minutes: int = 15) -> pd.DataFrame:
    """TODO: add `is_delayed = (arr_delay >= threshold_minutes)`."""
    raise NotImplementedError
