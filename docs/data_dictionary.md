# Data Dictionary

TODO: verify every column against the downloaded file.

| Column | Type | Description | Known at decision time? | Use |
|---|---|---|---|---|
| year, month, day | int | Flight date | Yes | Calendar features |
| sched_dep_time | int (HHMM) | Scheduled departure | Yes | Schedule features |
| sched_arr_time | int (HHMM) | Scheduled arrival | Yes | Schedule features |
| carrier | str | Airline code | Yes | Categorical |
| flight | int | Flight number | Yes | TODO decide |
| tailnum | str | Aircraft tail number | Partly (assignment may change) | TODO decide |
| origin, dest | str | Airports | Yes | Route / congestion |
| distance | float | Route distance (miles) | Yes | Numeric |
| dep_time | int | Actual departure | **No** | Drop |
| dep_delay | float | Departure delay | **No** | Drop |
| arr_time | int | Actual arrival | **No** | Drop |
| arr_delay | float | Arrival delay (min) | **No** | Target source only |
| air_time | float | Actual airborne time | **No** | Drop |

## Data quality checks (TODO in `notebooks/01_data_quality.ipynb`)
- [ ] Missing values per column (cancelled flights → missing actuals)
- [ ] Duplicates
- [ ] Impossible values / outliers
- [ ] Class balance of target
- [ ] Date coverage and gaps
