import pytest

from src import utils


def test_00(capfd: pytest.CaptureFixture[str]) -> None:
    utils.test()
    out, err = capfd.readouterr()
    assert "This is a test!\n" == out
    assert "" == err
