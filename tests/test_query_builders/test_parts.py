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

import pytest

from ansys.grantami.bomanalytics import queries

from .common import check_query_manager_attributes


@pytest.mark.parametrize("query_type", [queries.PartComplianceQuery, queries.PartImpactedSubstancesQuery])
@pytest.mark.parametrize("part_numbers", [[], ["One part number"], ["Two", "Part numbers"]])
def test_add_part_numbers(query_type, part_numbers):
    query = query_type().with_part_numbers(part_numbers)
    assert isinstance(query, query_type)
    assert check_query_manager_attributes(
        query,
        ["record_guid", "record_history_guid", "record_history_identity"],
        "part_number",
        part_numbers,
    )


@pytest.mark.parametrize("query_type", [queries.PartComplianceQuery, queries.PartImpactedSubstancesQuery])
def test_add_part_numbers_wrong_type(query_type):
    with pytest.raises(TypeError) as e:
        query_type().with_part_numbers("Strings are not allowed")
    assert 'Incorrect type for value "Strings are not allowed"' in str(e.value)
    with pytest.raises(TypeError) as e:
        query_type().with_part_numbers(part_numbers="Strings are not allowed")
    assert 'Incorrect type for value "Strings are not allowed"' in str(e.value)
