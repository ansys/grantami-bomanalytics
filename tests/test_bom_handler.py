# Copyright (C) 2022 - 2025 ANSYS, Inc. and/or its affiliates.
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

from abc import ABC
from difflib import context_diff
from itertools import product
from pathlib import Path
import re
from typing import Any, Dict, Literal
import uuid

from lxml import etree
import pytest

from ansys.grantami.bomanalytics import BoMHandler
from ansys.grantami.bomanalytics.bom_types import eco2301, eco2412, gbt1205

from .inputs import (
    bom_with_annotations_2301,
    bom_with_annotations_2301_path,
    bom_with_annotations_2412,
    bom_with_annotations_2412_path,
    large_bom_2301,
    large_bom_2301_path,
    large_bom_2412,
    large_bom_2412_path,
    sample_bom_1711,
    sample_sustainability_bom_2301,
    sample_sustainability_bom_2301_path,
    sample_sustainability_bom_2412,
    sample_sustainability_bom_2412_path,
)


class TestRoundTripBoMs:
    @pytest.mark.parametrize(
        "input_bom",
        [
            pytest.param(large_bom_2301, id="large_bom_2301"),
            pytest.param(sample_sustainability_bom_2301, id="sustainability_bom_2301"),
            pytest.param(large_bom_2412, id="large_bom_2412"),
            pytest.param(sample_sustainability_bom_2412, id="sustainability_bom_2412"),
        ],
    )
    @pytest.mark.parametrize("allow_unsupported_data", [True, False])
    def test_roundtrip_from_text_parsing_succeeds(self, input_bom: str, allow_unsupported_data: bool):
        bom_handler = BoMHandler()
        deserialized_bom = bom_handler.load_bom_from_text(input_bom, allow_unsupported_data)

        rendered_bom = bom_handler.dump_bom(deserialized_bom)
        deserialized_bom_roundtriped = bom_handler.load_bom_from_text(rendered_bom)

        assert deserialized_bom == deserialized_bom_roundtriped

    @pytest.mark.parametrize(
        "input_bom",
        [
            pytest.param(bom_with_annotations_2301, id="annotations_2301"),
            pytest.param(bom_with_annotations_2412, id="annotations_2412"),
        ],
    )
    def test_roundtrip_from_text_parsing_succeeds_unsupported_boms_lax(self, input_bom: str):
        bom_handler = BoMHandler()
        deserialized_bom = bom_handler.load_bom_from_text(input_bom, True)

        rendered_bom = bom_handler.dump_bom(deserialized_bom)
        deserialized_bom_roundtriped = bom_handler.load_bom_from_text(rendered_bom)

        assert deserialized_bom == deserialized_bom_roundtriped

    @pytest.mark.parametrize(
        "input_bom",
        [
            pytest.param(bom_with_annotations_2301, id="annotations_2301"),
            pytest.param(bom_with_annotations_2412, id="annotations_2412"),
        ],
    )
    def test_roundtrip_from_text_parsing_fails_unsupported_boms_strict(self, input_bom: str):
        bom_handler = BoMHandler()
        with pytest.raises(ValueError, match="The following fields in the provided BoM could not be deserialized"):
            bom_handler.load_bom_from_text(input_bom, False)

    @pytest.mark.parametrize(
        "input_bom",
        [
            pytest.param(large_bom_2301_path, id="large_bom_2301"),
            pytest.param(sample_sustainability_bom_2301_path, id="sustainability_bom_2301"),
            pytest.param(large_bom_2412_path, id="large_bom_2412"),
            pytest.param(sample_sustainability_bom_2412_path, id="sustainability_bom_2412"),
        ],
    )
    @pytest.mark.parametrize("allow_unsupported_data", [True, False])
    def test_roundtrip_from_file_parsing_succeeds(self, input_bom: Path, allow_unsupported_data: bool):
        bom_handler = BoMHandler()
        deserialized_bom = bom_handler.load_bom_from_file(input_bom, allow_unsupported_data)

        rendered_bom = bom_handler.dump_bom(deserialized_bom)
        deserialized_bom_roundtriped = bom_handler.load_bom_from_text(rendered_bom)

        assert deserialized_bom == deserialized_bom_roundtriped

    @pytest.mark.parametrize(
        "input_bom",
        [
            pytest.param(bom_with_annotations_2301_path, id="annotations_2301"),
            pytest.param(bom_with_annotations_2412_path, id="annotations_2412"),
        ],
    )
    def test_roundtrip_from_file_parsing_succeeds_unsupported_boms_lax(self, input_bom: Path):
        bom_handler = BoMHandler()
        deserialized_bom = bom_handler.load_bom_from_file(input_bom, True)

        rendered_bom = bom_handler.dump_bom(deserialized_bom)
        deserialized_bom_roundtriped = bom_handler.load_bom_from_text(rendered_bom)

        assert deserialized_bom == deserialized_bom_roundtriped

    @pytest.mark.parametrize(
        "input_bom",
        [
            pytest.param(bom_with_annotations_2301_path, id="annotations_2301"),
            pytest.param(bom_with_annotations_2412_path, id="annotations_2412"),
        ],
    )
    def test_roundtrip_from_file_parsing_fails_unsupported_boms_strict(self, input_bom: Path):
        bom_handler = BoMHandler()
        with pytest.raises(ValueError, match="The following fields in the provided BoM could not be deserialized"):
            bom_handler.load_bom_from_file(input_bom, False)


