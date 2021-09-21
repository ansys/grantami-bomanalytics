import pytest
from .common import (
    RECORD_QUERY_TYPES,
    COMPLIANCE_QUERY_TYPES,
    SUBSTANCE_QUERY_TYPES,
    ALL_QUERY_TYPES,
    TEST_HISTORY_IDS,
    TEST_GUIDS,
    STK_OBJECT,
)


@pytest.mark.parametrize("query_type", RECORD_QUERY_TYPES)
class TestAddPropertiesToRecordQueries:
    @pytest.mark.parametrize("test_values", TEST_GUIDS)
    def test_record_guids(self, query_type, test_values):
        query = query_type().add_record_guids(test_values)
        assert isinstance(query, query_type)
        assert len(query._items) == len(test_values)
        for idx, guid in enumerate(test_values):
            assert query._items[idx].record_guid == guid
            assert not query._items[idx].record_history_guid
            assert not query._items[idx].record_history_identity

    @pytest.mark.parametrize("test_values", TEST_GUIDS)
    def test_record_history_guids(self, query_type, test_values):
        query = query_type().add_record_history_guids(test_values)
        assert isinstance(query, query_type)
        assert len(query._items) == len(test_values)
        for idx, guid in enumerate(test_values):
            assert query._items[idx].record_history_guid == guid
            assert not query._items[idx].record_guid
            assert not query._items[idx].record_history_identity

    @pytest.mark.parametrize("test_values", TEST_HISTORY_IDS)
    def test_record_history_ids(self, query_type, test_values):
        query = query_type().add_record_history_ids(test_values)
        assert isinstance(query, query_type)
        assert len(query._items) == len(test_values)
        for idx, id in enumerate(test_values):
            assert query._items[idx].record_history_identity == id
            assert not query._items[idx].record_guid
            assert not query._items[idx].record_history_guid

    @pytest.mark.parametrize("test_values", TEST_HISTORY_IDS[1:])
    def test_record_guids_wrong_type(self, query_type, test_values):
        with pytest.raises(TypeError) as e:
            query_type().add_record_guids(test_values)
        assert "Incorrect type for value" in str(e.value)
        with pytest.raises(TypeError) as e:
            query_type().add_record_guids(record_guids=test_values)
        assert "Incorrect type for value" in str(e.value)

    @pytest.mark.parametrize("test_values", TEST_HISTORY_IDS[1:])
    def test_record_history_guids_wrong_type(self, query_type, test_values):
        with pytest.raises(TypeError) as e:
            query_type().add_record_history_guids(test_values)
        assert "Incorrect type for value" in str(e.value)
        with pytest.raises(TypeError) as e:
            query_type().add_record_history_guids(record_history_guids=test_values)
        assert "Incorrect type for value" in str(e.value)

    @pytest.mark.parametrize("test_values", TEST_GUIDS[1:])
    def test_record_history_ids_wrong_type(self, query_type, test_values):
        with pytest.raises(TypeError) as e:
            query_type().add_record_history_ids(test_values)
        assert "Incorrect type for value" in str(e.value)
        with pytest.raises(TypeError) as e:
            query_type().add_record_history_ids(record_history_identities=test_values)
        assert "Incorrect type for value" in str(e.value)

    def test_stk_object(self, query_type):
        query = query_type().add_stk_records(STK_OBJECT)
        assert isinstance(query, query_type)
        assert len(query._items) == len(STK_OBJECT)
        for idx, stk_record in enumerate(STK_OBJECT):
            assert query._items[idx].record_guid == stk_record["record_guid"]
            assert not query._items[idx].record_history_identity
            assert not query._items[idx].record_history_guid


class TestAddIndicators:
    @pytest.mark.parametrize("query_type", COMPLIANCE_QUERY_TYPES)
    def test_compliance_query_success(self, query_type, indicators):
        query = query_type().add_indicators(indicators)
        assert len(query._indicators) == len(indicators)
        for indicator in indicators:
            assert query._indicators[indicator.name] == indicator

    @pytest.mark.parametrize("query_type", COMPLIANCE_QUERY_TYPES)
    def test_compliance_query_wrong_type_fails(self, query_type, legislations):
        with pytest.raises(TypeError) as e:
            query_type().add_indicators(legislations)
        assert "Incorrect type for value" in str(e.value)
        with pytest.raises(TypeError) as e:
            query_type().add_indicators(indicators=legislations)
        assert "Incorrect type for value" in str(e.value)

    @pytest.mark.parametrize("query_type", SUBSTANCE_QUERY_TYPES)
    def test_impacted_substances_query_attribute_error(self, query_type, indicators):
        with pytest.raises(AttributeError):
            query_type().add_indicators(indicators)


class TestAddLegislations:
    @pytest.mark.parametrize("query_type", SUBSTANCE_QUERY_TYPES)
    def test_impacted_substances_query_success(self, query_type, legislations):
        query = query_type().add_legislations(legislations)
        assert len(query._legislations) == len(legislations)
        for idx, legislation in enumerate(legislations):
            assert query._legislations[idx] == legislation

    @pytest.mark.parametrize("query_type", SUBSTANCE_QUERY_TYPES)
    def test_impacted_substances_query_wrong_type_fails(self, query_type, indicators):
        with pytest.raises(TypeError) as e:
            query_type().add_legislations(indicators)
        assert "Incorrect type for value" in str(e.value)
        with pytest.raises(TypeError) as e:
            query_type().add_legislations(legislations=indicators)
        assert "Incorrect type for value" in str(e.value)

    @pytest.mark.parametrize("query_type", COMPLIANCE_QUERY_TYPES)
    def test_compliance_query_attribute_error(self, query_type, legislations):
        with pytest.raises(AttributeError):
            query_type().add_legislations(legislations)


@pytest.mark.parametrize("query_type", ALL_QUERY_TYPES)
class TestBatchSize:
    @pytest.mark.parametrize("batch_size", [5, 5000])
    def test_correct_types_and_values(
        self,
        query_type,
        batch_size,
    ):
        query = query_type().set_batch_size(batch_size)
        assert query._batch_size == batch_size

    @pytest.mark.parametrize("batch_size", [0, -25])
    def test_incorrect_values(self, query_type, batch_size):
        query = query_type()
        with pytest.raises(ValueError) as e:
            query.set_batch_size(batch_size)
        assert "Batch must be a positive integer" in str(e.value)
        with pytest.raises(ValueError) as e:
            query.set_batch_size(batch_size=batch_size)
        assert "Batch must be a positive integer" in str(e.value)

    @pytest.mark.parametrize("batch_size", [20.25, "5", None])
    def test_incorrect_types(
        self,
        query_type,
        batch_size,
    ):
        query = query_type()
        with pytest.raises(TypeError) as e:
            query.set_batch_size(batch_size)
        assert "Incorrect type for value" in str(e.value)
        with pytest.raises(TypeError) as e:
            query.set_batch_size(batch_size=batch_size)
        assert "Incorrect type for value" in str(e.value)
