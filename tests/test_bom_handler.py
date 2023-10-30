from difflib import context_diff
from pathlib import Path
import re
from typing import Any, Dict

from lxml import etree
import pytest

from ansys.grantami.bomanalytics import BoMHandler
from ansys.grantami.bomanalytics.bom_types import BaseType, BillOfMaterials

from .inputs import drill_bom_2301, large_bom_2301, sample_bom_1711, sample_sustainability_bom_2301


class _TestableBoMHandler(BoMHandler):
    def __init__(self, default_namespace: str, namespace_mapping: Dict[str, str]):
        super().__init__()
        self._default_namespace = default_namespace
        self._namespace_mapping = namespace_mapping

    def dump_bom(self, bom: BillOfMaterials) -> str:
        raw = super().dump_bom(bom)

        root = etree.fromstring(raw)
        exisitng_ns = root.nsmap

        default_namespace_source = next(k for k, v in exisitng_ns.items() if v == self._default_namespace)

        # Set default namespace
        if default_namespace_source != "":
            raw = raw.replace(f"{default_namespace_source}:", "")
            raw = raw.replace(f":{default_namespace_source}", "")

        # Rename other namespaces
        for new_prefix, uri in self._namespace_mapping.items():
            prefix = next((k for k, v in exisitng_ns.items() if v == uri), None)
            if prefix is None:
                continue

            raw = raw.replace(f"{prefix}:", f"{new_prefix}:")
            raw = raw.replace(f":{prefix}", f":{new_prefix}")
        return raw


class TestRoundTripBoM:
    _bom_location = Path(__file__).parent / "inputs"
    _namespace_map = {"gbt": "http://www.grantadesign.com/12/05/GrantaBaseTypes"}
    _default_namespace = "http://www.grantadesign.com/23/01/BillOfMaterialsEco"

    @staticmethod
    def _compare_boms(*, source_bom: str, result_bom: str):
        source_lines = source_bom.splitlines()
        result_lines = result_bom.splitlines()

        output_lines = []

        diff_result = context_diff(source_lines, result_lines)

        for diff_item in diff_result:
            output_lines.append(diff_item)
        return output_lines

    @pytest.mark.parametrize(
        "input_bom",
        [
            pytest.param(drill_bom_2301, id="drill"),
            pytest.param(large_bom_2301, id="large_bom"),
        ],
    )
    def test_roundtrip_with_assertions(self, input_bom: str):
        bom_handler = _TestableBoMHandler(
            default_namespace=self._default_namespace, namespace_mapping=self._namespace_map
        )
        deserialized_bom = bom_handler.load_bom_from_text(input_bom)
        output_bom = bom_handler.dump_bom(deserialized_bom)

        diff = self._compare_boms(source_bom=input_bom, result_bom=output_bom)

        assert len(diff) == 0, "\n".join(diff)

    @pytest.mark.parametrize(
        "input_bom",
        [
            pytest.param(drill_bom_2301, id="drill"),
            pytest.param(large_bom_2301, id="large_bom"),
            pytest.param(sample_sustainability_bom_2301, id="sustainability_bom"),
        ],
    )
    def test_roundtrip_parsing_succeeds(self, input_bom: str):
        bom_handler = BoMHandler()
        deserialized_bom = bom_handler.load_bom_from_text(input_bom)

        rendered_bom = bom_handler.dump_bom(deserialized_bom)
        bom_handler.load_bom_from_text(rendered_bom)


class TestBoMDeserialization:
    @pytest.fixture(scope="class")
    def simple_bom(self):
        # 17/11 and 23/01 are quite similar, and in the context of this particular BoM and test, substituting the
        # namespace is sufficient to obtain a valid 23/01 BoM.
        input_bom = sample_bom_1711.replace(
            "http://www.grantadesign.com/17/11/BillOfMaterialsEco",
            "http://www.grantadesign.com/23/01/BillOfMaterialsEco",
        )
        bom_handler = BoMHandler()
        yield bom_handler.load_bom_from_text(input_bom)

    def get_field(self, obj: BaseType, p_path: str) -> Any:
        tokens = p_path.split("/")
        while True:
            try:
                next_token = tokens.pop(0)
                if "[" in next_token:
                    index_token = re.search(r"([^\[]+)\[(\d+)]", next_token)
                    if index_token is None:
                        raise KeyError(f"Token {next_token} is invalid, index entries must be of the form [0]")
                    field = index_token.groups()[0]
                    index = index_token.groups()[1]
                    obj = getattr(obj, field, None)
                    if obj is None and len(tokens) > 0:
                        raise ValueError(f"Item {obj} has no property {next_token}")
                    obj = obj[int(index)]
                else:
                    obj = getattr(obj, next_token, None)
                if obj is None and len(tokens) > 0:
                    raise ValueError(f"Item {obj} has no property {next_token}")
            except IndexError:
                return obj

    @pytest.mark.parametrize(
        ("query", "value"),
        [
            ("internal_id", "B0"),
            ("notes/notes", "Part with substance"),
            ("notes/product_name", "Part with substance"),
            ("components[0]/quantity/unit", "Each"),
            ("components[0]/quantity/value", pytest.approx(2.0)),
            ("components[0]/part_number", "123456789"),
            ("components[0]/part_name", "Part One"),
            ("components[0]/components[0]/quantity/unit", "Each"),
            ("components[0]/components[0]/quantity/value", pytest.approx(1.0)),
            ("components[0]/components[0]/mass_per_unit_of_measure/unit", "kg/Part"),
            ("components[0]/components[0]/mass_per_unit_of_measure/value", pytest.approx(2.0)),
            ("components[0]/components[0]/part_number", "987654321"),
            ("components[0]/components[0]/part_name", "New Part One"),
            ("components[0]/components[0]/substances[0]/percentage", pytest.approx(66.0)),
            ("components[0]/components[0]/substances[0]/mi_substance_reference/db_key", "MI_Restricted_Substances"),
            (
                "components[0]/components[0]/substances[0]/mi_substance_reference/record_history_guid",
                "af1cb650-6db5-49d6-b4a2-0eee9a090207",
            ),
            ("components[0]/components[0]/substances[0]/name", "Lead oxide"),
            ("components[0]/components[1]/quantity/unit", "Each"),
            ("components[0]/components[1]/quantity/value", pytest.approx(1.0)),
            ("components[0]/components[1]/mass_per_unit_of_measure/unit", "kg/Part"),
            ("components[0]/components[1]/mass_per_unit_of_measure/value", pytest.approx(2.0)),
            ("components[0]/components[1]/part_number", "3333"),
            ("components[0]/components[1]/part_name", "Part Two"),
            ("components[0]/components[1]/materials[0]/percentage", pytest.approx(80.0)),
            ("components[0]/components[1]/materials[0]/mi_material_reference/db_key", "MI_Restricted_Substances"),
            (
                "components[0]/components[1]/materials[0]/mi_material_reference/record_history_guid",
                "ab4147f6-0e97-47f0-be53-cb5d17dfa82b",
            ),
        ],
    )
    def test_simple_bom(self, simple_bom: BillOfMaterials, query: str, value: Any) -> None:
        deserialized_field = self.get_field(simple_bom, query)
        assert deserialized_field == value
