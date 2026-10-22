"""Chronological train / validation / test split."""

import pandas as pd


def chronological_split(
    df: pd.DataFrame, date_col: str, ranges: dict[str, tuple[str, str]]
) -> dict[str, pd.DataFrame]:
    """Split by inclusive date ranges, e.g. {"train": ("2013-01-01", "2013-08-31"), ...}.

    TODO: implement; assert ranges are ordered and non-overlapping.
    """
    raise NotImplementedError
