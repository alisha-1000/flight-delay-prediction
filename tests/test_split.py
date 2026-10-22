import pytest


@pytest.mark.skip(reason="TODO: implement chronological_split")
def test_split_is_chronological_and_disjoint(tiny_flights):
    """TODO: max(train.date) < min(valid.date) < min(test.date); no row in two splits."""
