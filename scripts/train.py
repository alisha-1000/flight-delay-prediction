"""Train a model (--model logreg|xgboost), calibrate on validation, save to models/."""

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/config.yaml")
    parser.add_argument("--model", choices=["logreg", "xgboost"], required=True)
    args = parser.parse_args()
    # TODO: implement
    raise NotImplementedError


if __name__ == "__main__":
    main()