class RoundTripWithAssertionsBoMTester(ABC):
    _namespace_map: dict[str, str]
    _default_namespace: str
    _bom: str
    _bom_path: Path

    class _TestableBoMHandler(BoMHandler):
        def __init__(self, default_namespace: str, namespace_mapping: Dict[str, str]):
            super().__init__()
            self._default_namespace = default_namespace
            self._namespace_mapping = namespace_mapping

        def dump_bom(self, bom: eco2301.BillOfMaterials) -> str:
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

    @staticmethod
    def _compare_boms(*, source_bom: str, result_bom: str):
        source_lines = source_bom.splitlines()
        result_lines = result_bom.splitlines()

        output_lines = []

        diff_result = context_diff(source_lines, result_lines)

        for diff_item in diff_result:
            output_lines.append(diff_item)
        return output_lines

    def test_roundtrip_from_text(self):
        bom_handler = type(self)._TestableBoMHandler(
            default_namespace=self._default_namespace, namespace_mapping=self._namespace_map
        )
        deserialized_bom = bom_handler.load_bom_from_text(self._bom)
        output_bom = bom_handler.dump_bom(deserialized_bom)

        diff = self._compare_boms(source_bom=self._bom, result_bom=output_bom)

        assert len(diff) == 0, "\n".join(diff)

    def test_roundtrip_from_file(self):
        bom_handler = type(self)._TestableBoMHandler(
            default_namespace=self._default_namespace, namespace_mapping=self._namespace_map
        )
        deserialized_bom = bom_handler.load_bom_from_file(self._bom_path)
        output_bom = bom_handler.dump_bom(deserialized_bom)

        diff = self._compare_boms(source_bom=self._bom, result_bom=output_bom)

        assert len(diff) == 0, "\n".join(diff)


class TestRoundTripBoM2301WithAssertions(RoundTripWithAssertionsBoMTester):
    _namespace_map = {"gbt": "http://www.grantadesign.com/12/05/GrantaBaseTypes"}
    _default_namespace = "http://www.grantadesign.com/23/01/BillOfMaterialsEco"
    _bom = large_bom_2301
    _bom_path = large_bom_2301_path


class TestRoundTripBoM2412WithAssertions(RoundTripWithAssertionsBoMTester):
    _namespace_map = {"gbt": "http://www.grantadesign.com/12/05/GrantaBaseTypes"}
    _default_namespace = "http://www.grantadesign.com/24/12/BillOfMaterialsEco"
    _bom = large_bom_2412
    _bom_path = large_bom_2412_path


