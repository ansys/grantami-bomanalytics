from difflib import context_diff
from pathlib import Path
import re
from typing import Any, Dict
import uuid
from lxml import etree
import pytest

from ansys.grantami.bomanalytics import BoMHandler
from ansys.grantami.bomanalytics.bom_types import *


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
        "bom_filename",
        ["drill.xml", "medium-test-bom.xml"],
    )
    def test_roundtrip_with_assertions(self, bom_filename: str):
        bom_path = self._bom_location / bom_filename
        with open(bom_path, "r", encoding="utf8") as fp:
            input_bom = fp.read()

        bom_handler = _TestableBoMHandler(
            default_namespace=self._default_namespace, namespace_mapping=self._namespace_map
        )
        deserialized_bom = bom_handler.load_bom_from_text(input_bom)
        output_bom = bom_handler.dump_bom(deserialized_bom)

        diff = self._compare_boms(source_bom=input_bom, result_bom=output_bom)

        assert len(diff) == 0, "\n".join(diff)

    @pytest.mark.parametrize(
        "bom_filename",
        ["drill.xml", "medium-test-bom.xml"],
    )
    def test_roundtrip_parsing_succeeds(self, bom_filename: str):
        bom_path = self._bom_location / bom_filename
        with open(bom_path, "r", encoding="utf8") as fp:
            input_bom = fp.read()

        bom_handler = BoMHandler()
        deserialized_bom = bom_handler.load_bom_from_text(input_bom)

        rendered_bom = bom_handler.dump_bom(deserialized_bom)
        deserialized_bom_roundtriped = bom_handler.load_bom_from_text(rendered_bom)

        assert deserialized_bom == deserialized_bom_roundtriped


class TestBoMDeserialization:
    _bom_location = Path(__file__).parent / "inputs"

    @pytest.fixture(scope="class")
    def simple_bom(self):
        bom_path = self._bom_location / "bom-1711-as-2301.xml"
        with open(bom_path, "r", encoding="utf8") as fp:
            input_bom = fp.read()

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


@pytest.fixture
def empty_bom():
    return BillOfMaterials(
        components=[],
        transport_phase=[],
        use_phase=None,
        location=None,
        notes=None,
        internal_id="BomId"
    )


@pytest.mark.xfail(reason="Empty BoMs can be instantiated and serialized, but not deserialized.")
def test_empty_bom(empty_bom):
    bom_handler = BoMHandler()
    text = bom_handler.dump_bom(empty_bom)

    rebuilt = bom_handler.load_bom_from_text(text)
    assert rebuilt == empty_bom


