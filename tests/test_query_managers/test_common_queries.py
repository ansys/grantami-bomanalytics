import pytest
from ansys.granta.bom_analytics import (
    MaterialImpactedSubstanceQuery,
    MaterialComplianceQuery,
    PartImpactedSubstanceQuery,
    PartComplianceQuery,
    SpecificationImpactedSubstanceQuery,
    SpecificationComplianceQuery,
    SubstanceComplianceQuery,
    BomImpactedSubstancesQuery,
    BomComplianceQuery,
)

RECORD_QUERY_TYPES = [
    MaterialImpactedSubstanceQuery,
    MaterialComplianceQuery,
    PartImpactedSubstanceQuery,
    PartComplianceQuery,
    SpecificationImpactedSubstanceQuery,
    SpecificationComplianceQuery,
    SubstanceComplianceQuery,
]

COMPLIANCE_QUERY_TYPES = [
    MaterialComplianceQuery,
    PartComplianceQuery,
    SpecificationComplianceQuery,
    SubstanceComplianceQuery,
    BomComplianceQuery,
]
SUBSTANCE_QUERY_TYPES = [
    MaterialImpactedSubstanceQuery,
    PartImpactedSubstanceQuery,
    SpecificationImpactedSubstanceQuery,
    BomImpactedSubstancesQuery,
]
ALL_QUERY_TYPES = COMPLIANCE_QUERY_TYPES + SUBSTANCE_QUERY_TYPES


TEST_GUIDS = [
    [],
    ["00000000-0000-0000-0000-000000000000"],
    [
        "00000000-0123-4567-89AB-000000000000",
        "00000000-0000-0000-0000-CDEF01234567",
    ],
]


TEST_HISTORY_IDS = [
    [],
    [123],
    [
        456,
        789,
    ],
]


@pytest.mark.parametrize("query_type", RECORD_QUERY_TYPES)
class TestAddPropertiesToRecordQueries:
    @pytest.mark.parametrize("test_values", TEST_GUIDS)
    def test_record_guids(self, query_type, test_values, connection):
        query = query_type(connection).add_record_guids(test_values)
        assert isinstance(query, query_type)
        assert len(query._items) == len(test_values)
        for idx, guid in enumerate(test_values):
            assert query._items[idx].record_guid == guid
            assert not query._items[idx].record_history_guid
            assert not query._items[idx].record_history_identity

    @pytest.mark.parametrize("test_values", TEST_HISTORY_IDS[1:])
    def test_record_guids_wrong_type(self, query_type, test_values, connection):
        with pytest.raises(TypeError) as e:
            query_type(connection).add_record_guids(test_values)
        assert "Incorrect type for value" in str(e.value)
        with pytest.raises(TypeError) as e:
            query_type(connection).add_record_guids(record_guids=test_values)
        assert "Incorrect type for value" in str(e.value)

    @pytest.mark.parametrize("test_values", TEST_GUIDS)
    def test_record_history_guids(self, query_type, test_values, connection):
        query = query_type(connection).add_record_history_guids(test_values)
        assert isinstance(query, query_type)
        assert len(query._items) == len(test_values)
        for idx, guid in enumerate(test_values):
            assert query._items[idx].record_history_guid == guid
            assert not query._items[idx].record_guid
            assert not query._items[idx].record_history_identity

    @pytest.mark.parametrize("test_values", TEST_HISTORY_IDS[1:])
    def test_record_history_guids_wrong_type(self, query_type, test_values, connection):
        with pytest.raises(TypeError) as e:
            query_type(connection).add_record_history_guids(test_values)
        assert "Incorrect type for value" in str(e.value)
        with pytest.raises(TypeError) as e:
            query_type(connection).add_record_history_guids(
                record_history_guids=test_values
            )
        assert "Incorrect type for value" in str(e.value)

    @pytest.mark.parametrize("test_values", TEST_HISTORY_IDS)
    def test_record_history_ids(self, query_type, test_values, connection):
        query = query_type(connection).add_record_history_ids(test_values)
        assert isinstance(query, query_type)
        assert len(query._items) == len(test_values)
        for idx, id in enumerate(test_values):
            assert query._items[idx].record_history_identity == id
            assert not query._items[idx].record_guid
            assert not query._items[idx].record_history_guid

    @pytest.mark.parametrize("test_values", TEST_GUIDS[1:])
    def test_record_history_ids_wrong_type(self, query_type, test_values, connection):
        with pytest.raises(TypeError) as e:
            query_type(connection).add_record_history_ids(test_values)
        assert "Incorrect type for value" in str(e.value)
        with pytest.raises(TypeError) as e:
            query_type(connection).add_record_history_ids(
                record_history_identities=test_values
            )
        assert "Incorrect type for value" in str(e.value)


