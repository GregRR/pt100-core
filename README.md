# pt100-core

A small, platform-independent Python library for converting resistance measurements from a standard IEC 60751 Pt100 resistance temperature detector into temperature.

It also supports the inverse conversion from temperature to ideal Pt100 resistance for simulation and testing.

## Scope

`pt100-core` handles:

```text
Pt100 resistance in ohms ↔ temperature in Celsius
```

The initial implementation assumes:

* IEC 60751 Pt100
* 100 Ω at 0 °C
* α = 0.00385

The conversion is not specific to a particular sensor manufacturer.

Hardware-specific concerns such as ADC readings, GPIO, SPI, I²C, excitation circuits, and lead-wire compensation belong in separate hardware layers.

## Basic usage

```python
from rtd import pt100

temperature_c = pt100.resistance_to_celsius(119.3971)
resistance_ohms = pt100.celsius_to_resistance(50.0)
```

## Development setup

The project currently targets Python 3.14.

```bash
conda create -n pt100-core python=3.14 pip
conda activate pt100-core
python -m pip install -e ".[dev]"
```

Run the checks:

```bash
pytest
ruff check .
mypy
```

## Project structure

```text
src/rtd/
    pt100.py
    simulation.py

tests/
docs/DESIGN.md
```

The repository is named `pt100-core` for discoverability. The Python package uses the broader `rtd` namespace so additional RTD families can be added later without changing existing Pt100 imports.

See [`docs/DESIGN.md`](docs/DESIGN.md) for detailed architecture, mathematical assumptions, testing requirements, and future plans.

## Status

Version 0.1.0 provides:

- IEC 60751 Pt100 resistance-to-temperature conversion
- temperature-to-resistance conversion
- input and supported-range validation
- independently sourced reference-value tests
- fixed, sequential, repeating, and noisy simulation readers
- reproducible seeded simulation noise
- a stable initial public API

## License

This project is licensed under the Mozilla Public License 2.0. See [`LICENSE`](LICENSE).
