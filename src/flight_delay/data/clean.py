"""Flight status, target construction and handling of flights without an arrival delay."""

from __future__ import annotations

import pandas as pd

from flight_delay.data.schema import TARGET_COLUMN, TARGET_SOURCE_COLUMN

# Flight outcome categories derived from which actual-time fields are present.
COMPLETED = "completed"
CANCELLED = "cancelled"  # no actual departure time
NO_ARRIVAL_RECORD = "departed_no_arrival_delay"  # departed, but arr_delay missing (likely diverted)

CANCELLED_POLICIES = ("exclude", "delayed")


def add_flight_status(df: pd.DataFrame) -> pd.DataFrame:
    """Add a categorical ``flight_status`` column.

    The dataset has no explicit cancelled / diverted flags, so status is inferred:

    * ``cancelled`` — ``dep_time`` is missing.
    * ``departed_no_arrival_delay`` — departed but ``arr_delay`` is missing. These are most
      likely diversions, but the dataset does not say so; treat the label as an assumption.
    * ``completed`` — ``arr_delay`` is present.
    """
    out = df.copy()
    status = pd.Series(COMPLETED, index=out.index)
    status[out["arr_delay"].isna()] = NO_ARRIVAL_RECORD
    status[out["dep_time"].isna()] = CANCELLED
    out["flight_status"] = pd.Categorical(
        status, categories=[COMPLETED, CANCELLED, NO_ARRIVAL_RECORD]
    )
    return out


def add_target(df: pd.DataFrame, threshold_minutes: int = 15) -> pd.DataFrame:
    """Add ``is_delayed`` = 1 if ``arr_delay >= threshold_minutes`` else 0.

    The 15-minute default follows the US BTS on-time definition (a flight is on time if it
    arrives less than 15 minutes after schedule). Rows with missing ``arr_delay`` get a
    missing label (``<NA>``); decide what to do with them via :func:`handle_cancelled`.
    """
    out = df.copy()
    delay = out[TARGET_SOURCE_COLUMN]
    out[TARGET_COLUMN] = (delay >= threshold_minutes).astype("Int8").mask(delay.isna())
    return out


def handle_cancelled(df: pd.DataFrame, policy: str = "exclude") -> pd.DataFrame:
    """Resolve rows whose target is missing (cancelled or no arrival record).

    * ``exclude`` (default, matches ``configs/config.yaml``): drop them. The model then
      predicts "arrival delay >= 15 min *given that the flight operates and arrives*".
    * ``delayed``: keep them and label them 1, i.e. treat any disruption as a bad outcome.
    """
    if policy not in CANCELLED_POLICIES:
        raise ValueError(f"policy must be one of {CANCELLED_POLICIES}, got {policy!r}")
    if TARGET_COLUMN not in df:
        raise KeyError("call add_target() before handle_cancelled()")
    missing = df[TARGET_COLUMN].isna()
    if policy == "exclude":
        return df.loc[~missing].copy()
    out = df.copy()
    out.loc[missing, TARGET_COLUMN] = 1
    return out


def build_labelled_frame(
    df: pd.DataFrame, threshold_minutes: int = 15, policy: str = "exclude"
) -> pd.DataFrame:
    """Convenience: status -> target -> missing-label policy, in that order."""
    return handle_cancelled(add_target(add_flight_status(df), threshold_minutes), policy)