class TestAddIndicators:
    @pytest.mark.parametrize("query_type", COMPLIANCE_QUERY_TYPES)
    def test_compliance_query_success(self, query_type, indicators, connection):
        query = query_type(connection).add_indicators(indicators)
        assert len(query._indicators) == len(indicators)
        for idx, indicator in enumerate(indicators):
            assert query._indicators[idx] == indicator

    @pytest.mark.parametrize("query_type", COMPLIANCE_QUERY_TYPES)
    def test_compliance_query_wrong_type_fails(
        self, query_type, legislations, connection
    ):
        with pytest.raises(TypeError) as e:
            query_type(connection).add_indicators(legislations)
        assert "Incorrect type for value" in str(e.value)
        with pytest.raises(TypeError) as e:
            query_type(connection).add_indicators(indicators=legislations)
        assert "Incorrect type for value" in str(e.value)

    @pytest.mark.parametrize("query_type", SUBSTANCE_QUERY_TYPES)
    def test_impacted_substances_query_attribute_error(
        self, query_type, indicators, connection
    ):
        with pytest.raises(AttributeError):
            query_type(connection).add_indicators(indicators)


class TestAddLegislations:
    @pytest.mark.parametrize("query_type", SUBSTANCE_QUERY_TYPES)
    def test_impacted_substances_query_success(
        self, query_type, legislations, connection
    ):
        query = query_type(connection).add_legislations(legislations)
        assert len(query._legislations) == len(legislations)
        for idx, legislation in enumerate(legislations):
            assert query._legislations[idx] == legislation

    @pytest.mark.parametrize("query_type", SUBSTANCE_QUERY_TYPES)
    def test_impacted_substances_query_wrong_type_fails(
        self, query_type, indicators, connection
    ):
        with pytest.raises(TypeError) as e:
            query_type(connection).add_legislations(indicators)
        assert "Incorrect type for value" in str(e.value)
        with pytest.raises(TypeError) as e:
            query_type(connection).add_legislations(legislations=indicators)
        assert "Incorrect type for value" in str(e.value)

    @pytest.mark.parametrize("query_type", COMPLIANCE_QUERY_TYPES)
    def test_compliance_query_attribute_error(
        self, query_type, legislations, connection
    ):
        with pytest.raises(AttributeError):
            query_type(connection).add_legislations(legislations)


@pytest.mark.parametrize("query_type", ALL_QUERY_TYPES)
class TestBatchSize:
    @pytest.mark.parametrize("batch_size", [5, 5000])
    def test_correct_types_and_values(self, query_type, batch_size, connection):
        query = query_type(connection).set_batch_size(batch_size)
        assert query.batch_size == batch_size
        assert query._batch_size == batch_size

    @pytest.mark.parametrize("batch_size", [0, -25])
    def test_incorrect_values(self, query_type, batch_size, connection):
        query = query_type(connection)
        with pytest.raises(ValueError) as e:
            query.set_batch_size(batch_size)
        assert "Batch must be a positive integer" in str(e.value)
        with pytest.raises(ValueError) as e:
            query.set_batch_size(value=batch_size)
        assert "Batch must be a positive integer" in str(e.value)

    @pytest.mark.parametrize("batch_size", [20.25, "5", None])
    def test_incorrect_types(self, query_type, batch_size, connection):
        query = query_type(connection)
        with pytest.raises(TypeError) as e:
            query.set_batch_size(batch_size)
        assert "Incorrect type for value" in str(e.value)
        with pytest.raises(TypeError) as e:
            query.set_batch_size(value=batch_size)
        assert "Incorrect type for value" in str(e.value)
