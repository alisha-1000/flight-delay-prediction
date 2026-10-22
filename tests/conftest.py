"""Shared fixtures."""

import pandas as pd
import pytest


@pytest.fixture
def tiny_flights() -> pd.DataFrame:
    """TODO: small synthetic frame spanning several dates/carriers/airports for unit tests."""
    return pd.DataFrame(
        {
            "date": pd.to_datetime(["2013-01-01", "2013-01-02", "2013-01-03"]),
            "carrier": ["UA", "AA", "UA"],
            "origin": ["JFK", "LGA", "EWR"],
            "dest": ["LAX", "ORD", "LAX"],
            "sched_dep_time": [600, 1230, 1945],
            "arr_delay": [-5.0, 30.0, 12.0],
        }
    )
