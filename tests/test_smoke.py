def test_package_imports():
    import flight_delay

    assert flight_delay.__version__


def test_config_loads():
    from flight_delay.config import load_config

    cfg = load_config()
    assert cfg["target"]["threshold_minutes"] == 15
