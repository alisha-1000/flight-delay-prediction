"""Train-only learned transformations: categorical level collapsing and numeric imputation."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

OTHER = "__OTHER__"


class FeatureEncoder:
    """Fit on the training split only, then apply unchanged to every split.

    * Categorical columns: levels with fewer than ``min_count`` training rows, and any level
      not seen in training, are mapped to ``__OTHER__``. Output is a pandas ``category`` with
      the same fixed category list in every split. That suits one-hot encoding for Logistic
      Regression and native categorical handling in XGBoost.
    * Numeric columns: missing values are filled with the training median. The only expected
      case is the first date of the data, when no history exists yet.
    """

    def __init__(self, categorical: list[str], numeric: list[str], min_count: int = 50):
        self.categorical = list(categorical)
        self.numeric = list(numeric)
        self.min_count = int(min_count)
        self.categories_: dict[str, list[str]] | None = None
        self.medians_: dict[str, float] | None = None

    def fit(self, train: pd.DataFrame) -> FeatureEncoder:
        self.categories_ = {}
        for col in self.categorical:
            counts = train[col].astype(str).value_counts()
            keep = sorted(counts[counts >= self.min_count].index)
            self.categories_[col] = keep + [OTHER]
        self.medians_ = {col: float(train[col].median()) for col in self.numeric}
        return self

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.categories_ is None or self.medians_ is None:
            raise RuntimeError("FeatureEncoder must be fitted on the training split first")
        out = df.copy()
        for col, cats in self.categories_.items():
            s = out[col].astype(str)
            s = s.where(s.isin(cats[:-1]), OTHER)
            out[col] = pd.Categorical(s, categories=cats)
        for col, med in self.medians_.items():
            out[col] = out[col].astype(float).fillna(med)
        return out

    def fit_transform(self, train: pd.DataFrame) -> pd.DataFrame:
        return self.fit(train).transform(train)

    # --- persistence (for reproducibility and reuse at inference time) ---
    def to_dict(self) -> dict:
        return {
            "categorical": self.categorical,
            "numeric": self.numeric,
            "min_count": self.min_count,
            "categories_": self.categories_,
            "medians_": self.medians_,
        }

    @classmethod
    def from_dict(cls, d: dict) -> FeatureEncoder:
        enc = cls(d["categorical"], d["numeric"], d["min_count"])
        enc.categories_, enc.medians_ = d["categories_"], d["medians_"]
        return enc

    def save(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(self.to_dict(), indent=1))

    @classmethod
    def load(cls, path: str | Path) -> FeatureEncoder:
        return cls.from_dict(json.loads(Path(path).read_text()))