@pytest.fixture
def full_bom():
    class Counter:
        """Used to generate unique identities and test values."""
        def __init__(self):
            self._int = 0
            self._float = 0.1

        def get_int(self) -> int:
            self._int += 1
            return self._int

        def get_float(self) -> float:
            self._float += 0.1
            return self._float

    counter = Counter()

    # Very invalid BoM for any query, but aims to exercise all fields of all types
    # TODO add non mi part reference
    return BillOfMaterials(
        components=[
            Part(
                components=[
                    Part(
                        part_number="SubPart0",
                    )
                ],
                part_number="RootPartNumber",
                part_name="RootPartName",
                internal_id="RootPartId",
                mass_per_unit_of_measure=UnittedValue(counter.get_float(), "RootPartMassPerUnitOfMeasure"),
                quantity=UnittedValue(counter.get_float(), "RootPartQuantity"),
                volume_per_unit_of_measure=UnittedValue(counter.get_float(), "RootPartVolumePerUnitOfMeasure"),
                # Exercise all attributes of all references
                mi_part_reference=MIRecordReference(
                    db_key="RootPartRefDbKey",
                    record_guid=str(uuid.uuid4()),
                    record_history_guid=str(uuid.uuid4()),
                    record_version_number=counter.get_int(),
                    record_history_identity=counter.get_int(),
                    record_uid="RootPartRefRecordUID",
                    lookup_value="RootPartRefLookupValue",
                    lookup_attribute_reference=MIAttributeReference(
                        db_key="RootPartRefLookupRefDbKey",
                        attribute_name="RootPartRefLookupRefAttributeName",
                        # attribute_identity=counter.get_int(), # TODO Choice with AttName
                        table_reference=PartialTableReference(
                            table_identity=counter.get_int(),
                            table_guid=str(uuid.uuid4()),
                            table_name="RootPartRefLookupRefTableRefName",
                        ),
                        # pseudo=PseudoAttribute.Name, # TODO choice with AttName
                        is_standard=False,
                    ),
                ),
                materials=[
                    Material(
                        mi_material_reference=MIRecordReference(
                            db_key="RootPartMaterial0RefDbKey",
                            record_guid=str(uuid.uuid4()),
                        ),
                        percentage=counter.get_float(),
                        # mass=UnittedValue(counter.get_float(), "RootPartMaterial0MassUnit"), # CHoice percentage
                        # recycle_content_is_typical=True, # TODO choice with recycle_content_percentage, need a second material
                        recycle_content_percentage=counter.get_float(),
                        end_of_life_fates=[
                            EndOfLifeFate(
                                mi_end_of_life_reference=MIRecordReference(
                                    db_key="RootPartMaterial0EOLFRefDbKey",
                                    record_guid=str(uuid.uuid4()),
                                ),
                                fraction=counter.get_float(),
                            )
                        ],
                        external_identity="RootPartMaterial0ExternalIdentity",
                        internal_id="RootPartMaterial0Id",
                        identity="RootPartMaterial0Identity",
                        name="RootPartMaterial0Name",
                        processes=[
                            Process(  # Process with all fields
                                mi_process_reference=MIRecordReference(
                                    db_key="RootPartMaterial0Process0RefDbKey",
                                    record_guid=str(uuid.uuid4()),
                                ),
                                identity="RootPartMaterial0Process0Identity",
                                external_identity="RootPartMaterial0Process0ExternalIdentity",
                                internal_id="RootPartMaterial0Process0Id",
                                name="RootPartMaterial0Process0Name",
                                dimension_type=DimensionType.MassRemoved,
                                percentage=counter.get_float(),
                                # TODO choice, make another process to test quantity
                                # quantity=UnittedValue(
                                #     counter.get_float(),
                                #     unit="RootPartMaterial0Process0QuantityUnit",
                                # )
                            )
                        ]
                    )
                ],
                processes=[
                    Process(  # Minimal process
                        mi_process_reference=MIRecordReference(
                            db_key="RootPartProcess0RefDbKey",
                            record_guid=str(uuid.uuid4()),
                        ),
                        dimension_type=DimensionType.Mass,
                        # TODO process requires either Percentage/Quantity, but that's not reflected in typing
                        percentage=counter.get_float()
                    )
                ],
                specifications=[
                    Specification(
                        mi_specification_reference=MIRecordReference(
                            db_key="RootPartSpec0RefDbKey",
                            record_guid=str(uuid.uuid4()),
                        ),
                        quantity=UnittedValue(counter.get_float(), "RootPartSpec0QuantityUnit"),
                        identity="RootPartSpec0Identity",
                        external_identity="RootPartSpec0ExternalIdentity",
                        internal_id="RootPartSpec0Id",
                        name="RootPartSpec0Name",
                    )
                ],
                substances=[
                    Substance(
                        mi_substance_reference=MIRecordReference(
                            db_key="RootPartSubstance0RefDbKey",
                            record_guid=str(uuid.uuid4()),
                        ),
                        percentage=counter.get_float(),
                        category=Category.Incorporated,
                        identity="RootPartSubstance0Identity",
                        external_identity="RootPartSubstance0ExternalIdentity",
                        internal_id="RootPartSubstance0Id",
                        name="RootPartSubstance0Name",
                    )
                ],
                rohs_exemptions=[
                    "RootPartRohsExemption0"
                    "RootPartRohsExemption1"
                ],
                end_of_life_fates=[
                    EndOfLifeFate(
                        mi_end_of_life_reference=MIRecordReference(
                            db_key="RootPartEOLFRefDbKey",
                            record_guid=str(uuid.uuid4()),
                        ),
                        fraction=counter.get_float(),
                    )
                ],
            ),
        ],
        transport_phase=[
            TransportStage(
                mi_transport_reference=MIRecordReference(
                    db_key="Transport0RefDbKey",
                    record_guid=str(uuid.uuid4()),
                ),
                name="Transport0Name",
                distance=UnittedValue(counter.get_float(), "Transport0DistanceUnit"),
                internal_id="Transport0Id",
            ),
        ],
        use_phase=UsePhase(
            product_life_span=ProductLifeSpan(
                duration_years=counter.get_float(),
                number_of_functional_units=counter.get_float(),
                functional_unit_description="UsePhaseFunctionalUnitDescription",
                utility=UtilitySpecification(
                    # TODO choice between the three
                    # industry_average_number_of_functional_units=counter.get_float(),
                    # industry_average_duration_years=counter.get_float(),
                    utility=counter.get_float(),
                )
            ),
            electricity_mix=ElectricityMix(
                mi_region_reference=MIRecordReference(
                    db_key="UsePhaseElectricityMixRefDbKey",
                    record_guid=str(uuid.uuid4()),
                )
            ),
            mobile_mode=MobileMode(
                mi_transport_reference=MIRecordReference(
                    db_key="UsePhaseMobileModeRefDbKey",
                    record_guid=str(uuid.uuid4()),
                ),
                days_used_per_year=counter.get_float(),
                distance_travelled_per_day=UnittedValue(
                    value=counter.get_float(),
                    unit="UsePhaseMobileDistancePerDayUnit",
                ),
            ),
            static_mode=StaticMode(
                mi_energy_conversion_reference=MIRecordReference(
                    db_key="UsePhaseStaticModeRefDbKey",
                    record_guid=str(uuid.uuid4()),
                ),
                days_used_per_year=counter.get_float(),
                hours_used_per_day=counter.get_float(),
                power_rating=UnittedValue(counter.get_float(), "UsePhaseStaticModePowerRating"),
            ),
        ),
        location=Location(
            mi_location_reference=MIRecordReference(
                db_key="LocationRefDbKey",
                record_guid=str(uuid.uuid4()),
            ),
            identity="LocationIdentity",
            name="LocationName",
            external_identity="LocationExternalIdentity",
            internal_id="LocationId",
        ),
        notes=BoMDetails(
            notes="BomNotes",
            picture_url="https://www.ansys.com/",
            product_name="ProductName",
        ),
        # annotations=[  # TODO annotations differ quite a lot from schema
        #     Annotation(
        #         target_id="RootPartId",
        #         type_="Annotation0Type",
        #         source_id="AnnotationSource0Id",
        #         value="Annotation0",
        #     )
        # ],
        # annotation_sources=[
        #     AnnotationSource(
        #         name="AnnotationSource0Name",
        #         method="AnnotationSource0Method",
        #         data=[
        #             "AnnotationSource0Data0"
        #         ],
        #         internal_id="AnnotationSource0Id"
        #     )
        # ],
        internal_id="BomId"
    )

# TODO fix annotations


def test_everything_bom(full_bom):
    bom_handler = BoMHandler()
    text = bom_handler.dump_bom(full_bom)

    rebuilt = bom_handler.load_bom_from_text(text)
    assert rebuilt == full_bom

