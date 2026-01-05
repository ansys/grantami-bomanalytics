# Copyright (C) 2022 - 2026 ANSYS, Inc. and/or its affiliates.
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

from dataclasses import dataclass
import re

import pytest

from ansys.grantami.bomanalytics import queries

from .inputs import example_boms


class MockRecordDefinition:
    @dataclass
    class Definition:
        reference_type: str
        reference_value: str

    def __init__(self, reference_type: str, reference_value: str):
        self._definition = self.Definition(reference_type, reference_value)

    @property
    def _record_reference(self) -> str:
        return {"reference_type": self._definition.reference_type, "reference_value": self._definition.reference_value}


class TestRecordArgManager:
    def test_uninitialized_configuration(self):
        am = queries._RecordQueryDataManager()
        assert am.batch_size is None
        assert am.item_type_name == ""
        assert am.__repr__() == "<_RecordQueryDataManager {record_type_name: None, batch_size: None}, length = 0>"

    def test_no_record_type_raises_runtime_error(self):
        am = queries._RecordQueryDataManager(batch_size=100)
        with pytest.raises(RuntimeError) as e:
            next(am.batched_arguments)
        assert '"item_type_name" must be populated before record arguments can be generated.' in str(e.value)

    def test_no_batch_size_raises_runtime_error(self):
        am = queries._RecordQueryDataManager(item_type_name="TEST_RECORD")
        with pytest.raises(RuntimeError) as e:
            next(am.batched_arguments)
        assert '"batch_size" must be populated before record arguments can be generated.' in str(e.value)

    def test_initialized_arg_manager_no_records(self):
        am = queries._RecordQueryDataManager(batch_size=100, item_type_name="TEST_RECORD")
        args = list(am.batched_arguments)
        assert args == []

    @pytest.mark.parametrize("reference_type", ["test_string", None])
    @pytest.mark.parametrize("reference_value", ["test_string", None])
    def test_add_null_record_ref_to_arg_manager_runtime_error(self, reference_type, reference_value):
        if reference_type and reference_value:  # We don't want to test the case where both are truthy
            return
        am = queries._RecordQueryDataManager()
        record_def = MockRecordDefinition(reference_type=reference_type, reference_value=reference_value)
        with pytest.raises(TypeError) as e:
            am.append_record_definition(record_def)
        assert "Attempted to add a RecordDefinition-derived object with a null record reference to a query." in str(
            e.value
        )

    @pytest.mark.parametrize("number_of_records", [1, 2, 3, 4, 49, 50, 51, 99, 100, 101, 200, 500, 1000])
    @pytest.mark.parametrize("batch_size", [1, 2, 50, 100])
    def test_argument_batching(self, number_of_records, batch_size):
        am = queries._RecordQueryDataManager(batch_size=batch_size, item_type_name="TEST_RECORD")
        for idx in range(number_of_records):
            rec_def = MockRecordDefinition(reference_type="Ref Type", reference_value=f"Ref Val{idx}")
            am.append_record_definition(rec_def)
        args = list(am.batched_arguments)

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
        am = queries._RecordQueryDataManager(batch_size=100, item_type_name="TEST_NAME")
        assert am.__repr__() == '<_RecordQueryDataManager {record_type_name: "TEST_NAME", batch_size: 100}, length = 0>'

        am.append_record_definition(MockRecordDefinition(reference_type="type", reference_value="12345"))
        assert am.__repr__() == '<_RecordQueryDataManager {record_type_name: "TEST_NAME", batch_size: 100}, length = 1>'


all_bom_formats = [item for item in queries._BomFormat]


