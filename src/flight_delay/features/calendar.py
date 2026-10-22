"""Calendar and cyclic time features."""

import pandas as pd


def add_calendar_features(df: pd.DataFrame) -> pd.DataFrame:
    """TODO: day_of_week, month, week_of_year, is_weekend, US holiday proximity."""
    raise NotImplementedError


def add_cyclic_encoding(df: pd.DataFrame, col: str, period: int) -> pd.DataFrame:
    """TODO: add `{col}_sin`, `{col}_cos` = sin/cos(2*pi*x/period)."""
    raise NotImplementedError
