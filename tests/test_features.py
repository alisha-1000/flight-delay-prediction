import pytest


@pytest.mark.skip(reason="TODO: implement historical features")
def test_historical_rates_use_only_past_dates(tiny_flights):
    """TODO: the first date per key must have NaN history; changing a future label must not change past features."""


@pytest.mark.skip(reason="TODO: implement cyclic encoding")
def test_cyclic_encoding_wraps(tiny_flights):
    """TODO: hour 23 and hour 0 should be close in (sin, cos) space."""