class TestBomArgManager:
    @pytest.mark.parametrize("bom_version", ["bom_xml1711", "bom_xml2301"])
    def test_uninitialized_configuration(self, bom_version):
        am = queries._BomQueryDataManager(all_bom_formats)
        assert am._item_definitions == []
        assert am.__repr__() == "<_BomQueryDataManager>"

    @pytest.mark.parametrize("bom_key", ["bom-1711", "sustainability-bom-2301", "sustainability-bom-2412"])
    def test_add_bom(self, bom_key: str):
        am = queries._BomQueryDataManager(all_bom_formats)
        bom = example_boms[bom_key].content
        am.bom = bom
        assert am._item_definitions[0] == bom
        assert am.batched_arguments == [{"bom_xml": bom}]
        assert am.__repr__() == f'<_BomQueryDataManager {{bom: "{bom[:100]}"}}>'


class TestBomNameSpaceParsing:
    @pytest.mark.parametrize(
        ["bom_key", "bom_format"],
        [
            ("sustainability-bom-2301", queries._BomFormat.bom_xml2301),
            ("sustainability-bom-2412", queries._BomFormat.bom_xml2412),
            ("bom-1711", queries._BomFormat.bom_xml1711),
            ("compliance-bom-1711", queries._BomFormat.bom_xml1711),
        ],
    )
    def test_valid_namespace_parsing(self, bom_key, bom_format):
        bom = example_boms[bom_key].content
        parsed_format = queries._BomQueryDataManager(all_bom_formats)._validate_bom(bom)
        assert parsed_format == bom_format

    def test_not_valid_xml(self):
        bom = example_boms["bom-1711"].content.replace("<Components>", "<Component>")
        with pytest.raises(ValueError, match="BoM provided as input is not valid XML"):
            queries._BomQueryDataManager(all_bom_formats).bom = bom

    def test_xml_but_not_a_bom(self):
        bom = example_boms["bom-1711"].content.replace("PartsEco", "SomeOtherRoot")
        with pytest.raises(
            ValueError, match="Invalid input BoM. Ensure the document is compliant with the expected XML schema"
        ):
            queries._BomQueryDataManager(all_bom_formats).bom = bom

    def test_xml_bom_but_unknown_namespace(self):
        bom = example_boms["sustainability-bom-2301"].content.replace(
            "http://www.grantadesign.com/23/01/BillOfMaterialsEco", "UnknownNamespace"
        )
        with pytest.raises(
            ValueError, match="Invalid input BoM. Ensure the document is compliant with the expected XML schema"
        ):
            queries._BomQueryDataManager(all_bom_formats).bom = bom

    def test_xml_bom_but_not_version_supported_by_query(self):
        expected_error = re.escape(
            "bom_xml2301 (http://www.grantadesign.com/23/01/BillOfMaterialsEco) is not supported by this query."
        )
        with pytest.raises(ValueError, match=expected_error):
            queries._BomQueryDataManager([queries._BomFormat.bom_xml1711]).bom = example_boms[
                "sustainability-bom-2301"
            ].content


def test_add_boms_sequentially():
    # Check that properties are updated as expected when overwriting a bom with a bom from another version
    bom_manager = queries._BomQueryDataManager(all_bom_formats)
    # assert query.item_type_name is None  # TODO attribute does not exist
    bom_1 = example_boms["bom-1711"].content
    bom_manager.bom = bom_1
    assert bom_manager.item_type_name == "bom_xml"
    assert bom_manager._item_definitions[0] == bom_1

    bom_2 = example_boms["sustainability-bom-2301"].content
    bom_manager.bom = bom_2
    assert bom_manager.item_type_name == "bom_xml"
    assert bom_manager._item_definitions[0] == bom_2


class TestBomFormatEnum:
    @pytest.mark.parametrize(
        "value",
        [
            "http://www.grantadesign.com/17/11/BillOfMaterialsEco",
            "http://www.grantadesign.com/23/01/BillOfMaterialsEco",
        ],
    )
    def test_valid_values_by_namespace(self, value):
        queries._BomFormat(value)

    def test_invalid_value(self):
        value = "SomeOtherNotValidValue"
        with pytest.raises(ValueError, match=f"'{value}' is not a valid _BomFormat"):
            queries._BomFormat(value)

    def test_by_name(self):
        _ = queries._BomFormat["bom_xml1711"]
