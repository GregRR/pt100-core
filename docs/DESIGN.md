# pt100-core Design

## 1. Purpose

`pt100-core` provides a small, dependable, platform-independent implementation of resistance-to-temperature and temperature-to-resistance conversion for an industry-standard Pt100 resistance temperature detector.

The first supported sensor model is:

- platinum resistance thermometer
- nominal resistance: 100 Ω at 0 °C
- standard: IEC 60751
- nominal temperature coefficient: α = 0.00385

The project exists so applications can share one tested scientific conversion layer while keeping hardware acquisition code separate.

## 2. Core architectural boundary

The project begins only after a hardware or simulated measurement has been expressed as resistance in ohms.

```text
raw ADC or digital-interface data
              |
              v
hardware-specific measurement and compensation
              |
              v
resistance in ohms
              |
              v
pt100-core
              |
              v
temperature in Celsius
```

`pt100-core` does not determine how raw electrical signals become resistance. That responsibility belongs to hardware-facing code.

This boundary allows identical conversion code to be used with:

- BeagleBone Black
- Raspberry Pi
- desktop computers
- microcomputer test environments
- MAX31865 interfaces
- custom analog front ends
- recorded datasets
- simulated data

## 3. Design principles

### 3.1 Platform independence

The core package must not depend on GPIO, SPI, I²C, ADC, or board-specific libraries.

### 3.2 Scientific transparency

The implementation should identify the standard, equation, constants, assumptions, and supported range. Constants must not appear as unexplained magic numbers.

### 3.3 Small public API

The primary version 1 interface should remain simple:

```python
from rtd import pt100

temperature_c = pt100.resistance_to_celsius(resistance_ohms)
resistance_ohms = pt100.celsius_to_resistance(temperature_c)
```

### 3.4 Simulation as a first-class use case

Temperature-to-resistance conversion is part of the supported public API, not merely an internal helper. It enables application testing without attached hardware.

### 3.5 No premature hardware coupling

Wire compensation, excitation circuits, ADC scaling, amplifier gain, reference resistors, and device-register handling must not leak into the scientific conversion layer.

### 3.6 Verifiability

Results must be tested against authoritative IEC 60751 reference values or independently reproduced reference tables.

## 4. Mathematical model

Version 1 will use the IEC 60751 Callendar–Van Dusen relationship.

For temperatures at or above 0 °C:

```text
R(T) = R0 × (1 + A×T + B×T²)
```

For temperatures below 0 °C:

```text
R(T) = R0 × [1 + A×T + B×T² + C×(T - 100)×T³]
```

For the standard IEC 60751 Pt100 curve:

```text
R0 = 100 Ω
A  = 3.9083 × 10⁻³ °C⁻¹
B  = -5.775 × 10⁻⁷ °C⁻²
C  = -4.183 × 10⁻¹² °C⁻⁴
```

Resistance-to-temperature conversion above 0 °C may use the analytic inverse of the quadratic equation. Below 0 °C, the implementation may use a bounded numerical solution of the complete equation.

The implementation must document numerical tolerances and must avoid silently extrapolating beyond its supported range.

## 5. Initial public API

The initial module is `rtd.pt100`.

Planned functions:

```python
def resistance_to_celsius(resistance_ohms: float) -> float:
    ...

def celsius_to_resistance(temperature_c: float) -> float:
    ...
```

Potential future convenience functions may include:

```python
def resistance_to_fahrenheit(resistance_ohms: float) -> float:
    ...

def fahrenheit_to_resistance(temperature_f: float) -> float:
    ...
```

Those convenience functions are not required for the first release. Celsius is the native temperature representation because the governing standard is expressed in Celsius.

## 6. Validation and errors

The conversion functions should reject:

- non-finite numeric values
- non-positive resistance values
- temperatures outside the documented supported range
- resistance values that cannot represent a temperature inside that range

Errors should use clear `ValueError` messages unless a dedicated exception hierarchy becomes justified.

