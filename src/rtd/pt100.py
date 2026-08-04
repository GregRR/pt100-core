# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""IEC 60751 Pt100 resistance and temperature conversion.

The implementation uses the IEC 60751 PT-385 Callendar–Van Dusen
resistance–temperature relationship.

Normative reference:
    IEC 60751:2022, Industrial platinum resistance thermometers and
    platinum temperature sensors.

Publicly accessible verification references:
    - Analog Devices, MAX31865 RTD-to-Digital Converter Data Sheet,
      Temperature Conversion section.
    - Fluke Calibration, PT100 Calculator and Resistance Table
      Generator.

The coefficients represent the standardized ideal curve. They do not
include individual probe calibration, lead-wire resistance, self-heating,
or measurement-circuit errors.
"""


from __future__ import annotations

import math

# IEC 60751 PT-385 Callendar–Van Dusen coefficients.
# Verified against the Analog Devices MAX31865 data sheet and Fluke's
# published PT100 calculation references.

R0_OHMS = 100.0

A = 3.9083e-3
B = -5.775e-7
C = -4.183e-12

MIN_TEMPERATURE_C = -200.0
MAX_TEMPERATURE_C = 850.0

_BISECTION_ITERATIONS = 60


def celsius_to_resistance(temperature_c: float) -> float:
    """Convert temperature in Celsius to ideal Pt100 resistance in ohms.

    The conversion uses the IEC 60751 Callendar–Van Dusen equation for
    a Pt100 RTD with a nominal resistance of 100 ohms at 0 °C.

    Args:
        temperature_c: Temperature in degrees Celsius.

    Returns:
        Ideal Pt100 resistance in ohms.

    Raises:
        ValueError: If the temperature is non-finite or outside the
            supported IEC 60751 range of -200 °C through 850 °C.
    """
    temperature = float(temperature_c)
    _validate_temperature(temperature)

    return _celsius_to_resistance_unchecked(temperature)


def resistance_to_celsius(resistance_ohms: float) -> float:
    """Convert Pt100 resistance in ohms to temperature in Celsius.

    The conversion uses the IEC 60751 Callendar–Van Dusen equation for
    a Pt100 RTD with a nominal resistance of 100 ohms at 0 °C.

    Temperatures at or above 0 °C are calculated by analytically
    inverting the quadratic portion of the equation. Temperatures below
    0 °C are calculated with bounded bisection over the supported range.

    Args:
        resistance_ohms: Measured, compensated Pt100 resistance in ohms.

    Returns:
        Temperature in degrees Celsius.

    Raises:
        ValueError: If the resistance is non-finite, non-positive, or
            outside the resistance range represented by -200 °C through
            850 °C.
    """
    resistance = float(resistance_ohms)
    _validate_resistance(resistance)

    if resistance >= R0_OHMS:
        return _nonnegative_resistance_to_celsius(resistance)

    return _negative_resistance_to_celsius(resistance)


def _celsius_to_resistance_unchecked(temperature_c: float) -> float:
    """Convert a previously validated temperature to resistance."""
    resistance_ratio = (
        1.0
        + A * temperature_c
        + B * temperature_c**2
    )

    if temperature_c < 0.0:
        resistance_ratio += (
            C
            * (temperature_c - 100.0)
            * temperature_c**3
        )

    return R0_OHMS * resistance_ratio


def _nonnegative_resistance_to_celsius(
    resistance_ohms: float,
) -> float:
    """Invert the nonnegative-temperature quadratic equation."""
    resistance_ratio = resistance_ohms / R0_OHMS

    discriminant = (
        A**2
        - 4.0 * B * (1.0 - resistance_ratio)
    )

    if discriminant < 0.0:
        raise ValueError(
            "Resistance cannot be converted using the IEC 60751 "
            "Pt100 curve"
        )

    temperature_c = (
        -A + math.sqrt(discriminant)
    ) / (2.0 * B)

    if temperature_c > MAX_TEMPERATURE_C:
        raise ValueError(
            "Resistance is above the supported Pt100 range"
        )

    return temperature_c


def _negative_resistance_to_celsius(
    resistance_ohms: float,
) -> float:
    """Invert the negative-temperature equation using bisection."""
    lower_c = MIN_TEMPERATURE_C
    upper_c = 0.0

    for _ in range(_BISECTION_ITERATIONS):
        midpoint_c = (lower_c + upper_c) / 2.0
        midpoint_resistance = _celsius_to_resistance_unchecked(
            midpoint_c
        )

        if midpoint_resistance < resistance_ohms:
            lower_c = midpoint_c
        else:
            upper_c = midpoint_c

    return (lower_c + upper_c) / 2.0


def _validate_temperature(temperature_c: float) -> None:
    if not math.isfinite(temperature_c):
        raise ValueError("Temperature must be finite")

    if not MIN_TEMPERATURE_C <= temperature_c <= MAX_TEMPERATURE_C:
        raise ValueError(
            "Temperature must be between "
            f"{MIN_TEMPERATURE_C:g} °C and "
            f"{MAX_TEMPERATURE_C:g} °C"
        )


def _validate_resistance(resistance_ohms: float) -> None:
    if not math.isfinite(resistance_ohms):
        raise ValueError("Resistance must be finite")

    if resistance_ohms <= 0.0:
        raise ValueError("Resistance must be greater than zero")

    minimum_resistance = _celsius_to_resistance_unchecked(
        MIN_TEMPERATURE_C
    )
    maximum_resistance = _celsius_to_resistance_unchecked(
        MAX_TEMPERATURE_C
    )

    if resistance_ohms < minimum_resistance:
        raise ValueError(
            "Resistance is below the supported Pt100 range"
        )

    if resistance_ohms > maximum_resistance:
        raise ValueError(
            "Resistance is above the supported Pt100 range"
        )