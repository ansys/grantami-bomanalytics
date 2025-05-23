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

import json

import pytest

from ansys.grantami.bomanalytics import TransportCategory, queries
from ansys.grantami.bomanalytics._query_results import (
    BomSustainabilityQueryResult,
    BomSustainabilitySummaryQueryResult,
)

from ..inputs import example_boms, example_payloads
from .common import BaseMockTester


class TestBomSustainability(BaseMockTester):
    # Use sample BoM to avoid validation error
    # The response depends only on the examples.py module, not on the provided BoM
    bom = example_boms["sustainability-bom-2301"].content
    query = queries.BomSustainabilityQuery().with_bom(bom)
    mock_key = "GetSustainabilityForBom.Response"

    def test_response_processing(self, mock_connection):
        response = self.get_mocked_response(mock_connection)

        assert isinstance(response, BomSustainabilityQueryResult)

        assert len(response.transport_stages) == 0
        assert len(response.messages) == 1

        # Top-level
        part_0 = response.part
        assert len(part_0.materials) == 0
        assert len(part_0.processes) == 0
        assert len(part_0.transport_stages) == 0

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
        assert len(part_0_0.transport_stages) == 0

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
        assert len(process.transport_stages) == 0


class TestBomSustainabilitySummary(BaseMockTester):
    # Use sample BoM to avoid validation error
    # The response depends only on the examples.py module, not on the provided BoM
    bom = example_boms["sustainability-bom-2301"].content
    query = queries.BomSustainabilitySummaryQuery().with_bom(bom)
    mock_key = "GetSustainabilitySummaryForBom.Response.2301"

    def test_response_processing(self, mock_connection):
        patched_response = example_payloads[self.mock_key].data
        patched_response["MaterialSummary"]["Summary"][0]["LargestContributors"][0]["RecordReference"] = {}
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
        assert response.transport_details_aggregated_by_part == []
        assert response.manufacturing_transport_summary is None
        assert response.distribution_transport_summary is None


class TestBomSustainabilitySummary2412(BaseMockTester):
    # Use sample BoM to avoid validation error
    # The response depends only on the examples.py module, not on the provided BoM
    bom = example_boms["sustainability-bom-2412"].content
    query = queries.BomSustainabilitySummaryQuery().with_bom(bom)
    mock_key = "GetSustainabilitySummaryForBoM.Response.2412"

    def test_response_processing(self, mock_connection):
        response = self.get_mocked_response(mock_connection)
        assert isinstance(response, BomSustainabilitySummaryQueryResult)

        assert len(response.messages) == 0

        # Transport details
        transport_details = response.transport_details
        assert len(transport_details) == 1
        transport = transport_details[0]
        assert transport.climate_change.value == 0.333123822320444
        assert transport.climate_change.unit == "kg"
        assert transport.climate_change_percentage == 100.0
        assert transport.distance.value == 200.0
        assert transport.distance.unit == "km"
        assert transport.embodied_energy.value == 4.72415244615649
        assert transport.embodied_energy.unit == "MJ"
        assert transport.embodied_energy_percentage == 100.0
        assert transport.name == "Aircraft, short haul, belly-freight"
        assert transport.transport_reference.record_guid == "b916ed6b-5e06-4343-9131-d4d562e2d12b"
        assert transport.transport_reference.record_history_guid is None
        assert transport.transport_reference.record_history_identity is None

        # Transport summary by part
        part_transport_groups = response.transport_details_aggregated_by_part
        assert len(part_transport_groups) == 1
        part_transport_group = part_transport_groups[0]
        assert part_transport_group.category == TransportCategory.MANUFACTURING
        assert part_transport_group.climate_change.value == 0.333123822320444
        assert part_transport_group.climate_change.unit == "kg"
        assert part_transport_group.climate_change_percentage == 100.0
        assert part_transport_group.distance.value == 200.0
        assert part_transport_group.distance.unit == "km"
        assert part_transport_group.embodied_energy.value == 4.72415244615649
        assert part_transport_group.embodied_energy.unit == "MJ"
        assert part_transport_group.embodied_energy_percentage == 100.0
        assert part_transport_group.parent_part_name is None
        assert part_transport_group.part_name is None
        assert part_transport_group.transport_types == {"Aircraft, short haul, belly-freight"}

        # Distribution transport
        distribution_transport_group = response.distribution_transport_summary
        assert distribution_transport_group.climate_change.value == 0.0
        assert distribution_transport_group.climate_change.unit == "kg"
        assert distribution_transport_group.climate_change_percentage == 0.0
        assert distribution_transport_group.distance.value == 0.0
        assert distribution_transport_group.distance.unit == "km"
        assert distribution_transport_group.embodied_energy.value == 0.0
        assert distribution_transport_group.embodied_energy.unit == "MJ"
        assert distribution_transport_group.embodied_energy_percentage == 0.0

        # Manufacturing transport
        manufacturing_transport_group = response.manufacturing_transport_summary
        assert manufacturing_transport_group.climate_change.value == 0.333123822320444
        assert manufacturing_transport_group.climate_change.unit == "kg"
        assert manufacturing_transport_group.climate_change_percentage == 100.0
        assert manufacturing_transport_group.distance.value == 200.0
        assert manufacturing_transport_group.distance.unit == "km"
        assert manufacturing_transport_group.embodied_energy.value == 4.72415244615649
        assert manufacturing_transport_group.embodied_energy.unit == "MJ"
        assert manufacturing_transport_group.embodied_energy_percentage == 100.0
