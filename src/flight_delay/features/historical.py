"""Historical delay statistics using strictly past dates."""

import pandas as pd


def add_historical_delay_rates(
    df: pd.DataFrame, keys: list[str], windows_days: list[int]
) -> pd.DataFrame:
    """Rolling delay rate per key (carrier, origin, dest, route) over previous N days.

    TODO: aggregate to daily level, shift by one day, then roll — never include the current date.
    """
    raise NotImplementedError
