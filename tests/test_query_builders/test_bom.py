# Copyright (C) 2022 - 2026 ANSYS, Inc. and/or its affiliates.
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

from ..inputs import example_boms

all_bom_queries = pytest.mark.parametrize(
    "query_type",
    [
        queries.BomComplianceQuery,
        queries.BomImpactedSubstancesQuery,
        queries.BomSustainabilityQuery,
        queries.BomSustainabilitySummaryQuery,
    ],
)


@all_bom_queries
def test_add_bom(query_type):
    bom = example_boms["sustainability-bom-2301"].content
    query = query_type().with_bom(bom)
    assert isinstance(query, query_type)
    assert query._data.bom == bom


@all_bom_queries
def test_add_bom_wrong_type(query_type):
    with pytest.raises(TypeError) as e:
        query_type().with_bom(12345)
    assert "Incorrect type for argument 'bom'" in str(e.value)
    with pytest.raises(TypeError) as e:
        query_type().with_bom(bom=12345)
    assert "Incorrect type for argument 'bom'" in str(e.value)


@all_bom_queries
def test_no_bom(query_type):
    query = query_type()
    with pytest.raises(ValueError, match=r"No BoM has been added to the query"):
        query._validate_items()
