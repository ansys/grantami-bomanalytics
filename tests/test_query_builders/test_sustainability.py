# Copyright (C) 2022 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from ansys.openapi.common import Unset
import pytest

from ansys.grantami.bomanalytics import queries

DISTANCE = "a"
ENERGY = "b"
MASS = "c"


class TestUnitSelection:
    @pytest.mark.parametrize("mass", [MASS, Unset])
    @pytest.mark.parametrize("energy", [ENERGY, Unset])
    @pytest.mark.parametrize("distance", [DISTANCE, Unset])
    @pytest.mark.parametrize("query_type", [queries.BomSustainabilitySummaryQuery, queries.BomSustainabilityQuery])
    def test_units_are_set(self, query_type, mass, energy, distance):
        query = query_type()
        query.with_units(distance=distance, energy=energy, mass=mass)
        assert query._preferred_units.mass_unit == mass
        assert query._preferred_units.distance_unit == distance
        assert query._preferred_units.energy_unit == energy
