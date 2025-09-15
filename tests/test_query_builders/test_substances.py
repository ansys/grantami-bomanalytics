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

SubstanceCompliance = queries.SubstanceComplianceQuery


@pytest.mark.parametrize("values", [[], ["One chemical_name"], ["Two", "Chemical names"]])
class TestWithoutAmounts:
    def test_add_chemical_names(self, values):
        query = SubstanceCompliance().with_chemical_names(values)
        assert isinstance(query, SubstanceCompliance)
        assert check_query_manager_attributes(
            query,
            [
                "record_guid",
                "record_history_guid",
                "record_history_identity",
                "cas_number",
                "ec_number",
                "_percentage_amount",
            ],
            "chemical_name",
            values,
        )
        assert all([i.percentage_amount == i._default_percentage_amount for i in query._data._item_definitions])

    def test_add_cas_numbers(self, values):
        query = SubstanceCompliance().with_cas_numbers(values)
        assert isinstance(query, SubstanceCompliance)
        assert check_query_manager_attributes(
            query,
            [
                "record_guid",
                "record_history_guid",
                "record_history_identity",
                "chemical_name",
                "ec_number",
                "_percentage_amount",
            ],
            "cas_number",
            values,
        )
        assert all([i.percentage_amount == i._default_percentage_amount for i in query._data._item_definitions])

    def test_add_ec_numbers(self, values):
        query = SubstanceCompliance().with_ec_numbers(values)
        assert isinstance(query, SubstanceCompliance)
        assert check_query_manager_attributes(
            query,
            [
                "record_guid",
                "record_history_guid",
                "record_history_identity",
                "chemical_name",
                "cas_number",
                "_percentage_amount",
            ],
            "ec_number",
            values,
        )
        assert all([i.percentage_amount == i._default_percentage_amount for i in query._data._item_definitions])


@pytest.mark.parametrize("values", ["Strings are not allowed", [("id_with_amount", 12)], 12])
class TestWithoutAmountsWrongType:
    def test_add_chemical_names(self, values):
        with pytest.raises(TypeError) as e:
            SubstanceCompliance().with_chemical_names(values)
        assert "Incorrect type for argument 'chemical_names' value" in str(e.value)
        with pytest.raises(TypeError) as e:
            SubstanceCompliance().with_chemical_names(chemical_names=values)
        assert "Incorrect type for argument 'chemical_names' value" in str(e.value)

    def test_add_cas_numbers(self, values):
        with pytest.raises(TypeError) as e:
            SubstanceCompliance().with_cas_numbers(values)
        assert "Incorrect type for argument 'cas_numbers' value" in str(e.value)
        with pytest.raises(TypeError) as e:
            SubstanceCompliance().with_cas_numbers(cas_numbers=values)
        assert "Incorrect type for argument 'cas_numbers' value" in str(e.value)

    def test_add_ec_numbers(self, values):
        with pytest.raises(TypeError) as e:
            SubstanceCompliance().with_ec_numbers(values)
        assert "Incorrect type for argument 'ec_numbers' value" in str(e.value)
        with pytest.raises(TypeError) as e:
            SubstanceCompliance().with_ec_numbers(ec_numbers=values)
        assert "Incorrect type for argument 'ec_numbers' value" in str(e.value)


@pytest.mark.parametrize(
    "values",
    [([("One chemical_name", 12.5)]), ([("Two", 0.001), ("Chemical names", 100)])],
)
class TestWithAmounts:
    def test_record_guids(self, values):
        query = SubstanceCompliance().with_record_guids_and_amounts(values)
        assert isinstance(query, SubstanceCompliance)
        assert check_query_manager_attributes(
            query,
            [
                "chemical_name",
                "record_history_guid",
                "record_history_identity",
                "cas_number",
                "ec_number",
            ],
            "record_guid",
            [v for (v, _) in values],
        )
        assert all([i._percentage_amount == amount for i, (_, amount) in zip(query._data._item_definitions, values)])
        assert all([i.percentage_amount == amount for i, (_, amount) in zip(query._data._item_definitions, values)])

    def test_record_history_guids(self, values):
        query = SubstanceCompliance().with_record_history_guids_and_amounts(values)
        assert isinstance(query, SubstanceCompliance)
        assert check_query_manager_attributes(
            query,
            [
                "chemical_name",
                "record_guid",
                "record_history_identity",
                "cas_number",
                "ec_number",
            ],
            "record_history_guid",
            [v for (v, _) in values],
        )
        assert all([i._percentage_amount == amount for i, (_, amount) in zip(query._data._item_definitions, values)])
        assert all([i.percentage_amount == amount for i, (_, amount) in zip(query._data._item_definitions, values)])

    def test_add_chemical_names(self, values):
        query = SubstanceCompliance().with_chemical_names_and_amounts(values)
        assert isinstance(query, SubstanceCompliance)
        assert check_query_manager_attributes(
            query,
            [
                "record_guid",
                "record_history_guid",
                "record_history_identity",
                "cas_number",
                "ec_number",
            ],
            "chemical_name",
            [v for (v, _) in values],
        )
        assert all([i._percentage_amount == amount for i, (_, amount) in zip(query._data._item_definitions, values)])
        assert all([i.percentage_amount == amount for i, (_, amount) in zip(query._data._item_definitions, values)])

    def test_add_cas_numbers(self, values):
        query = SubstanceCompliance().with_cas_numbers_and_amounts(values)
        assert isinstance(query, SubstanceCompliance)
        assert check_query_manager_attributes(
            query,
            [
                "record_guid",
                "record_history_guid",
                "record_history_identity",
                "chemical_name",
                "ec_number",
            ],
            "cas_number",
            [v for (v, _) in values],
        )
        assert all([i._percentage_amount == amount for i, (_, amount) in zip(query._data._item_definitions, values)])
        assert all([i.percentage_amount == amount for i, (_, amount) in zip(query._data._item_definitions, values)])

    def test_add_ec_numbers(self, values):
        query = SubstanceCompliance().with_ec_numbers_and_amounts(values)
        assert isinstance(query, SubstanceCompliance)
        assert check_query_manager_attributes(
            query,
            [
                "record_guid",
                "record_history_guid",
                "record_history_identity",
                "chemical_name",
                "cas_number",
            ],
            "ec_number",
            [v for (v, _) in values],
        )
        assert all([i._percentage_amount == amount for i, (_, amount) in zip(query._data._item_definitions, values)])
        assert all([i.percentage_amount == amount for i, (_, amount) in zip(query._data._item_definitions, values)])


