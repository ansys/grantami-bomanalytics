from ..common import pytest, queries, check_query_manager_attributes


@pytest.mark.parametrize("query_type", [queries.MaterialImpactedSubstancesQuery, queries.MaterialComplianceQuery])
class TestAddMaterialIDs:
    @pytest.mark.parametrize("material_ids", [[],
                                              ["One Material ID"],
                                              ["Two", "Material IDs"],
                                              {"Set", "Material IDs"}])
    def test_correct_types(self, query_type, material_ids):
        query = query_type().with_material_ids(material_ids)
        assert isinstance(query, query_type)
        assert check_query_manager_attributes(
            query,
            ["record_guid", "record_history_guid", "record_history_identity"],
            "material_id",
            material_ids,
        )

    @pytest.mark.parametrize("material_ids", ["String", 12, ["HeterogeneousList", 34], {56, "Heterogeneous set"}])
    def test_wrong_types(self, query_type, material_ids):
        with pytest.raises(TypeError):
            query_type().with_material_ids(material_ids)
            query_type().with_material_ids(material_ids=material_ids)
