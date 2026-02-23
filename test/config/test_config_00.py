import src


def test_config_00() -> None:
    config = src.config.Config.get_instance()
    assert config

    assert "sqlite:///:memory:" == config.connection_string