The package should not silently clamp values.

## 7. Simulation

Simulation should support two levels.

### 7.1 Exact reference simulation

The inverse conversion function generates ideal resistance from a requested temperature:

```python
resistance = pt100.celsius_to_resistance(65.0)
```

This is sufficient for deterministic tests of application behavior.

### 7.2 Measurement-stream simulation

A later simulation module may produce:

- fixed readings
- finite sequences
- repeating sequences
- ramps
- heating and cooling profiles
- seeded noise
- injected open-circuit or short-circuit faults

Simulation components should expose resistance values so they exercise the same application path as real hardware.

## 8. Testing strategy

Tests should include:

- 0 °C equals exactly 100 Ω
- representative negative temperatures
- representative positive temperatures
- round-trip temperature → resistance → temperature
- round-trip resistance → temperature → resistance
- boundary values
- invalid input
- non-finite values
- monotonicity across the supported range
- known IEC reference-table values

Round-trip tests alone are insufficient because the forward and inverse implementations could share the same error. At least some expected values must come from an independent reference source.

## 9. Accuracy boundaries

The core conversion describes the ideal standardized curve. It does not by itself account for:

- sensor tolerance class
- individual probe calibration
- lead-wire resistance
- self-heating
- excitation-current error
- amplifier offset or gain
- ADC quantization
- reference-resistor tolerance
- thermal gradients
- immersion depth
- response time

Hardware and calibration layers may correct these effects before passing resistance into the core, or may apply a documented calibration model afterward.

## 10. Package structure

Initial structure:

```text
pt100-core/
├── src/
│   └── rtd/
│       ├── __init__.py
│       ├── pt100.py
│       └── simulation.py
├── tests/
│   ├── test_pt100.py
│   └── test_simulation.py
├── docs/
│   └── DESIGN.md
├── .gitignore
├── pyproject.toml
└── README.md
```

The `rtd` namespace is intentionally broader than the initial repository name.

## 11. Repository and namespace strategy

The repository begins as `pt100-core` because users commonly search for the specific term “Pt100.”

The Python import namespace begins as `rtd`:

```python
from rtd import pt100
```

Once the project genuinely supports additional RTD families, the repository may be renamed `rtd-core`. The Python import path would remain unchanged.

## 12. Future RTD-family support

Potential future additions include:

- Pt1000
- Pt500
- alternate standardized platinum curves
- user-supplied Callendar–Van Dusen coefficients
- individually calibrated R0 values
- calibrated coefficient sets
- tolerance-class calculations
- uncertainty propagation
- vectorized conversion
- tabular or lookup-based conversion for constrained systems

Additional RTD types should not be advertised until their equations, ranges, and reference tests are implemented and documented.

## 13. Related future repositories

Possible companion projects include:

```text
pt100-hardware
    Shared hardware-facing interfaces and measurement models

pt100-max31865
    MAX31865 driver independent of host platform

pt100-bbb
    BeagleBone-specific acquisition adapters

pt100-rpi
    Raspberry Pi-specific acquisition adapters

pt100-examples
    Complete applications and integration examples
```

These names are provisional. Hardware packages should be split by actual abstraction boundary rather than created in advance.

## 14. Explicit non-goals for version 1

Version 1 will not include:

- board-specific hardware drivers
- ADC configuration
- GPIO, SPI, or I²C access
- analog circuit design
- lead-wire compensation algorithms tied to a circuit
- MAX31865 register handling
- process-control logic
- heater or relay control
- data logging
- graphical interfaces
- network services

## 15. Open design decisions

The following decisions should be made before the first stable release:

1. Exact supported temperature range.
2. Authoritative reference table used for verification.
3. Numerical inversion method below 0 °C.
4. Required absolute and relative numerical tolerances.
5. Whether simulation belongs in the core distribution or an optional module.
6. Final open-source license.
7. Minimum supported Python version.
8. Whether the distribution name should remain `pt100-core` after a future repository rename.
