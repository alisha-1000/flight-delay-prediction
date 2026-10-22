"""Load the YAML experiment config."""

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = REPO_ROOT / "configs" / "config.yaml"


def load_config(path: str | Path = DEFAULT_CONFIG) -> dict:
    """Return the config as a dict."""
    with open(path) as f:
        return yaml.safe_load(f)
