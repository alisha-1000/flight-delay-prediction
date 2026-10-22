"""Evaluation figures saved to reports/figures/."""


def plot_pr_curve(results: dict, out_path: str) -> None:
    """TODO: PR curves for all models on one axis, with no-skill baseline."""
    raise NotImplementedError


def plot_roc_curve(results: dict, out_path: str) -> None:
    """TODO: ROC curves for all models."""
    raise NotImplementedError


def plot_reliability_diagram(results: dict, out_path: str, n_bins: int = 10) -> None:
    """TODO: reliability diagram before/after calibration."""
    raise NotImplementedError


def plot_feature_importance(model, feature_names: list[str], out_path: str) -> None:
    """TODO: XGBoost gain importance (+ optional SHAP) and LR coefficients."""
    raise NotImplementedError
