from ..common import pytest, queries, check_query_manager_attributes


@pytest.mark.parametrize("query_type", [queries.PartComplianceQuery, queries.PartImpactedSubstancesQuery])
class TestAddPartNumbers:
    @pytest.mark.parametrize("part_numbers", [[],
                                              ["One part number"],
                                              ["Two", "Part numbers"],
                                              {"Set", "Part Numbers"}])
    def test_correct_types(self, query_type, part_numbers):
        query = query_type().with_part_numbers(part_numbers)
        assert isinstance(query, query_type)
        assert check_query_manager_attributes(
            query,
            ["record_guid", "record_history_guid", "record_history_identity"],
            "part_number",
            part_numbers,
        )

    @pytest.mark.parametrize("part_numbers", ["String", 12, ["HeterogeneousList", 34], {56, "Heterogeneous set"}])
    def test_wrong_types(self, query_type, part_numbers):
        with pytest.raises(TypeError):
            query_type().with_part_numbers(part_numbers)
            query_type().with_part_numbers(part_numbers=part_numbers)
