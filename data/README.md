# Data

| Folder | Contents | Committed? |
|---|---|---|
| `raw/` | Original immutable download | No |
| `interim/` | Cleaned, typed, target added | No |
| `processed/` | Feature matrices per split | No |
| `external/` | Supplementary data (e.g., BTS, airport metadata) | No |

## Download

TODO: fill in exact Kaggle slug and file name.

```bash
# requires ~/.kaggle/kaggle.json
kaggle datasets download -d <owner>/<dataset> -p data/raw --unzip
```

## Provenance

- Source: Kaggle *Flights* dataset (2013 US flights).
- Extension: US Bureau of Transportation Statistics, Airline On-Time Performance.
- TODO: record download date, file hash, row count.
