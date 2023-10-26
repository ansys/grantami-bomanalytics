import json

from ansys.grantami.bomanalytics_openapi.models import (
    CommonSustainabilityPartWithSustainability,
    CommonValueWithUnit,
    GetSustainabilityForBom2301Response,
    GetSustainabilitySummaryForBom2301Response,
)
import pytest

from ansys.grantami.bomanalytics import queries
from ansys.grantami.bomanalytics._query_results import (
    BomSustainabilityQueryResult,
    BomSustainabilitySummaryQueryResult,
)

from ..inputs import examples_as_dicts, sample_sustainability_bom_2301
from .common import BaseMockTester


class TestBomSustainability(BaseMockTester):
    # Use sample BoM to avoid validation error
    query = queries.BomSustainabilityQuery().with_bom(sample_sustainability_bom_2301)
    mock_key = GetSustainabilityForBom2301Response.__name__

    def test_response_processing(self, mock_connection):
        response = self.get_mocked_response(mock_connection)

        assert isinstance(response, BomSustainabilityQueryResult)

        assert len(response.transport_stages) == 0
        assert len(response.messages) == 1

        # Top-level
        assert len(response.parts) == 1
        part_0 = response.parts[0]
        assert len(part_0.materials) == 0
        assert len(part_0.processes) == 0

        assert part_0.embodied_energy.unit == "MJ"
        assert part_0.embodied_energy.value == pytest.approx(490.22, 0.01)
        assert part_0.climate_change.unit == "kg"
        assert part_0.climate_change.value == pytest.approx(18.09, 0.01)
        assert part_0.reported_mass.unit == "kg"
        assert part_0.reported_mass.value == 2

        assert part_0.part_number is None
        assert part_0.record_history_identity is None

        # Level 1
        assert len(part_0.parts) == 1
        part_0_0 = part_0.parts[0]

        assert len(part_0_0.parts) == 0
        assert len(part_0_0.processes) == 0

        assert part_0_0.embodied_energy.unit == "MJ"
        assert part_0_0.embodied_energy.value == pytest.approx(490.22, 0.01)
        assert part_0_0.climate_change.unit == "kg"
        assert part_0_0.climate_change.value == pytest.approx(18.09, 0.01)
        assert part_0_0.reported_mass.unit == "kg"
        assert part_0_0.reported_mass.value == 2

        assert len(part_0_0.materials) == 1
        part_0_0_material_0 = part_0_0.materials[0]
        assert part_0_0_material_0.embodied_energy.unit == "MJ"
        assert part_0_0_material_0.embodied_energy.value == pytest.approx(489.33, 0.01)
        assert part_0_0_material_0.climate_change.unit == "kg"
        assert part_0_0_material_0.climate_change.value == pytest.approx(18.037, 0.01)
        assert part_0_0_material_0.reported_mass.unit == "kg"
        assert part_0_0_material_0.reported_mass.value == 2
        assert part_0_0_material_0.recyclable is True
        assert part_0_0_material_0.biodegradable is False
        assert part_0_0_material_0.functional_recycle is True
        assert part_0_0_material_0.record_guid == "8dc38bb5-eff9-4c60-9233-271a3c8f6270"

        assert len(part_0_0_material_0.processes) == 1

        process = part_0_0_material_0.processes[0]
        assert process.embodied_energy.unit == "MJ"
        assert process.embodied_energy.value == pytest.approx(0.89, 0.01)
        assert process.climate_change.unit == "kg"
        assert process.climate_change.value == pytest.approx(0.0579, 0.01)
        assert process.record_history_guid == "d986c90a-2835-45f3-8b69-d6d662dcf53a"

    def test_two_root_parts_emits_warning(self, mock_connection):
        part1 = CommonSustainabilityPartWithSustainability(
            input_part_number="PartOne",
            reference_type="MiRecordGuid",
            reference_value="GUID",
            parts=[],
            specifications=[],
            materials=[],
            processes=[],
            embodied_energy=CommonValueWithUnit(value=1.0, unit="UNIT"),
            climate_change=CommonValueWithUnit(value=1.0, unit="UNIT"),
            reported_mass=CommonValueWithUnit(value=1.0, unit="UNIT"),
        )
        part2 = CommonSustainabilityPartWithSustainability(**part1.to_dict())
        part2.input_part_number = "PartTwo"
        two_parts_response = GetSustainabilityForBom2301Response(
            log_messages=[],
            parts=[part1, part2],
            transport_stages=[],
        )
        mock_response = json.dumps(mock_connection.sanitize_for_serialization(two_parts_response))
        with pytest.warns(UserWarning, match="single root part"):
            response = self.get_mocked_response(mock_connection, response=mock_response)


