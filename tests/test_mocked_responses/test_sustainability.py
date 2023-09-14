from ansys.grantami.bomanalytics import queries
from ansys.grantami.bomanalytics._query_results import (
    BomSustainabilityQueryResult,
    BomSustainabilitySummaryQueryResult,
)
from ansys.grantami.bomanalytics_openapi.models import (
    GetSustainabilityForBom2301Response,
    GetSustainabilitySummaryForBom2301Response,
)
from .common import (
    BaseMockTester,
)


class TestBomSustainability(BaseMockTester):
    query = queries.BomSustainabilityQuery()
    mock_key = GetSustainabilityForBom2301Response.__name__

    def test_response_processing(self, mock_connection):
        response = self.get_mocked_response(mock_connection)

        # TODO Example isn't complete enough

        assert isinstance(response, BomSustainabilityQueryResult)

        assert len(response.transport_stages) == 0
        assert len(response.messages) == 0

        # Top-level
        assert len(response.parts) == 1
        part_0 = response.parts[0]
        assert len(part_0.materials) == 0
        assert len(part_0.processes) == 0
        assert len(part_0.substances) == 0
        assert len(part_0.specifications) == 0

        assert part_0.embodied_energy.unit == "MJ"
        assert part_0.embodied_energy.value == 441.2
        assert part_0.climate_change.unit == "kg"
        assert part_0.climate_change.value == 14.2
        assert part_0.reported_mass.unit == "kg"
        assert part_0.reported_mass.value == 2

        assert part_0.part_number is None
        assert part_0.record_history_identity is None

        # Level 1
        assert len(part_0.parts) == 1
        part_0_0 = part_0.parts[0]

        assert len(part_0_0.parts) == 0
        assert len(part_0_0.processes) == 0
        assert len(part_0_0.substances) == 0
        assert len(part_0_0.specifications) == 0

        assert part_0_0.embodied_energy.unit == "MJ"
        assert part_0_0.embodied_energy.value == 441.2
        assert part_0_0.climate_change.unit == "kg"
        assert part_0_0.climate_change.value == 14.2
        assert part_0_0.reported_mass.unit == "kg"
        assert part_0_0.reported_mass.value == 2

        assert len(part_0_0.materials) == 1
        part_0_0_material_0 = part_0_0.materials[0]
        # TODO something does not add-up in Climate change
        assert part_0_0_material_0.embodied_energy.unit == "MJ"
        assert part_0_0_material_0.embodied_energy.value == 441.1
        assert part_0_0_material_0.climate_change.unit == "kg"
        assert part_0_0_material_0.climate_change.value == 14.9
        assert part_0_0_material_0.reported_mass.unit == "kg"
        assert part_0_0_material_0.reported_mass.value == 2
        assert part_0_0_material_0.recyclable is True
        assert part_0_0_material_0.biodegradable is False
        assert part_0_0_material_0.downcycle is True
        assert part_0_0_material_0.record_guid == "8dc38bb5-eff9-4c60-9233-271a3c8f6270"

        assert len(part_0_0_material_0.processes) == 1
        assert len(part_0_0_material_0.substances) == 0

        process = part_0_0_material_0.processes[0]
        assert process.embodied_energy.unit == "MJ"
        assert process.embodied_energy.value == 0.09
        assert process.climate_change.unit == "kg"
        assert process.climate_change.value == 0
        assert process.record_history_guid == "d986c90a-2835-45f3-8b69-d6d662dcf53a"


