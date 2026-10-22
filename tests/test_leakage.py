import pytest

from flight_delay.features.leakage import POST_DEPARTURE_COLUMNS, assert_no_leakage


def test_assert_no_leakage_rejects_post_departure_columns():
    with pytest.raises(ValueError):
        assert_no_leakage(["carrier", "dep_delay"])


def test_assert_no_leakage_accepts_clean_columns():
    assert_no_leakage(["carrier", "origin", "sched_dep_time"])


@pytest.mark.skip(reason="TODO: enable once build_features is implemented")
def test_feature_matrix_has_no_post_departure_columns(tiny_flights):
    from flight_delay.features.build import build_features

    X = build_features(tiny_flights, config={})
    assert not POST_DEPARTURE_COLUMNS.intersection(X.columns)