class TestBomSustainabilitySummary(BaseMockTester):
    # Use sample BoM to avoid validation error
    query = queries.BomSustainabilitySummaryQuery().with_bom(sample_sustainability_bom_2301)
    mock_key = GetSustainabilitySummaryForBom2301Response.__name__

    def test_response_processing(self, mock_connection):
        patched_response = examples_as_dicts[self.mock_key]
        patched_response["MaterialSummary"]["Summary"][0]["LargestContributors"][0]["RecordReference"] = {
            "Id": None,
            "ReferenceType": None,
            "ReferenceValue": None,
        }
        response = self.get_mocked_response(mock_connection, json.dumps(patched_response))
        assert isinstance(response, BomSustainabilitySummaryQueryResult)

        assert len(response.messages) == 0

        material_summary = response.material
        assert material_summary.embodied_energy.value == pytest.approx(149.17, 0.01)
        assert material_summary.embodied_energy.unit == "MJ"
        assert material_summary.climate_change.value == pytest.approx(5.499, 0.01)
        assert material_summary.climate_change.unit == "kg"
        assert material_summary.embodied_energy_percentage == pytest.approx(54.943, 0.01)
        assert material_summary.climate_change_percentage == pytest.approx(39.56, 0.01)

        process_summary = response.process
        assert process_summary.embodied_energy.value == 122.341468869412
        assert process_summary.embodied_energy.unit == "MJ"
        assert process_summary.climate_change.value == 8.40038083098692
        assert process_summary.climate_change.unit == "kg"
        assert process_summary.embodied_energy_percentage == 45.0566568976384
        assert process_summary.climate_change_percentage == 60.4354407962734

        transport_summary = response.transport
        assert transport_summary.embodied_energy.value == 0
        assert transport_summary.embodied_energy.unit == "MJ"
        assert transport_summary.climate_change.value == 0
        assert transport_summary.climate_change.unit == "kg"
        assert transport_summary.embodied_energy_percentage == 0
        assert transport_summary.climate_change_percentage == 0

        assert len(response.material_details) == 1
        unique_material_0 = response.material_details[0]
        assert unique_material_0.identity == "steel-kovar-annealed"
        assert unique_material_0.material_reference.record_guid == "8dc38bb5-eff9-4c60-9233-271a3c8f6270"
        assert unique_material_0.embodied_energy.value == 149.186596666725
        assert unique_material_0.embodied_energy.unit == "MJ"
        assert unique_material_0.climate_change.value == 5.49937851602342
        assert unique_material_0.climate_change.unit == "kg"
        assert unique_material_0.embodied_energy_percentage == 100
        assert unique_material_0.climate_change_percentage == 100
        assert unique_material_0.mass_before_processing.value == 0.625
        assert unique_material_0.mass_before_processing.unit == "kg"
        assert unique_material_0.mass_after_processing.value == 0.5
        assert unique_material_0.mass_after_processing.unit == "kg"

        assert len(unique_material_0.contributors) == 1
        # TODO this is consistent with the example response. But is the example response correct?
        assert unique_material_0.contributors[0].name == "PartTwo"
        assert unique_material_0.contributors[0].part_number == "PartTwo"
        assert unique_material_0.contributors[0].material_mass_before_processing.value == 0.625
        assert unique_material_0.contributors[0].material_mass_before_processing.unit == "kg"

        assert len(response.joining_and_finishing_processes_details) == 0

        assert len(response.primary_processes_details) == 1
        # Unique primary process - material pair
        unique_ppmp_0 = response.primary_processes_details[0]
        assert unique_ppmp_0.process_name == "Metal casting"
        assert unique_ppmp_0.process_reference.record_guid == "baa6c95b-ff0e-4811-9120-92717ee15bda"
        assert unique_ppmp_0.material_identity == "steel-kovar-annealed"
        assert unique_ppmp_0.material_reference.record_guid == "8dc38bb5-eff9-4c60-9233-271a3c8f6270"

        assert unique_ppmp_0.embodied_energy.value == 120.110900684605
        assert unique_ppmp_0.embodied_energy.unit == "MJ"
        assert unique_ppmp_0.climate_change.value == 8.25552087559637
        assert unique_ppmp_0.climate_change.unit == "kg"
        assert unique_ppmp_0.embodied_energy_percentage == 100
        assert unique_ppmp_0.climate_change_percentage == 100

        assert len(response.secondary_processes_details) == 1
        # Unique secondary process - material pair
        unique_spmp_0 = response.secondary_processes_details[0]
        assert unique_spmp_0.process_name == "Machining, coarse"
        assert unique_spmp_0.process_reference.record_guid == "907bda29-e800-44f6-b7ea-4eb8e7cff375"
        assert unique_spmp_0.material_identity == "steel-kovar-annealed"
        assert unique_spmp_0.material_reference.record_guid == "8dc38bb5-eff9-4c60-9233-271a3c8f6270"

        assert unique_spmp_0.embodied_energy.value == 2.23056818480611
        assert unique_spmp_0.embodied_energy.unit == "MJ"
        assert unique_spmp_0.climate_change.value == 0.144859955390553
        assert unique_spmp_0.climate_change.unit == "kg"
        assert unique_spmp_0.embodied_energy_percentage == 100
        assert unique_spmp_0.climate_change_percentage == 100

        assert len(response.transport_details) == 0
