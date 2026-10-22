# Leakage Policy

The model must not use post-departure information when making pre-departure predictions.

## 1. Decision time
TODO: state the chosen prediction timestamp (see `configs/config.yaml → decision_time`).

## 2. Rules
1. Drop all actual-outcome columns: `dep_time`, `dep_delay`, `arr_time`, `arr_delay` (except to build the target), `air_time`.
2. Historical aggregates (carrier/route/airport delay rates, congestion) use **strictly earlier dates** than the flight's date (`shift` before rolling).
3. Encoders / scalers / target encodings are fit on the **training split only**.
4. Split chronologically; validation and test are later in time than training.
5. Same-day congestion uses only **scheduled** counts, never realised delays.

## 3. Enforcement
- `src/flight_delay/features/leakage.py` holds the allow-list / deny-list.
- `tests/test_leakage.py` asserts no denied column reaches the feature matrix.
