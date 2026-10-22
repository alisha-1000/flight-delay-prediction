"""Single source of truth for columns that must never be used as features."""

# Known only after departure / arrival.
POST_DEPARTURE_COLUMNS: frozenset[str] = frozenset(
    {"dep_time", "dep_delay", "arr_time", "arr_delay", "air_time"}
)


def assert_no_leakage(columns) -> None:
    """Raise if any post-departure column is present in a feature matrix."""
    leaked = POST_DEPARTURE_COLUMNS.intersection(columns)
    if leaked:
        raise ValueError(f"Leaky columns in features: {sorted(leaked)}")
