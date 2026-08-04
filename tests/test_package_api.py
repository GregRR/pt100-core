# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from rtd import pt100


def test_package_exports_pt100_module() -> None:
    from rtd import pt100 as imported_pt100

    assert imported_pt100 is pt100


def test_pt100_public_api() -> None:
    assert set(pt100.__all__) == {
        "MAX_TEMPERATURE_C",
        "MIN_TEMPERATURE_C",
        "R0_OHMS",
        "celsius_to_resistance",
        "resistance_to_celsius",
    }
