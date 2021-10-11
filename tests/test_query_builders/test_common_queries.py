from .common import (
    pytest,
    RECORD_QUERY_TYPES,
    COMPLIANCE_QUERY_TYPES,
    SUBSTANCE_QUERY_TYPES,
    ALL_QUERY_TYPES,
    TEST_HISTORY_IDS,
    TEST_GUIDS,
    STK_OBJECT,
    LEGISLATIONS,
    INDICATORS,
)
from ansys.granta.bom_analytics.queries import Yaml


@pytest.mark.parametrize("query_type", RECORD_QUERY_TYPES)
class TestAddPropertiesToRecordQueries:
    @pytest.mark.parametrize("test_values", TEST_GUIDS)
    def test_record_guids(self, query_type, test_values):
        query = query_type().with_record_guids(test_values)
        assert isinstance(query, query_type)
        assert len(query._record_argument_manager._items) == len(test_values)
        for idx, guid in enumerate(test_values):
            assert query._record_argument_manager._items[idx].record_guid == guid
            assert not query._record_argument_manager._items[idx].record_history_guid
            assert not query._record_argument_manager._items[idx].record_history_identity

    @pytest.mark.parametrize("test_values", TEST_GUIDS)
    def test_record_history_guids(self, query_type, test_values):
        query = query_type().with_record_history_guids(test_values)
        assert isinstance(query, query_type)
        assert len(query._record_argument_manager._items) == len(test_values)
        for idx, guid in enumerate(test_values):
            assert query._record_argument_manager._items[idx].record_history_guid == guid
            assert not query._record_argument_manager._items[idx].record_guid
            assert not query._record_argument_manager._items[idx].record_history_identity

    @pytest.mark.parametrize("test_values", TEST_HISTORY_IDS)
    def test_record_history_ids(self, query_type, test_values):
        query = query_type().with_record_history_ids(test_values)
        assert isinstance(query, query_type)
        assert len(query._record_argument_manager._items) == len(test_values)
        for idx, id in enumerate(test_values):
            assert query._record_argument_manager._items[idx].record_history_identity == id
            assert not query._record_argument_manager._items[idx].record_guid
            assert not query._record_argument_manager._items[idx].record_history_guid

    @pytest.mark.parametrize("test_values", TEST_HISTORY_IDS[1:])
    def test_record_guids_wrong_type(self, query_type, test_values):
        with pytest.raises(TypeError) as e:
            query_type().with_record_guids(test_values)
        assert "Incorrect type for value" in str(e.value)
        with pytest.raises(TypeError) as e:
            query_type().with_record_guids(record_guids=test_values)
        assert "Incorrect type for value" in str(e.value)

    @pytest.mark.parametrize("test_values", TEST_HISTORY_IDS[1:])
    def test_record_history_guids_wrong_type(self, query_type, test_values):
        with pytest.raises(TypeError) as e:
            query_type().with_record_history_guids(test_values)
        assert "Incorrect type for value" in str(e.value)
        with pytest.raises(TypeError) as e:
            query_type().with_record_history_guids(record_history_guids=test_values)
        assert "Incorrect type for value" in str(e.value)

    @pytest.mark.parametrize("test_values", TEST_GUIDS[1:])
    def test_record_history_ids_wrong_type(self, query_type, test_values):
        with pytest.raises(TypeError) as e:
            query_type().with_record_history_ids(test_values)
        assert "Incorrect type for value" in str(e.value)
        with pytest.raises(TypeError) as e:
            query_type().with_record_history_ids(record_history_identities=test_values)
        assert "Incorrect type for value" in str(e.value)

    def test_no_items_raises_warning(self, query_type):
        query = query_type()
        with pytest.warns(RuntimeWarning) as w:
            query._validate_items()
        assert len(w) == 1
        assert (
            f"No {query._record_argument_manager.record_type_name} have been added to the query. Server response will be"
            f" empty." in w[0].message.args[0]
        )

    def test_stk_object(self, query_type):
        query = query_type().with_stk_records(STK_OBJECT)
        assert isinstance(query, query_type)
        assert len(query._record_argument_manager._items) == len(STK_OBJECT)
        for idx, stk_record in enumerate(STK_OBJECT):
            assert query._record_argument_manager._items[idx].record_guid == stk_record["record_guid"]
            assert not query._record_argument_manager._items[idx].record_history_identity
            assert not query._record_argument_manager._items[idx].record_history_guid


class TestAddIndicators:
    @pytest.mark.parametrize("query_type", COMPLIANCE_QUERY_TYPES)
    def test_compliance_query_success(self, query_type):
        query = query_type().with_indicators(INDICATORS)
        assert len(query._indicators) == len(INDICATORS)
        for indicator in INDICATORS:
            assert query._indicators[indicator.name] is indicator

    @pytest.mark.parametrize("query_type", COMPLIANCE_QUERY_TYPES)
    def test_compliance_query_wrong_type_fails(self, query_type):
        with pytest.raises(TypeError) as e:
            query_type().with_indicators(LEGISLATIONS)
        assert "Incorrect type for value" in str(e.value)
        with pytest.raises(TypeError) as e:
            query_type().with_indicators(indicators=LEGISLATIONS)
        assert "Incorrect type for value" in str(e.value)

    @pytest.mark.parametrize("query_type", SUBSTANCE_QUERY_TYPES)
    def test_impacted_substances_query_attribute_error(self, query_type):
        with pytest.raises(AttributeError):
            query_type().with_indicators(INDICATORS)


class TestAddLegislations:
    @pytest.mark.parametrize("query_type", SUBSTANCE_QUERY_TYPES)
    def test_impacted_substances_query_success(self, query_type):
        query = query_type().with_legislations(LEGISLATIONS)
        assert len(query._legislations) == len(LEGISLATIONS)
        for idx, legislation in enumerate(LEGISLATIONS):
            assert query._legislations[idx] == legislation

    @pytest.mark.parametrize("query_type", SUBSTANCE_QUERY_TYPES)
    def test_impacted_substances_query_wrong_type_fails(self, query_type):
        with pytest.raises(TypeError) as e:
            query_type().with_legislations(INDICATORS)
        assert "Incorrect type for value" in str(e.value)
        with pytest.raises(TypeError) as e:
            query_type().with_legislations(legislations=INDICATORS)
        assert "Incorrect type for value" in str(e.value)

    @pytest.mark.parametrize("query_type", COMPLIANCE_QUERY_TYPES)
    def test_compliance_query_attribute_error(self, query_type):
        with pytest.raises(AttributeError):
            query_type().with_legislations(LEGISLATIONS)


@pytest.mark.parametrize("query_type", ALL_QUERY_TYPES)
class TestBatchSize:
    @pytest.mark.parametrize("batch_size", [0, -25])
    def test_incorrect_values(self, query_type, batch_size):
        query = query_type()
        with pytest.raises(ValueError) as e:
            query.with_batch_size(batch_size)
        assert "Batch must be a positive integer" in str(e.value)
        with pytest.raises(ValueError) as e:
            query.with_batch_size(batch_size=batch_size)
        assert "Batch must be a positive integer" in str(e.value)

    @pytest.mark.parametrize("batch_size", [20.25, "5", None])
    def test_incorrect_types(
        self,
        query_type,
        batch_size,
    ):
        query = query_type()
        with pytest.raises(TypeError) as e:
            query.with_batch_size(batch_size)
        assert "Incorrect type for value" in str(e.value)
        with pytest.raises(TypeError) as e:
            query.with_batch_size(batch_size=batch_size)
        assert "Incorrect type for value" in str(e.value)


def test_yaml(connection):
    assert Yaml.get_yaml(connection)
