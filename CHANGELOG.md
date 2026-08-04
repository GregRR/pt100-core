# Changelog

All notable changes to this project will be documented in this file.

## 0.1.0 — 2026-08-04

Initial release.

### Added

* IEC 60751 PT-385 Pt100 resistance-to-Celsius conversion.
* Celsius-to-resistance conversion for simulation and testing.
* Support for the standard -200 °C through 850 °C range.
* Input validation for non-finite, invalid, and out-of-range values.
* Analytic positive-temperature conversion and bounded numerical inversion below 0 °C.
* Independent reference-value tests based on the Fluke PT100 table generator.
* Exact boundary, round-trip, monotonicity, and invalid-input tests.
* Fixed resistance simulation.
* Finite and repeating resistance sequences.
* Temperature-defined simulation sequences.
* Reproducible Gaussian-noise simulation.
* Public `rtd.pt100` and `rtd.simulation` APIs.
* Python 3.14 support.
* GitHub Actions continuous integration.
* Mozilla Public License 2.0.
