from ..common import pytest, queries, check_query_manager_attributes

SubstanceCompliance = queries.SubstanceCompliance


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
        assert all([i.percentage_amount == i._default_percentage_amount for i in query._items])

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
        assert all([i.percentage_amount == i._default_percentage_amount for i in query._items])

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
        assert all([i.percentage_amount == i._default_percentage_amount for i in query._items])


@pytest.mark.parametrize("values", ["Strings are not allowed", [("id_with_amount", 12)], 12])
class TestWithoutAmountsWrongType:
    def test_add_chemical_names(self, values):
        with pytest.raises(TypeError) as e:
            SubstanceCompliance().with_chemical_names(values)
        assert "Incorrect type for value" in str(e.value)
        with pytest.raises(TypeError) as e:
            SubstanceCompliance().with_chemical_names(chemical_names=values)
        assert "Incorrect type for value" in str(e.value)

    def test_add_cas_numbers(self, values):
        with pytest.raises(TypeError) as e:
            SubstanceCompliance().with_cas_numbers(values)
        assert "Incorrect type for value" in str(e.value)
        with pytest.raises(TypeError) as e:
            SubstanceCompliance().with_cas_numbers(cas_numbers=values)
        assert "Incorrect type for value" in str(e.value)

    def test_add_ec_numbers(self, values):
        with pytest.raises(TypeError) as e:
            SubstanceCompliance().with_ec_numbers(values)
        assert "Incorrect type for value" in str(e.value)
        with pytest.raises(TypeError) as e:
            SubstanceCompliance().with_ec_numbers(ec_numbers=values)
        assert "Incorrect type for value" in str(e.value)


@pytest.mark.parametrize(
    "values",
    [([("One chemical_name", 12.5)]), ([("Two", 0.001), ("Chemical names", 100)])],
)
class TestWithAmounts:
    def test_record_guids(self, values):
        query = SubstanceCompliance().with_record_guids_with_amounts(values)
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
        assert all([i._percentage_amount == amount for i, (_, amount) in zip(query._items, values)])
        assert all([i.percentage_amount == amount for i, (_, amount) in zip(query._items, values)])

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
        assert all([i._percentage_amount == amount for i, (_, amount) in zip(query._items, values)])
        assert all([i.percentage_amount == amount for i, (_, amount) in zip(query._items, values)])

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
        assert all([i._percentage_amount == amount for i, (_, amount) in zip(query._items, values)])
        assert all([i.percentage_amount == amount for i, (_, amount) in zip(query._items, values)])

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
        assert all([i._percentage_amount == amount for i, (_, amount) in zip(query._items, values)])
        assert all([i.percentage_amount == amount for i, (_, amount) in zip(query._items, values)])

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
        assert all([i._percentage_amount == amount for i, (_, amount) in zip(query._items, values)])
        assert all([i.percentage_amount == amount for i, (_, amount) in zip(query._items, values)])


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
    assert all([i._percentage_amount == amount for i, (_, amount) in zip(query._items, values)])
    assert all([i.percentage_amount == amount for i, (_, amount) in zip(query._items, values)])


@pytest.mark.parametrize("values", ["Strings are not allowed", [("id_without_amount", None)], 12])
class TestWithAmountsWrongType:
    def test_record_guids(self, values):
        with pytest.raises(TypeError) as e:
            SubstanceCompliance().with_record_guids_with_amounts(values)
        assert f"Incorrect type for value" in str(e.value)
        with pytest.raises(TypeError) as e:
            SubstanceCompliance().with_record_guids_with_amounts(record_guids_and_amounts=values)
        assert f"Incorrect type for value" in str(e.value)

    def test_record_history_guids(self, values):
        with pytest.raises(TypeError) as e:
            SubstanceCompliance().with_record_history_guids_and_amounts(values)
        assert f"Incorrect type for value" in str(e.value)
        with pytest.raises(TypeError) as e:
            SubstanceCompliance().with_record_history_guids_and_amounts(record_history_guids_and_amounts=values)
        assert f"Incorrect type for value" in str(e.value)

    def test_record_history_ids(self, values):
        with pytest.raises(TypeError) as e:
            SubstanceCompliance().with_record_history_ids_and_amounts(values)
        assert f"Incorrect type for value" in str(e.value)
        with pytest.raises(TypeError) as e:
            SubstanceCompliance().with_record_history_ids_and_amounts(record_history_identities_and_amounts=values)
        assert f"Incorrect type for value" in str(e.value)

    def test_add_chemical_names(self, values):
        with pytest.raises(TypeError) as e:
            SubstanceCompliance().with_chemical_names_and_amounts(values)
        assert f"Incorrect type for value" in str(e.value)
        with pytest.raises(TypeError) as e:
            SubstanceCompliance().with_chemical_names_and_amounts(chemical_names_and_amounts=values)
        assert f"Incorrect type for value" in str(e.value)

    def test_add_cas_numbers(self, values):
        with pytest.raises(TypeError) as e:
            SubstanceCompliance().with_cas_numbers_and_amounts(values)
        assert f"Incorrect type for value" in str(e.value)
        with pytest.raises(TypeError) as e:
            SubstanceCompliance().with_cas_numbers_and_amounts(cas_numbers_and_amounts=values)
        assert f"Incorrect type for value" in str(e.value)

    def test_add_ec_numbers(self, values):
        with pytest.raises(TypeError) as e:
            SubstanceCompliance().with_ec_numbers_and_amounts(values)
        assert f"Incorrect type for value" in str(e.value)
        with pytest.raises(TypeError) as e:
            SubstanceCompliance().with_ec_numbers_and_amounts(ec_numbers_and_amounts=values)
        assert f"Incorrect type for value" in str(e.value)
