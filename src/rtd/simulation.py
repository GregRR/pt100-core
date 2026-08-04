# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Simulation tools for RTD-based applications.

All simulated readers expose resistance in ohms. This allows application
code to use the same interface for simulated data and physical hardware.
"""

from __future__ import annotations

import math
import random
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Protocol

from . import pt100

__all__ = [
    "FixedResistanceReader",
    "NoisyTemperatureReader",
    "ResistanceReader",
    "ResistanceSequenceReader",
    "TemperatureSequenceReader",
    "read_temperature_celsius",
]


class ResistanceReader(Protocol):
    """An object capable of returning an RTD resistance measurement."""

    def read_resistance_ohms(self) -> float:
        """Return one resistance measurement in ohms."""
        ...


@dataclass(slots=True)
class FixedResistanceReader:
    """Return the same resistance for every reading."""

    resistance_ohms: float

    def __post_init__(self) -> None:
        self.resistance_ohms = _validate_resistance(
            self.resistance_ohms
        )

    def read_resistance_ohms(self) -> float:
        """Return the configured resistance."""
        return self.resistance_ohms


@dataclass(slots=True)
class ResistanceSequenceReader:
    """Return resistance values from a finite or repeating sequence."""

    readings_ohms: Sequence[float]
    repeat: bool = False
    _readings: tuple[float, ...] = field(
        init=False,
        repr=False,
    )
    _index: int = field(
        init=False,
        default=0,
        repr=False,
    )

    def __post_init__(self) -> None:
        if not self.readings_ohms:
            raise ValueError(
                "At least one resistance reading is required"
            )

        self._readings = tuple(
            _validate_resistance(reading)
            for reading in self.readings_ohms
        )

    def read_resistance_ohms(self) -> float:
        """Return the next resistance value.

        Raises:
            StopIteration: When a non-repeating sequence is exhausted.
        """
        if self._index >= len(self._readings):
            if not self.repeat:
                raise StopIteration(
                    "No simulated resistance readings remain"
                )

            self._index = 0

        resistance = self._readings[self._index]
        self._index += 1

        return resistance


@dataclass(slots=True)
class TemperatureSequenceReader:
    """Simulate resistance from a temperature sequence."""

    temperatures_c: Sequence[float]
    repeat: bool = False
    _reader: ResistanceSequenceReader = field(
        init=False,
        repr=False,
    )

    def __post_init__(self) -> None:
        if not self.temperatures_c:
            raise ValueError(
                "At least one simulated temperature is required"
            )

        readings = tuple(
            pt100.celsius_to_resistance(temperature)
            for temperature in self.temperatures_c
        )

        self._reader = ResistanceSequenceReader(
            readings_ohms=readings,
            repeat=self.repeat,
        )

    def read_resistance_ohms(self) -> float:
        """Return resistance corresponding to the next temperature."""
        return self._reader.read_resistance_ohms()


@dataclass(slots=True)
class NoisyTemperatureReader:
    """Simulate a temperature with reproducible Gaussian noise.

    Noise is applied in degrees Celsius before the simulated temperature
    is converted into ideal Pt100 resistance.

    Supplying the same seed produces the same sequence of readings.
    """

    temperature_c: float
    noise_standard_deviation_c: float = 0.05
    seed: int | None = None
    _random: random.Random = field(
        init=False,
        repr=False,
    )

    def __post_init__(self) -> None:
        # Validate the base temperature through the public conversion API.
        pt100.celsius_to_resistance(self.temperature_c)

        standard_deviation = float(
            self.noise_standard_deviation_c
        )

        if not math.isfinite(standard_deviation):
            raise ValueError(
                "Noise standard deviation must be finite"
            )

        if standard_deviation < 0.0:
            raise ValueError(
                "Noise standard deviation cannot be negative"
            )

        self.noise_standard_deviation_c = standard_deviation
        self._random = random.Random(self.seed)

    def read_resistance_ohms(self) -> float:
        """Return one noisy simulated Pt100 resistance reading."""
        simulated_temperature = self._random.gauss(
            self.temperature_c,
            self.noise_standard_deviation_c,
        )

        return pt100.celsius_to_resistance(
            simulated_temperature
        )


def read_temperature_celsius(
    reader: ResistanceReader,
) -> float:
    """Read resistance from a source and convert it to Celsius."""
    resistance = reader.read_resistance_ohms()
    return pt100.resistance_to_celsius(resistance)


def _validate_resistance(resistance_ohms: float) -> float:
    resistance = float(resistance_ohms)

    if not math.isfinite(resistance):
        raise ValueError("Resistance must be finite")

    if resistance <= 0.0:
        raise ValueError("Resistance must be greater than zero")

    # Validate that the resistance belongs to the supported Pt100 range.
    pt100.resistance_to_celsius(resistance)

    return resistance