class TestBomSustainabilitySummary(BaseMockTester):
    query = queries.BomSustainabilitySummaryQuery()
    mock_key = GetSustainabilitySummaryForBom2301Response.__name__

    def test_response_processing(self, mock_connection):
        response = self.get_mocked_response(mock_connection)
        assert isinstance(response, BomSustainabilitySummaryQueryResult)

        assert len(response.messages) == 0

        material_summary = response.material
        assert material_summary.embodied_energy.value == 134.482549067761
        assert material_summary.embodied_energy.unit == "MJ"
        assert material_summary.climate_change.value == 4.3276934674222
        assert material_summary.climate_change.unit == "kg"
        assert material_summary.embodied_energy_percentage == 95.1957177924867
        assert material_summary.climate_change_percentage == 93.623465310322

        process_summary = response.process
        assert process_summary.embodied_energy.value == 6.78698719532399
        assert process_summary.embodied_energy.unit == "MJ"
        assert process_summary.climate_change.value == 0.29475182775859
        assert process_summary.climate_change.unit == "kg"
        assert process_summary.embodied_energy_percentage == 4.80428220751333
        assert process_summary.climate_change_percentage == 6.37653468967796

        transport_summary = response.transport
        assert transport_summary.embodied_energy.value == 0
        assert transport_summary.embodied_energy.unit == "MJ"
        assert transport_summary.climate_change.value == 0
        assert transport_summary.climate_change.unit == "kg"
        assert transport_summary.embodied_energy_percentage == 0
        assert transport_summary.climate_change_percentage == 0

        assert len(response.material_details) == 1
        unique_material_0 = response.material_details[0]
        assert unique_material_0.name == "steel-kovar-annealed"
        assert unique_material_0.record_guid == "8dc38bb5-eff9-4c60-9233-271a3c8f6270"
        assert unique_material_0.embodied_energy.value == 134.482549067761
        assert unique_material_0.embodied_energy.unit == "MJ"
        assert unique_material_0.climate_change.value == 4.3276934674222
        assert unique_material_0.climate_change.unit == "kg"
        assert unique_material_0.embodied_energy_percentage == 100
        assert unique_material_0.climate_change_percentage == 100
        assert unique_material_0.mass_before_processing.value == 0.625
        assert unique_material_0.mass_before_processing.unit == "kg"
        assert unique_material_0.mass_after_processing.value == 0.5
        assert unique_material_0.mass_after_processing.unit == "kg"

        assert len(unique_material_0.contributors) == 1
        # TODO this is consistent with the example response. But is the example response correct?
        assert unique_material_0.contributors[0].name == ""
        assert unique_material_0.contributors[0].part_number is None
        assert unique_material_0.contributors[0].material_mass_before_processing.value == 0.625
        assert unique_material_0.contributors[0].material_mass_before_processing.unit == "kg"

        assert len(response.joining_and_finishing_processes_details) == 0

        assert len(response.primary_processes_details) == 1
        # Unique primary process - material pair
        unique_ppmp_0 = response.primary_processes_details[0]
        assert unique_ppmp_0.process_name == "Metal casting"
        assert unique_ppmp_0.process_reference.record_guid == "baa6c95b-ff0e-4811-9120-92717ee15bda"
        assert unique_ppmp_0.material_name == "High alloy steel, Kovar, annealed"
        assert unique_ppmp_0.material_reference.record_guid == "8dc38bb5-eff9-4c60-9233-271a3c8f6270"

        assert unique_ppmp_0.embodied_energy.value == 6.55438765769984
        assert unique_ppmp_0.embodied_energy.unit == "MJ"
        assert unique_ppmp_0.climate_change.value == 0.283705040845716
        assert unique_ppmp_0.climate_change.unit == "kg"
        assert unique_ppmp_0.embodied_energy_percentage == 100
        assert unique_ppmp_0.climate_change_percentage == 100

        assert len(response.secondary_processes_details) == 1
        # Unique secondary process - material pair
        unique_spmp_0 = response.secondary_processes_details[0]
        assert unique_spmp_0.process_name == "Machining, coarse"
        assert unique_spmp_0.process_reference.record_guid == "907bda29-e800-44f6-b7ea-4eb8e7cff375"
        assert unique_spmp_0.material_name == "High alloy steel, Kovar, annealed"
        assert unique_spmp_0.material_reference.record_guid == "8dc38bb5-eff9-4c60-9233-271a3c8f6270"

        assert unique_spmp_0.embodied_energy.value == 0.232599537624153
        assert unique_spmp_0.embodied_energy.unit == "MJ"
        assert unique_spmp_0.climate_change.value == 0.0110467869128737
        assert unique_spmp_0.climate_change.unit == "kg"
        assert unique_spmp_0.embodied_energy_percentage == 100
        assert unique_spmp_0.climate_change_percentage == 100

        assert len(response.transport_details) == 0
