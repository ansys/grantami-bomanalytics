from .common import queries, pytest, dataclass, sample_bom


class MockRecordDefinition:
    @dataclass
    class Definition:
        reference_type: str
        reference_value: str

    def __init__(self, reference_type: str, reference_value: str):
        self.definition = self.Definition(reference_type, reference_value)


class TestRecordArgManager:
    def test_uninitialized_configuration(self):
        am = queries._RecordArgumentManager()
        assert am.batch_size is None
        assert am.item_type_name is None
        assert am.__repr__() == "<_RecordArgumentManager {record_type_name: None, batch_size: None}, length = 0>"

    def test_no_record_type_raises_runtime_error(self):
        am = queries._RecordArgumentManager(batch_size=100)
        with pytest.raises(RuntimeError) as e:
            next(am.batched_record_arguments)
        assert '"item_type_name" must be populated before record arguments can be generated.' in str(e.value)

    def test_no_batch_size_raises_runtime_error(self):
        am = queries._RecordArgumentManager(item_type_name="TEST_RECORD")
        with pytest.raises(RuntimeError) as e:
            next(am.batched_record_arguments)
        assert '"batch_size" must be populated before record arguments can be generated.' in str(e.value)

    def test_initialized_arg_manager_no_records(self):
        am = queries._RecordArgumentManager(batch_size=100, item_type_name="TEST_RECORD")
        args = list(am.batched_record_arguments)
        assert args == []

    @pytest.mark.parametrize("number_of_records", [1, 2, 3, 4, 49, 50, 51, 99, 100, 101, 200, 500, 1000])
    @pytest.mark.parametrize("batch_size", [1, 2, 50, 100])
    def test_argument_batching(self, number_of_records, batch_size):
        am = queries._RecordArgumentManager(batch_size=batch_size, item_type_name="TEST_RECORD")
        for idx in range(number_of_records):
            rec_def = MockRecordDefinition(reference_type="Ref Type", reference_value=f"Ref Val{idx}")
            am.append_record_definition(rec_def)
        args = list(am.batched_record_arguments)

        if number_of_records % am.batch_size == 0:
            epsilon = 0
        else:
            epsilon = 1
        number_of_batches = number_of_records // batch_size + epsilon
        assert len(args) == number_of_batches
        for batch in args[:-1]:
            assert len(batch["TEST_RECORD"]) == batch_size
        assert len(args[-1]["TEST_RECORD"]) == number_of_records % batch_size or batch_size

    def test_repr(self):
        am = queries._RecordArgumentManager(batch_size=100, item_type_name="TEST_NAME")
        assert am.__repr__() == '<_RecordArgumentManager {record_type_name: "TEST_NAME", batch_size: 100}, length = 0>'

        am.append_record_definition(MockRecordDefinition(reference_type="type", reference_value="12345"))
        assert am.__repr__() == '<_RecordArgumentManager {record_type_name: "TEST_NAME", batch_size: 100}, length = 1>'


class TestBomArgManager:
    def test_uninitialized_configuration(self):
        am = queries._BomArgumentManager()
        assert isinstance(am._items, str)
        assert am._items == ""
        assert am.__repr__() == '<_BomArgumentManager {bom: ""}>'

    @pytest.mark.parametrize("bom", ["Test bom less than 100 chars", sample_bom])
    def test_add_bom(self, bom):
        am = queries._BomArgumentManager()
        am._items = bom
        assert am._items == bom
        assert am.bom_argument == {"bom_xml1711": bom}
        assert am.__repr__() == f'<_BomArgumentManager {{bom: "{bom[:100]}"}}>'
