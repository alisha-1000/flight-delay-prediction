"""Evaluation metrics required by the project brief."""

import numpy as np


def pr_auc(y_true: np.ndarray, y_prob: np.ndarray) -> float:
    """TODO: average_precision_score."""
    raise NotImplementedError


def roc_auc(y_true: np.ndarray, y_prob: np.ndarray) -> float:
    """TODO: roc_auc_score."""
    raise NotImplementedError


def recall_at_precision(y_true: np.ndarray, y_prob: np.ndarray, min_precision: float) -> tuple[float, float]:
    """TODO: return (best recall, threshold) among thresholds with precision >= min_precision.
    Choose the threshold on validation, then apply it unchanged to test."""
    raise NotImplementedError


def brier(y_true: np.ndarray, y_prob: np.ndarray) -> float:
    """TODO: brier_score_loss."""
    raise NotImplementedError


def expected_calibration_error(y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10) -> float:
    """TODO: ECE with equal-width bins (Guo et al., 2017)."""
    raise NotImplementedError