@pytest.mark.parametrize("values", [([(123, 12.5)]), ([(234, 0.001), (345, 100)])])
def test_record_history_ids_with_amounts(values):
    query = SubstanceCompliance().with_record_history_ids_and_amounts(values)
    assert isinstance(query, SubstanceCompliance)
    assert check_query_manager_attributes(
        query,
        [
            "record_guid",
            "record_history_guid",
            "ec_number",
            "chemical_name",
            "cas_number",
        ],
        "record_history_identity",
        [v for (v, _) in values],
    )
    assert all([i._percentage_amount == amount for i, (_, amount) in zip(query._data._item_definitions, values)])
    assert all([i.percentage_amount == amount for i, (_, amount) in zip(query._data._item_definitions, values)])


@pytest.mark.parametrize(
    "values",
    [
        "Strings are not allowed",
        [("id_without_amount", None)],
        12,
        ("id_with_text_amount", "23"),
        ("id_with_complex_number", complex(5, 1)),
    ],
)
class TestWithAmountsWrongType:
    def test_record_guids(self, values):
        with pytest.raises(TypeError) as e:
            SubstanceCompliance().with_record_guids_and_amounts(values)
        assert "Incorrect type for argument 'record_guids_and_amounts' value" in str(e.value)
        with pytest.raises(TypeError) as e:
            SubstanceCompliance().with_record_guids_and_amounts(record_guids_and_amounts=values)
        assert "Incorrect type for argument 'record_guids_and_amounts' value" in str(e.value)

    def test_record_history_guids(self, values):
        with pytest.raises(TypeError) as e:
            SubstanceCompliance().with_record_history_guids_and_amounts(values)
        assert "Incorrect type for argument 'record_history_guids_and_amounts' value" in str(e.value)
        with pytest.raises(TypeError) as e:
            SubstanceCompliance().with_record_history_guids_and_amounts(record_history_guids_and_amounts=values)
        assert "Incorrect type for argument 'record_history_guids_and_amounts' value" in str(e.value)

    def test_record_history_ids(self, values):
        with pytest.raises(TypeError) as e:
            SubstanceCompliance().with_record_history_ids_and_amounts(values)
        assert "Incorrect type for argument 'record_history_identities_and_amounts' value" in str(e.value)
        with pytest.raises(TypeError) as e:
            SubstanceCompliance().with_record_history_ids_and_amounts(record_history_identities_and_amounts=values)
        assert "Incorrect type for argument 'record_history_identities_and_amounts' value" in str(e.value)

    def test_add_chemical_names(self, values):
        with pytest.raises(TypeError) as e:
            SubstanceCompliance().with_chemical_names_and_amounts(values)
        assert "Incorrect type for argument 'chemical_names_and_amounts' value" in str(e.value)
        with pytest.raises(TypeError) as e:
            SubstanceCompliance().with_chemical_names_and_amounts(chemical_names_and_amounts=values)
        assert "Incorrect type for argument 'chemical_names_and_amounts' value" in str(e.value)

    def test_add_cas_numbers(self, values):
        with pytest.raises(TypeError) as e:
            SubstanceCompliance().with_cas_numbers_and_amounts(values)
        assert "Incorrect type for argument 'cas_numbers_and_amounts' value" in str(e.value)
        with pytest.raises(TypeError) as e:
            SubstanceCompliance().with_cas_numbers_and_amounts(cas_numbers_and_amounts=values)
        assert "Incorrect type for argument 'cas_numbers_and_amounts' value" in str(e.value)

    def test_add_ec_numbers(self, values):
        with pytest.raises(TypeError) as e:
            SubstanceCompliance().with_ec_numbers_and_amounts(values)
        assert "Incorrect type for argument 'ec_numbers_and_amounts' value" in str(e.value)
        with pytest.raises(TypeError) as e:
            SubstanceCompliance().with_ec_numbers_and_amounts(ec_numbers_and_amounts=values)
        assert "Incorrect type for argument 'ec_numbers_and_amounts' value" in str(e.value)
