"""IEC 60751 Pt100 resistance and temperature conversion.

The conversion implementation will be added after the reference values,
supported range, and numerical tolerances are verified.
"""

from __future__ import annotations


def resistance_to_celsius(resistance_ohms: float) -> float:
    """Convert IEC 60751 Pt100 resistance in ohms to degrees Celsius."""
    raise NotImplementedError("Pt100 conversion is not implemented yet")


def celsius_to_resistance(temperature_c: float) -> float:
    """Convert degrees Celsius to ideal IEC 60751 Pt100 resistance."""
    raise NotImplementedError("Pt100 conversion is not implemented yet")
