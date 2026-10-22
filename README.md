# Flight Delay Prediction via Gradient Boosting and Temporal Deep Learning

> **Project 21 — Phase 1 (Machine Learning).** Predict whether a flight will **arrive ≥ 15 minutes late**
> using only information available **before departure**, with calibrated probabilities.

## Status

Phase 1 scaffold. Modules contain stubs and TODOs; no model is implemented yet.

| Phase 1 criterion | Where it lives |
|---|---|
| Literature Review | `docs/literature_review.md`, `report/references.bib` |
| Dataset Quality & EDA | `notebooks/01_data_quality.ipynb`, `notebooks/02_eda.ipynb`, `docs/data_dictionary.md` |
| Feature Engineering | `src/flight_delay/features/`, `docs/leakage_policy.md` |
| Theoretical Rigor | `docs/methodology.md`, `report/sections/` |
| Model Application | `src/flight_delay/models/` (Logistic Regression, XGBoost, calibration) |
| Evaluation | `src/flight_delay/evaluation/` (PR AUC, ROC AUC, recall@precision, calibration) |
| GitHub Repo & Code Quality | `tests/`, `pyproject.toml` (ruff + pytest config) |
| Project Presentation | `presentation/` |
| Project Report (IEEE) | `report/` (IEEEtran LaTeX) |

## Problem definition

- **Target:** `is_delayed = 1` if arrival delay ≥ 15 min (BTS on-time convention), else 0. Cancelled/diverted flights: TODO decide (exclude vs. treat as delayed) and document.
- **Decision time:** TODO fix in `configs/config.yaml` (default suggestion: end of day D-1). Every feature must be computable at that moment — see `docs/leakage_policy.md`.
- **Split:** chronological by date (train → validation → test). No random shuffling.
- **Metrics:** PR AUC (primary, class-imbalanced), ROC AUC, recall at a chosen operational precision, Brier score, ECE and reliability diagrams.

## Dataset

Kaggle *Flights* dataset (2013 US flights departing NYC). Larger extension: BTS Airline On-Time Performance.
Raw data is **not** committed. See `data/README.md` for download instructions.

## Repository layout

```
configs/            experiment configuration (paths, decision time, split dates, target threshold)
data/               raw / interim / processed data (git-ignored contents)
docs/               literature review, data dictionary, leakage policy, methodology
notebooks/          numbered exploratory notebooks (EDA, feature checks, model results)
src/flight_delay/   importable package: data, features, models, evaluation, utils
scripts/            CLI entry points that chain the pipeline
tests/              pytest suite (leakage, split, features, metrics)
models/             trained model artifacts (git-ignored)
reports/            generated figures and metric tables
report/             IEEE-format LaTeX project report
presentation/       slides and speaker notes for the Phase 1 evaluation
```

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
pytest
```

## Pipeline (planned)

```bash
python scripts/download_data.py      # TODO
python scripts/build_features.py     # TODO
python scripts/train.py --model logreg   # TODO
python scripts/train.py --model xgboost  # TODO
python scripts/evaluate.py           # TODO
```

## Phase 2 (later)

Compact MLP with learned embeddings for airline / origin / destination, optional temporal model,
and an offline what-if rescheduling analysis. Not part of this scaffold.

## Author

Ganga Raghuwanshi — Newton School of Technology, Rishihood University
