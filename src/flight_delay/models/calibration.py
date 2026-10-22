"""Post-hoc probability calibration (fit on validation split only)."""


def calibrate(model, X_valid, y_valid, method: str = "isotonic"):
    """TODO: wrap a fitted model with Platt ('sigmoid') or isotonic calibration."""
    raise NotImplementedError
