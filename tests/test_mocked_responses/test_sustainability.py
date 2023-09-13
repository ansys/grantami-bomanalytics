from ansys.grantami.bomanalytics import queries
from ansys.grantami.bomanalytics._query_results import BomSustainabilityQueryResult
from ansys.grantami.bomanalytics_openapi.models import GetSustainabilityForBom2301Response
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