class TestBoMDeserialization:
    # 17/11, 23/01, and 24/12 are quite similar, and in the context of this particular BoM and test, substituting
    # the namespace is sufficient to obtain a valid 23/01 or 24/12 BoM.

    @pytest.fixture(scope="class")
    def simple_2301_bom(self):
        input_bom = sample_bom_1711.replace(
            "http://www.grantadesign.com/17/11/BillOfMaterialsEco",
            "http://www.grantadesign.com/23/01/BillOfMaterialsEco",
        )
        bom_handler = BoMHandler()
        yield bom_handler.load_bom_from_text(input_bom)

    @pytest.fixture(scope="class")
    def simple_2412_bom(self):
        input_bom = sample_bom_1711.replace(
            "http://www.grantadesign.com/17/11/BillOfMaterialsEco",
            "http://www.grantadesign.com/24/12/BillOfMaterialsEco",
        )
        bom_handler = BoMHandler()
        yield bom_handler.load_bom_from_text(input_bom)

    def get_field(self, obj: eco2301.BaseType, p_path: str) -> Any:
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
            ("components[0]/components[1]/part_number", ""),
            ("components[0]/components[1]/part_name", "Part Two"),
            ("components[0]/components[1]/materials[0]/percentage", pytest.approx(80.0)),
            ("components[0]/components[1]/materials[0]/mi_material_reference/db_key", "MI_Restricted_Substances"),
            (
                "components[0]/components[1]/materials[0]/mi_material_reference/record_history_guid",
                "ab4147f6-0e97-47f0-be53-cb5d17dfa82b",
            ),
        ],
    )
    @pytest.mark.parametrize("bom_fixture_name", ["simple_2301_bom", "simple_2412_bom"])
    def test_simple_bom(self, request: pytest.FixtureRequest, bom_fixture_name: str, query: str, value: Any) -> None:
        bom = request.getfixturevalue(bom_fixture_name)
        deserialized_field = self.get_field(bom, query)
        assert deserialized_field == value


@pytest.fixture
def empty_2301_bom():
    return eco2301.BillOfMaterials(
        components=[], transport_phase=[], use_phase=None, location=None, notes=None, internal_id="BomId"
    )


@pytest.fixture
def empty_2412_bom():
    return eco2412.BillOfMaterials(
        components=[], transport_phase=[], use_phase=None, location=None, notes=None, internal_id="BomId"
    )


@pytest.mark.xfail(reason="Empty BoMs can be instantiated and serialized, but not deserialized.")
@pytest.mark.parametrize("bom_fixture_name", ["simple_2301_bom", "simple_2412_bom"])
def test_empty_bom(request: pytest.FixtureRequest, bom_fixture_name: str):
    bom = request.getfixturevalue(bom_fixture_name)
    bom_handler = BoMHandler()
    text = bom_handler.dump_bom(bom)

    rebuilt = bom_handler.load_bom_from_text(text)
    assert rebuilt == bom


