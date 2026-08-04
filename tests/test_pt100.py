import pytest

from rtd import pt100


def test_resistance_to_celsius_is_not_implemented_yet() -> None:
    with pytest.raises(NotImplementedError):
        pt100.resistance_to_celsius(100.0)


def test_celsius_to_resistance_is_not_implemented_yet() -> None:
    with pytest.raises(NotImplementedError):
        pt100.celsius_to_resistance(0.0)
