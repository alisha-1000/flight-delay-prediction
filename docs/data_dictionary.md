# Data Dictionary

Source: Kaggle *Flights* dataset — all flights departing New York City airports (EWR, JFK, LGA)
in 2013 (the `nycflights13` table). File `data/raw/flights.csv`, 336,776 rows × 21 columns,
SHA-256 `8bdc6abbf07ac0cbb1036bc14a787cab3eea616be46c31899d2d8048963b08aa`.

Column roles are defined in code in `src/flight_delay/data/schema.py`; the post-departure list
is imported from `src/flight_delay/features/leakage.py`. Evidence for every statement below is in
`notebooks/01_data_quality.ipynb`.

## Columns

Times are local clock times in `HHMM` integer format (`2400` = midnight). "Known at decision
time" assumes the decision is made **before departure**.

| Column | dtype | Description | Missing | Known at decision time? | Role |
|---|---|---|---|---|---|
| `id` | int64 | Row identifier, 0–336,775; **not** in date order | 0 | — | Identifier, not a feature |
| `year` | int16 | Year (always 2013) | 0 | Yes | Pre-departure (constant) |
| `month` | int8 | Month 1–12 | 0 | Yes | Pre-departure |
| `day` | int8 | Day of month | 0 | Yes | Pre-departure |
| `dep_time` | float64 | Actual departure time | 8,255 (2.45%) | **No** | Post-departure — drop |
| `sched_dep_time` | int16 | Scheduled departure time | 0 | Yes | Pre-departure |
| `dep_delay` | float64 | Departure delay, minutes (negative = early) | 8,255 | **No** | Post-departure — drop |
| `arr_time` | float64 | Actual arrival time (destination local) | 8,713 (2.59%) | **No** | Post-departure — drop |
| `sched_arr_time` | int16 | Scheduled arrival time (destination local) | 0 | Yes | Pre-departure |
| `arr_delay` | float64 | Arrival delay, minutes (negative = early) | 9,430 (2.80%) | **No** | Target source only |
| `carrier` | string | Two-letter airline code (16 values) | 0 | Yes | Pre-departure |
| `flight` | int32 | Flight number (3,844 values) | 0 | Yes | Pre-departure |
| `tailnum` | string | Aircraft registration (4,043 values) | 2,512 (0.75%) | Usually, but swaps occur | **Caution** — see below |
| `origin` | string | Origin airport: EWR, JFK, LGA | 0 | Yes | Pre-departure |
| `dest` | string | Destination airport (105 values) | 0 | Yes | Pre-departure |
| `air_time` | float64 | Minutes airborne | 9,430 | **No** | Post-departure — drop |
| `distance` | int32 | Route distance, miles (17–4,983) | 0 | Yes | Pre-departure |
| `hour` | int8 | Scheduled departure hour (= `sched_dep_time // 100`) | 0 | Yes | Pre-departure (redundant) |
| `minute` | int8 | Scheduled departure minute (= `sched_dep_time % 100`) | 0 | Yes | Pre-departure (redundant) |
| `time_hour` | datetime | Scheduled departure date + hour | 0 | Yes | Pre-departure (redundant) |
| `name` | string | Carrier full name; exactly one per `carrier` | 0 | Yes | Pre-departure (redundant) |

Derived by `load_raw`: `date` (flight date) and `sched_dep_dt` (scheduled departure as a local
datetime). Both are built from pre-departure fields only.

## Target

`is_delayed = 1` if `arr_delay >= 15` else `0`. This follows the BTS on-time definition and is
implemented in `clean.add_target`.

| | Flights | Share |
|---|---|---|
| Labelled, on time (`0`) | 247,246 | 73.4% |
| Labelled, delayed (`1`) | 80,100 | 23.8% |
| No `arr_delay` (label missing) | 9,430 | 2.8% |

Flights with no `arr_delay` are resolved by `clean.handle_cancelled`. The policy is set by
`target.cancelled_policy` in `configs/config.yaml`:

- `exclude` (default): 327,346 flights remain, with a positive rate of **24.5%** (3.1 : 1).
- `delayed`: 336,776 flights, with a positive rate of 26.6% (2.8 : 1).

Positive rate by configured chronological split (`exclude`): train 26.4%, **valid 15.7%**, test 25.8%.

## Flight status (inferred, `clean.add_flight_status`)

The source has no cancelled or diverted flags, so status is inferred from which fields are missing.

| Status | Rule | Flights |
|---|---|---|
| `completed` | `arr_delay` present | 327,346 |
| `cancelled` | `dep_time` missing (all actual-time fields missing) | 8,255 |
| `departed_no_arrival_delay` | departed, `arr_delay` missing; probably diverted (assumption) | 1,175 |

## Data-quality summary

Implemented in `src/flight_delay/data/validate.py`:

- **Duplicates:** 0 exact, 0 on (date, carrier, flight, origin, sched_dep_time), 0 duplicate ids.
- **Invalid values:** 0 error-level violations. HHMM formats are valid; `hour`/`minute`/`time_hour`
  agree with `sched_dep_time`; `dep_delay` and `arr_delay` match actual − scheduled time modulo 24 h.
- **Unusual but valid:** 29 next-day departures (`dep_delay` > 12 h, max 1,301 min); 39 arrivals
  more than 10 h late; 199 arrivals more than 1 h early; 352 flights with implied speed < 150 mph
  and 2 with > 650 mph; EWR→EGE and JFK→EGE each list two distances 1 mile apart; one cancelled
  EWR→LGA record (17 mi).
- **Missingness is structured:** all actual-time fields are missing together for cancellations;
  `tailnum` is missing only for cancelled flights (2,512 of 8,255).

## Leakage notes

- `dep_time`, `dep_delay`, `arr_time`, `air_time` and `arr_delay` are unknown before departure.
  `dep_delay` alone gives a single-feature ROC AUC of 0.895 against the target.
- `schema.pre_departure_view()` removes them and also drops `id` and `tailnum`. `assert_no_leakage`
  is called on its output.
- `tailnum`: aircraft assignment can change close to departure, and in this file its missingness
  perfectly identifies a subset of cancellations. It is excluded by default (`keep_caution=False`).
  If it is used, it should only be through past-date aggregates.
- Any aggregate (carrier, airport or route delay rates) must be computed from strictly earlier dates.

## Known limitations

- Departures from three NYC airports in a single year only. There is no weather, aircraft-type
  or crew data.
- Times are local, and there is no time-zone column. Scheduled block time cannot be derived from
  `sched_dep_time` and `sched_arr_time` without external airport time-zone data.
- Cancelled and diverted status is inferred, not given.