class BoMFactory:
    def __init__(self, bom_module: Literal[eco2412] | Literal[eco2301]):
        self.bom_module = bom_module
        self._int = 0
        self._float = 0.1

    def get_int(self) -> int:
        self._int += 1
        return self._int

    def get_float(self) -> float:
        self._float += 0.1
        return self._float

    def get_guid(self) -> str:
        return str(uuid.uuid4())

    def make_location(self) -> eco2301.Location | eco2412.Location:
        id_int = self.get_int()
        return self.bom_module.Location(
            mi_location_reference=self.bom_module.MIRecordReference(
                db_key=f"Location{id_int}RefDbKey",
                record_guid=self.get_guid(),
            ),
            identity=f"Location{id_int}Identity",
            name=f"Location{id_int}Name",
            external_identity=f"Location{id_int}ExternalIdentity",
            internal_id=f"Location{id_int}Id",
        )

    def make_transport_stage(self) -> eco2301.TransportStage | eco2412.TransportStage:
        id_int = self.get_int()
        return self.bom_module.TransportStage(
            mi_transport_reference=self.bom_module.MIRecordReference(
                db_key=f"Transport{id_int}RefDbKey",
                record_guid=self.get_guid(),
            ),
            name=f"Transport{id_int}Name",
            distance=self.bom_module.UnittedValue(self.get_float(), f"Transport{id_int}DistanceUnit"),
            internal_id=f"Transport{id_int}Id",
        )

    def make_full_bom(
        self, use_phase_utility_kwarg, eco2301_compatible=False
    ) -> eco2301.BillOfMaterials | eco2412.BillOfMaterials:
        # Very invalid BoM for any query, but attempts to exercise all fields of all types
        # TODO add non mi part reference
        bom = self.bom_module.BillOfMaterials(
            components=[
                self.bom_module.Part(
                    components=[
                        self.bom_module.Part(
                            part_number="SubPart0",
                        )
                    ],
                    part_number="RootPartNumber",
                    part_name="RootPartName",
                    internal_id="RootPartId",
                    mass_per_unit_of_measure=self.bom_module.UnittedValue(
                        self.get_float(), "RootPartMassPerUnitOfMeasure"
                    ),
                    quantity=self.bom_module.UnittedValue(self.get_float(), "RootPartQuantity"),
                    volume_per_unit_of_measure=self.bom_module.UnittedValue(
                        self.get_float(), "RootPartVolumePerUnitOfMeasure"
                    ),
                    # Exercise as many attributes as possible for references
                    mi_part_reference=self.bom_module.MIRecordReference(
                        db_key="RootPartRefDbKey",
                        record_guid=self.get_guid(),
                        record_history_guid=self.get_guid(),
                        record_version_number=self.get_int(),
                        record_history_identity=self.get_int(),
                        record_uid="RootPartRefRecordUID",
                        lookup_value="RootPartRefLookupValue",
                        lookup_attribute_reference=gbt1205.MIAttributeReference(
                            db_key="RootPartRefLookupRefDbKey",
                            # Choice attribute_name | attribute_identity | pseudo
                            attribute_name="RootPartRefLookupRefAttributeName",
                            table_reference=gbt1205.PartialTableReference(
                                table_identity=self.get_int(),
                                table_guid=self.get_guid(),
                                table_name="RootPartRefLookupRefTableRefName",
                            ),
                            is_standard=False,
                        ),
                    ),
                    materials=[
                        self.bom_module.Material(
                            mi_material_reference=self.bom_module.MIRecordReference(
                                db_key="RootPartMaterial0RefDbKey",
                                lookup_value="RootPartMaterial0RefLookupValue",
                                lookup_attribute_reference=gbt1205.MIAttributeReference(
                                    db_key="RootPartMaterial0RefDbKey",
                                    # Choice attribute_name | attribute_identity | pseudo
                                    attribute_identity=self.get_int(),
                                ),
                            ),
                            # Choice percentage | mass
                            percentage=self.get_float(),
                            # Choice recycle_content_is_typical | recycle_content_percentage
                            recycle_content_percentage=self.get_float(),
                            end_of_life_fates=[
                                self.bom_module.EndOfLifeFate(
                                    mi_end_of_life_reference=self.bom_module.MIRecordReference(
                                        db_key="RootPartMaterial0EOLFRefDbKey",
                                        record_guid=self.get_guid(),
                                    ),
                                    fraction=self.get_float(),
                                )
                            ],
                            external_identity="RootPartMaterial0ExternalIdentity",
                            internal_id="RootPartMaterial0Id",
                            identity="RootPartMaterial0Identity",
                            name="RootPartMaterial0Name",
                            processes=[
                                self.bom_module.Process(  # Process with all fields
                                    mi_process_reference=self.bom_module.MIRecordReference(
                                        db_key="RootPartMaterial0Process0RefDbKey",
                                        record_guid=self.get_guid(),
                                    ),
                                    identity="RootPartMaterial0Process0Identity",
                                    external_identity="RootPartMaterial0Process0ExternalIdentity",
                                    internal_id="RootPartMaterial0Process0Id",
                                    name="RootPartMaterial0Process0Name",
                                    dimension_type=self.bom_module.DimensionType.MassRemoved,
                                    # Choice quantity|percentage: another process defines percentage.
                                    quantity=self.bom_module.UnittedValue(
                                        self.get_float(),
                                        unit="RootPartMaterial0Process0QuantityUnit",
                                    ),
                                )
                            ],
                        ),
                        self.bom_module.Material(
                            mi_material_reference=self.bom_module.MIRecordReference(
                                db_key="RootPartMaterial1RefDbKey",
                                lookup_value="RootPartMaterial1RefLookupValue",
                                lookup_attribute_reference=gbt1205.MIAttributeReference(
                                    db_key="RootPartMaterial0RefDbKey",
                                    # Choice attribute_name | attribute_identity | pseudo
                                    pseudo=gbt1205.PseudoAttribute.Name,
                                ),
                            ),
                            # Choice percentage | mass
                            mass=self.bom_module.UnittedValue(self.get_float(), "RootPartMaterial1MassUnit"),
                            # Choice recycle_content_is_typical | recycle_content_percentage
                            # recycle_content_is_typical=True, # TODO broken
                        ),
                    ],
                    processes=[
                        self.bom_module.Process(  # Minimal process
                            mi_process_reference=self.bom_module.MIRecordReference(
                                db_key="RootPartProcess0RefDbKey",
                                record_guid=self.get_guid(),
                            ),
                            dimension_type=self.bom_module.DimensionType.Mass,
                            # Choice quantity|percentage: another process defines quantity.
                            percentage=self.get_float(),
                        )
                    ],
                    specifications=[
                        self.bom_module.Specification(
                            mi_specification_reference=self.bom_module.MIRecordReference(
                                db_key="RootPartSpec0RefDbKey",
                                record_guid=self.get_guid(),
                            ),
                            quantity=self.bom_module.UnittedValue(self.get_float(), "RootPartSpec0QuantityUnit"),
                            identity="RootPartSpec0Identity",
                            external_identity="RootPartSpec0ExternalIdentity",
                            internal_id="RootPartSpec0Id",
                            name="RootPartSpec0Name",
                        )
                    ],
                    substances=[
                        self.bom_module.Substance(
                            mi_substance_reference=self.bom_module.MIRecordReference(
                                db_key="RootPartSubstance0RefDbKey",
                                record_guid=self.get_guid(),
                            ),
                            percentage=self.get_float(),
                            category=self.bom_module.Category.Incorporated,
                            identity="RootPartSubstance0Identity",
                            external_identity="RootPartSubstance0ExternalIdentity",
                            internal_id="RootPartSubstance0Id",
                            name="RootPartSubstance0Name",
                        )
                    ],
                    rohs_exemptions=["RootPartRohsExemption0" "RootPartRohsExemption1"],
                    end_of_life_fates=[
                        self.bom_module.EndOfLifeFate(
                            mi_end_of_life_reference=self.bom_module.MIRecordReference(
                                db_key="RootPartEOLFRefDbKey",
                                record_guid=self.get_guid(),
                            ),
                            fraction=self.get_float(),
                        )
                    ],
                ),
            ],
            transport_phase=[
                self.make_transport_stage(),
                self.make_transport_stage(),
            ],
            use_phase=self.bom_module.UsePhase(
                product_life_span=self.bom_module.ProductLifeSpan(
                    duration_years=self.get_float(),
                    number_of_functional_units=self.get_float(),
                    functional_unit_description="UsePhaseFunctionalUnitDescription",
                    utility=self.bom_module.UtilitySpecification(
                        **{use_phase_utility_kwarg: self.get_float()},
                    ),
                ),
                electricity_mix=self.bom_module.ElectricityMix(
                    mi_region_reference=self.bom_module.MIRecordReference(
                        db_key="UsePhaseElectricityMixRefDbKey",
                        record_guid=self.get_guid(),
                    )
                ),
                mobile_mode=self.bom_module.MobileMode(
                    mi_transport_reference=self.bom_module.MIRecordReference(
                        db_key="UsePhaseMobileModeRefDbKey",
                        record_guid=self.get_guid(),
                    ),
                    days_used_per_year=self.get_float(),
                    distance_travelled_per_day=self.bom_module.UnittedValue(
                        value=self.get_float(),
                        unit="UsePhaseMobileDistancePerDayUnit",
                    ),
                ),
                static_mode=self.bom_module.StaticMode(
                    mi_energy_conversion_reference=self.bom_module.MIRecordReference(
                        db_key="UsePhaseStaticModeRefDbKey",
                        record_guid=self.get_guid(),
                    ),
                    days_used_per_year=self.get_float(),
                    hours_used_per_day=self.get_float(),
                    power_rating=self.bom_module.UnittedValue(self.get_float(), "UsePhaseStaticModePowerRating"),
                ),
            ),
            location=self.make_location(),
            notes=self.bom_module.BoMDetails(
                notes="BomNotes",
                picture_url="https://www.ansys.com/",
                product_name="ProductName",
            ),
            # annotations=[
            #     self.bom_module.Annotation(
            #         target_id="RootPartId",
            #         type_="Annotation0Type",
            #         source_id="AnnotationSource0Id",
            #         value="Annotation0",
            #     )
            # ],
            # annotation_sources=[
            #     self.bom_module.AnnotationSource(
            #         name="AnnotationSource0Name",
            #         method="AnnotationSource0Method",
            #         data=[
            #             "AnnotationSource0Data0"
            #         ],
            #         internal_id="AnnotationSource0Id"
            #     )
            # ],
            internal_id="BomId",
        )
        # Add additional eco24/12 capabilities
        if self.bom_module == eco2412 and not eco2301_compatible:
            bom.components[0].transport_phase = [
                self.make_transport_stage(),
                self.make_transport_stage(),
            ]
            bom.components[0].location = self.make_location()
            bom.components[0].materials[0].processes[0].transport_phase = [
                self.make_transport_stage(),
                self.make_transport_stage(),
            ]
            bom.components[0].materials[0].processes[0].location = self.make_location()

        return bom


