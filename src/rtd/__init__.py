# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Resistance temperature detector conversion tools.

The initial public API provides IEC 60751 Pt100 conversion through the
:mod:`rtd.pt100` module.

Example:
    from rtd import pt100

    temperature_c = pt100.resistance_to_celsius(119.3971)
"""

from . import pt100

__all__ = ["pt100"]
