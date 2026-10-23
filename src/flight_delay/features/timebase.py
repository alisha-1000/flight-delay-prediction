"""Put local clock times at origin and destination on a common time basis (UTC).

The raw data gives departure times in origin local time and arrival times in destination local
time, as HHMM clock values with no arrival date. Arrivals are placed on a common basis by:

1. localising the arrival clock time on dates D-1, D and D+1 in the destination's IANA zone
   (DST aware);
2. taking the candidate with the smallest non-negative duration after departure.

Every flight in the data is shorter than 24 h (longest scheduled block: 700 min), so exactly one
candidate qualifies. That handles overnight arrivals and DST switch days. Airports missing from
``AIRPORT_TZ`` yield NaN.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from flight_delay.data.load import hhmm_to_minutes
from flight_delay.features.airport_timezones import AIRPORT_TZ

NY_TZ = "America/New_York"


def localize_to_utc(local_naive: pd.Series, airports: pd.Series) -> pd.Series:
    """Naive local datetimes at each airport -> UTC (NaT if the airport's zone is unknown)."""
    zones = airports.astype(str).map(AIRPORT_TZ)
    out = pd.Series(pd.NaT, index=local_naive.index, dtype="datetime64[ns, UTC]")
    for tz, idx in zones.dropna().groupby(zones.dropna()).groups.items():
        loc = pd.DatetimeIndex(local_naive.loc[idx]).tz_localize(
            tz, ambiguous=False, nonexistent="shift_forward"
        )
        out.loc[idx] = loc.tz_convert("UTC")
    return out


def arrival_utc(
    dep_utc: pd.Series, dep_local_date: pd.Series, arr_hhmm: pd.Series, dest: pd.Series
) -> pd.Series:
    """UTC arrival for an arrival clock time (dest local, no date) following ``dep_utc``."""
    arr_min = pd.to_timedelta(hhmm_to_minutes(arr_hhmm) % 1440, unit="m")
    best = pd.Series(pd.NaT, index=dep_utc.index, dtype="datetime64[ns, UTC]")
    best_dur = pd.Series(np.inf, index=dep_utc.index)
    for shift in (-1, 0, 1):
        cand = localize_to_utc(dep_local_date + pd.Timedelta(days=shift) + arr_min, dest)
        dur = (cand - dep_utc).dt.total_seconds()
        take = (dur >= 0) & (dur < best_dur)
        best = best.mask(take, cand)
        best_dur = best_dur.mask(take, dur)
    return best


def scheduled_block_minutes(df: pd.DataFrame) -> pd.Series:
    """Scheduled gate-to-gate time in minutes on a common (UTC) basis. Schedule-only inputs."""
    dep_utc = localize_to_utc(df["sched_dep_dt"], df["origin"])
    arr = arrival_utc(dep_utc, df["date"], df["sched_arr_time"], df["dest"])
    return (arr - dep_utc).dt.total_seconds() / 60


def actual_arrival_ny(df: pd.DataFrame) -> pd.Series:
    """Actual arrival as a naive New York local datetime.

    Uses post-departure fields, so it may only be used to time when PAST flights' outcomes
    became known, never as a feature.
    """
    dep_local = df["sched_dep_dt"] + pd.to_timedelta(df["dep_delay"], unit="m")
    dep_utc = localize_to_utc(dep_local, df["origin"])
    arr = arrival_utc(dep_utc, dep_local.dt.normalize(), df["arr_time"], df["dest"])
    return arr.dt.tz_convert(NY_TZ).dt.tz_localize(None)