# Utility appears only once in BoM, so the whole test is repeated to exercise the three mutually exclusive possible
# choices.
@pytest.mark.parametrize(
    "use_phase_utility_kwarg",
    [
        "industry_average_number_of_functional_units",
        "industry_average_duration_years",
        "utility",
    ],
)
@pytest.mark.parametrize("bom_types", [eco2412, eco2301])
def test_everything_bom(use_phase_utility_kwarg, bom_types):
    bom = BoMFactory(bom_types).make_full_bom(use_phase_utility_kwarg)
    bom_handler = BoMHandler()
    text = bom_handler.dump_bom(bom)

    rebuilt = bom_handler.load_bom_from_text(text)
    assert rebuilt == bom


@pytest.mark.parametrize("bom_types", [eco2412, eco2301])
def test_unexpected_args_raises_error(bom_types):
    with pytest.raises(TypeError, match="unexpected keyword argument 'unexpected_kwarg'"):
        bom_types.Part(part_number="PartNumber", unexpected_kwarg="UnexpectedKwargValue")


@pytest.mark.parametrize(
    "use_phase_utility_kwarg",
    [
        "industry_average_number_of_functional_units",
        "industry_average_duration_years",
        "utility",
    ],
)
class TestBoMConversion:
    @pytest.fixture(scope="function", autouse=True)
    def _bom_handler(self):
        self.bom_handler = BoMHandler()

    def rebuild_and_check_bom(self, original_bom, converted_bom, original_namespace, new_namespace):
        if original_namespace is not new_namespace:
            # Do the upgrade in reverse by changing namespaces in the text before rebuilding
            # This should always work, as long as BoM changes are always additive
            converted_bom = converted_bom.replace(new_namespace, original_namespace)
        rebuilt_bom = self.bom_handler.load_bom_from_text(converted_bom)
        assert rebuilt_bom == original_bom

    @pytest.mark.parametrize("source_bom_types", [eco2301, eco2412])
    @pytest.mark.parametrize("target_bom_types", [eco2301, eco2412])
    @pytest.mark.parametrize("allow_unsupported_data", [True, False])
    def test_full_bom_upgrade_and_crossgrade(
        self, source_bom_types, target_bom_types, use_phase_utility_kwarg, allow_unsupported_data
    ):
        is_downgrade = source_bom_types is eco2412 and target_bom_types is eco2301
        if is_downgrade and not allow_unsupported_data:
            pytest.skip("Full BoM downgrade with allow_unsupported_data=False mode raises exception")

        source_bom = BoMFactory(source_bom_types).make_full_bom(use_phase_utility_kwarg)
        target_bom = self.bom_handler.convert(source_bom, target_bom_types.BillOfMaterials, allow_unsupported_data)

        assert isinstance(target_bom, target_bom_types.BillOfMaterials)
        target_bom_text = self.bom_handler.dump_bom(target_bom)
        if is_downgrade:
            # Skip the final comparison
            return
        self.rebuild_and_check_bom(
            source_bom,
            target_bom_text,
            source_bom_types.BillOfMaterials.namespace,
            target_bom_types.BillOfMaterials.namespace,
        )

    @pytest.mark.parametrize("source_bom_types", [eco2301, eco2412])
    @pytest.mark.parametrize("target_bom_types", [eco2301, eco2412])
    @pytest.mark.parametrize("allow_unsupported_data", [True, False])
    def test_partial_bom_upgrade_crossgrade_downgrade(
        self, source_bom_types, target_bom_types, use_phase_utility_kwarg, allow_unsupported_data
    ):
        source_bom = BoMFactory(source_bom_types).make_full_bom(use_phase_utility_kwarg, eco2301_compatible=True)
        target_bom = self.bom_handler.convert(source_bom, target_bom_types.BillOfMaterials, allow_unsupported_data)

        assert isinstance(target_bom, target_bom_types.BillOfMaterials)
        target_bom_text = self.bom_handler.dump_bom(target_bom)
        self.rebuild_and_check_bom(
            source_bom,
            target_bom_text,
            source_bom_types.BillOfMaterials.namespace,
            target_bom_types.BillOfMaterials.namespace,
        )

    def test_full_bom_downgrade_strict_raises_exception(self, use_phase_utility_kwarg):
        source_bom = BoMFactory(eco2412).make_full_bom(use_phase_utility_kwarg)
        bom_handler = BoMHandler()
        with pytest.raises(ValueError, match="The following fields in the provided BoM could not be deserialized") as e:
            bom_handler.convert(source_bom, eco2301.BillOfMaterials, allow_unsupported_data=False)
        lines = set(str(e.value).splitlines())
        assert len(lines) == 5

        # Examine individual error cases
        parent_errors = ["Process", "Part"]
        field_errors = ["Location", "Transport"]
        errors = product(parent_errors, field_errors)
        for parent_error, field_error in errors:
            for line in lines.copy():
                if parent_error in line and field_error in line:
                    lines.remove(line)
                    break
        assert len(lines) == 1

    def test_invalid_target_raises_exception(self, use_phase_utility_kwarg):
        source_bom = BoMFactory(eco2412).make_full_bom(use_phase_utility_kwarg)
        bom_handler = BoMHandler()
        with pytest.raises(ValueError, match='target_bom_version "24/12" is not a valid BoM target.'):
            bom_handler.convert(source_bom, "24/12")
