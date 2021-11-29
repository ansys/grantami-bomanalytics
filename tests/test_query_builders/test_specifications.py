from ..common import (
    pytest,
    queries,
    check_query_manager_attributes,
)


@pytest.mark.parametrize(
    "query_type", [queries.SpecificationComplianceQuery, queries.SpecificationImpactedSubstancesQuery]
)
class TestAddSpecIDs:
    @pytest.mark.parametrize("spec_ids", [[],
                                          ["One spec id"],
                                          ["Two", "Spec IDs"],
                                          {"Set", "Spec IDs"}])
    def test_correct_types(self, query_type, spec_ids):
        query = query_type().with_specification_ids(spec_ids)
        assert isinstance(query, query_type)
        assert check_query_manager_attributes(
            query,
            ["record_guid", "record_history_guid", "record_history_identity"],
            "specification_id",
            spec_ids,
        )

    @pytest.mark.parametrize("spec_ids", ["String",
                                          12,
                                          ["HeterogeneousList", 34],
                                          {56, "Heterogeneous set"}])
    def test_wrong_types(self, query_type, spec_ids):
        with pytest.raises(TypeError):
            query_type().with_specification_ids(spec_ids)
            query_type().with_specification_ids(specification_ids=spec_ids)
