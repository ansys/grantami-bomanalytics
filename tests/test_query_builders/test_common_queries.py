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

from ..common import INDICATORS, LEGISLATIONS

TEST_GUIDS = [
    [],
    set(),
    ["00000000-0000-0000-0000-000000000000"],
    ["00000000-0123-4567-89AB-000000000000", "00000000-0000-0000-0000-CDEF01234567"],
    {"00000000-0000-0000-0000-000000000000"},
    {"00000000-0123-4567-89AB-000000000000", "00000000-0000-0000-0000-CDEF01234567"},
]
TEST_HISTORY_IDS = [
    [],
    set(),
    [123],
    [456, 789],
    {987, 654},
    {321},
]
TEST_HETEROGENEOUS = [
    ["Test", 789],
    {"Test", 654},
    [456, "Test"],
    {987, "Test"},
]


@pytest.mark.parametrize(
    "query_type",
    [
        queries.MaterialImpactedSubstancesQuery,
        queries.MaterialComplianceQuery,
        queries.PartImpactedSubstancesQuery,
        queries.PartComplianceQuery,
        queries.SpecificationImpactedSubstancesQuery,
        queries.SpecificationComplianceQuery,
        queries.SubstanceComplianceQuery,
    ],
)
class TestRecordQueries:
    @pytest.mark.parametrize("test_values", TEST_GUIDS)
    def test_add_record_guids(self, query_type, test_values):
        query = query_type().with_record_guids(test_values)
        assert isinstance(query, query_type)
        assert len(query._data._item_definitions) == len(test_values)
        for idx, guid in enumerate(test_values):
            assert query._data._item_definitions[idx].record_guid == guid
            assert not query._data._item_definitions[idx].record_history_guid
            assert not query._data._item_definitions[idx].record_history_identity

    @pytest.mark.parametrize("test_values", TEST_GUIDS)
    def test_add_record_history_guids(self, query_type, test_values):
        query = query_type().with_record_history_guids(test_values)
        assert isinstance(query, query_type)
        assert len(query._data._item_definitions) == len(test_values)
        for idx, guid in enumerate(test_values):
            assert query._data._item_definitions[idx].record_history_guid == guid
            assert not query._data._item_definitions[idx].record_guid
            assert not query._data._item_definitions[idx].record_history_identity

    @pytest.mark.parametrize("test_values", TEST_HISTORY_IDS)
    def test_add_record_history_ids(self, query_type, test_values):
        query = query_type().with_record_history_ids(test_values)
        assert isinstance(query, query_type)
        assert len(query._data._item_definitions) == len(test_values)
        for idx, id in enumerate(test_values):
            assert query._data._item_definitions[idx].record_history_identity == id
            assert not query._data._item_definitions[idx].record_guid
            assert not query._data._item_definitions[idx].record_history_guid

    @pytest.mark.parametrize("test_values", TEST_HISTORY_IDS[2:] + TEST_HETEROGENEOUS)
    def test_add_record_guids_wrong_type_type_error(self, query_type, test_values):
        with pytest.raises(TypeError):
            query_type().with_record_guids(test_values)
            query_type().with_record_guids(record_guids=test_values)

    @pytest.mark.parametrize("test_values", TEST_HISTORY_IDS[2:] + TEST_HETEROGENEOUS)
    def test_add_record_history_guids_wrong_type_type_error(self, query_type, test_values):
        with pytest.raises(TypeError):
            query_type().with_record_history_guids(test_values)
            query_type().with_record_history_guids(record_history_guids=test_values)

    @pytest.mark.parametrize("test_values", TEST_GUIDS[2:] + TEST_HETEROGENEOUS)
    def test_add_record_history_ids_wrong_type_type_error(self, query_type, test_values):
        with pytest.raises(TypeError):
            query_type().with_record_history_ids(test_values)
            query_type().with_record_history_ids(record_history_identities=test_values)

    def test_no_items_raises_error(self, query_type):
        query = query_type()
        with pytest.raises(ValueError, match=r"No \w+ have been added to the query"):
            query._validate_items()

    def test_batch_size(self, query_type):
        query = query_type()
        query = query.with_batch_size(50)
        assert query._data.batch_size == 50

    @pytest.mark.parametrize("batch_size", [0, -25])
    def test_batch_size_incorrect_values_value_error(self, query_type, batch_size):
        query = query_type()
        with pytest.raises(ValueError) as e:
            query.with_batch_size(batch_size)
        assert "Batch size must be a positive integer" in str(e.value)
        with pytest.raises(ValueError) as e:
            query.with_batch_size(batch_size=batch_size)
        assert "Batch size must be a positive integer" in str(e.value)

    @pytest.mark.parametrize("batch_size", [20.25, "5", None, ["List"], {"Set"}])
    def test_batch_size_incorrect_types_type_error(self, query_type, batch_size):
        query = query_type()
        with pytest.raises(TypeError):
            query.with_batch_size(batch_size)
            query.with_batch_size(batch_size=batch_size)


@pytest.mark.parametrize(
    "query_type",
    [
        queries.MaterialComplianceQuery,
        queries.PartComplianceQuery,
        queries.SpecificationComplianceQuery,
        queries.SubstanceComplianceQuery,
        queries.BomComplianceQuery,
    ],
)
class TestComplianceQueries:
    def test_add_indicators_correct_types(self, query_type):
        indicators = list(INDICATORS.values())
        query = query_type().with_indicators(indicators)
        assert len(query._indicators) == len(indicators)
        for indicator in indicators:
            assert query._indicators[indicator.name] is indicator

    def test_add_indicators_wrong_types_type_error(self, query_type):
        with pytest.raises(TypeError):
            query_type().with_indicators(LEGISLATIONS)
            query_type().with_indicators(indicators=LEGISLATIONS)

    def test_add_legislations_attribute_error(self, query_type):
        with pytest.raises(AttributeError):
            query_type().with_legislation_ids(LEGISLATIONS)


@pytest.mark.parametrize(
    "query_type",
    [
        queries.MaterialImpactedSubstancesQuery,
        queries.PartImpactedSubstancesQuery,
        queries.SpecificationImpactedSubstancesQuery,
        queries.BomImpactedSubstancesQuery,
    ],
)
class TestSubstanceQueries:
    def test_add_legislations_correct_types(self, query_type):
        query = query_type().with_legislation_ids(LEGISLATIONS)
        assert len(query._legislations) == len(LEGISLATIONS)
        for idx, legislation in enumerate(LEGISLATIONS):
            assert query._legislations[idx] == legislation

    def test_add_legislations_wrong_types_type_error(self, query_type):
        with pytest.raises(TypeError):
            query_type().with_legislation_ids(INDICATORS)
            query_type().with_legislation_ids(legislations=INDICATORS)

    def test_add_indicators_attribute_error(self, query_type):
        with pytest.raises(AttributeError):
            query_type().with_indicators(INDICATORS)
