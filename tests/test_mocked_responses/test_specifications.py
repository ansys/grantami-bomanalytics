# Copyright (C) 2022 - 2024 ANSYS, Inc. and/or its affiliates.
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

from ansys.grantami.bomanalytics_openapi.models import (
    GetComplianceForSpecificationsResponse,
    GetImpactedSubstancesForSpecificationsResponse,
)

from ansys.grantami.bomanalytics import indicators, queries

from .common import (
    BaseMockTester,
    CoatingValidator,
    MaterialValidator,
    SpecificationValidator,
    SubstanceValidator,
)


class TestImpactedSubstances(BaseMockTester):
    query = (
        queries.SpecificationImpactedSubstancesQuery()
        .with_legislation_ids(["Fake legislation"])
        .with_specification_ids(["Fake ID"])
    )
    mock_key = GetImpactedSubstancesForSpecificationsResponse.__name__

    def test_impacted_substances_by_specification(self, mock_connection):
        response = self.get_mocked_response(mock_connection)
        assert len(response.impacted_substances_by_specification) == 2

        spec_result_0 = response.impacted_substances_by_specification[0]
        specv_0 = SpecificationValidator(spec_result_0)
        assert specv_0.check_reference(record_history_identity="545019")

        # Test flattened list of substances
        assert len(spec_result_0.substances) == 2
        for substance in spec_result_0.substances:
            sv = SubstanceValidator(substance)
            sv.check_substance_details()

        # Test list of substances grouped by legislations
        assert len(spec_result_0.substances_by_legislation) == 1
        substances_0 = spec_result_0.substances_by_legislation["SINList"]
        assert len(substances_0) == 2
        for substance in substances_0:
            sv = SubstanceValidator(substance)
            sv.check_substance_details()

        spec_result_1 = response.impacted_substances_by_specification[1]
        specv_1 = SpecificationValidator(spec_result_1)
        assert specv_1.check_reference(specification_id="AMS03-27")

        # Test flattened list of substances
        assert len(spec_result_1.substances) == 2
        for substance in spec_result_1.substances:
            sv = SubstanceValidator(substance)
            sv.check_substance_details()

        # Test list of substances grouped by legislations
        assert len(spec_result_1.substances_by_legislation) == 1
        substances_1 = spec_result_1.substances_by_legislation["SINList"]
        assert len(substances_1) == 2
        for substance in substances_1:
            sv = SubstanceValidator(substance)
            sv.check_substance_details()

    def test_impacted_substances_by_legislation(self, mock_connection):
        response = self.get_mocked_response(mock_connection)
        assert len(response.impacted_substances_by_legislation) == 1
        legislation = response.impacted_substances_by_legislation["SINList"]
        for substance in legislation:
            sv = SubstanceValidator(substance)
            sv.check_substance_details()

    def test_impacted_substances(self, mock_connection):
        response = self.get_mocked_response(mock_connection)
        assert len(response.impacted_substances) == 4
        for substance in response.impacted_substances:
            sv = SubstanceValidator(substance)
            sv.check_substance_details()

    def test_query_result_repr(self, mock_connection):
        response = self.get_mocked_response(mock_connection)
        assert (
            repr(response) == "<SpecificationImpactedSubstancesQueryResult: "
            "2 SpecificationWithImpactedSubstances results>"
        )

    def test_impacted_substances_repr(self, mock_connection):
        response = self.get_mocked_response(mock_connection)
        assert "ImpactedSubstance" in repr(response.impacted_substances)

    def test_impacted_substances_by_specification_repr(self, mock_connection):
        response = self.get_mocked_response(mock_connection)
        assert "SpecificationWithImpactedSubstances" in repr(response.impacted_substances_by_specification)

    def test_impacted_substances_by_legislation_repr(self, mock_connection):
        response = self.get_mocked_response(mock_connection)
        for legislation in response.impacted_substances_by_legislation.keys():
            assert legislation in repr(response.impacted_substances_by_legislation)
        assert "ImpactedSubstance" in repr(response.impacted_substances_by_legislation)


class TestCompliance(BaseMockTester):
    """Check that each mocked result has the correct record references, indicator results, child objects, and bom
    relationships.

    A mocked query is used, populated by the examples included in the API definition.

    Spec, coating, material and substance details are verified in separate methods.
    """

    query = (
        queries.SpecificationComplianceQuery()
        .with_indicators(
            [
                indicators.WatchListIndicator(name="Indicator 1", legislation_ids=["Mock"]),
                indicators.RoHSIndicator(name="Indicator 2", legislation_ids=["Mock"]),
            ]
        )
        .with_specification_ids(["Fake ID"])
    )
    mock_key = GetComplianceForSpecificationsResponse.__name__

    def test_compliance_by_specification_and_indicator(self, mock_connection):
        response = self.get_mocked_response(mock_connection)
        assert len(response.compliance_by_specification_and_indicator) == 2

        spec_0 = response.compliance_by_specification_and_indicator[0]
        specv_0 = SpecificationValidator(spec_0)
        assert specv_0.check_reference(specification_id="MSP89,TypeI")
        spec_0_result = [
            indicators.WatchListFlag.WatchListAllSubstancesBelowThreshold,
            indicators.RoHSFlag.RohsCompliant,
        ]
        assert specv_0.check_indicators(spec_0_result)
        assert specv_0.check_bom_structure()
        assert specv_0.check_empty_children(materials=True, substances=True)

        spec_0_0 = spec_0.specifications[0]
        specv_0_0 = SpecificationValidator(spec_0_0)
        assert specv_0_0.check_reference(record_history_identity="987654")
        specv_0_0_result = [
            indicators.WatchListFlag.WatchListAllSubstancesBelowThreshold,
            indicators.RoHSFlag.RohsCompliant,
        ]
        assert specv_0_0.check_indicators(specv_0_0_result)
        assert specv_0_0.check_bom_structure()
        assert specv_0_0.check_empty_children(materials=True, specifications=True, coatings=True)

        spec_1 = response.compliance_by_specification_and_indicator[1]
        specv_1 = SpecificationValidator(spec_1)
        assert specv_1.check_reference(record_guid="3df206df-9fc8-4859-90d4-3519764f8b55")
        spec_1_result = [
            indicators.WatchListFlag.WatchListHasSubstanceAboveThreshold,
            indicators.RoHSFlag.RohsNonCompliant,
        ]
        assert specv_1.check_indicators(spec_1_result)
        assert specv_1.check_bom_structure()
        assert specv_1.check_empty_children(specifications=True, coatings=True)

    def test_compliance_by_specification_and_indicator_materials(self, mock_connection):
        response = self.get_mocked_response(mock_connection)

        coating_0_0 = response.compliance_by_specification_and_indicator[0].coatings[0]
        assert coating_0_0.substances[0].percentage_amount == 0.0
        cv_0_0 = CoatingValidator(coating_0_0)
        assert cv_0_0.check_reference(record_history_identity="987654")
        coating_0_0_result = [
            indicators.WatchListFlag.WatchListAllSubstancesBelowThreshold,
            indicators.RoHSFlag.RohsCompliant,
        ]
        assert cv_0_0.check_indicators(coating_0_0_result)
        assert cv_0_0.check_bom_structure()
        assert cv_0_0.check_empty_children()

    def test_compliance_by_specification_and_indicator_coatings(self, mock_connection):
        response = self.get_mocked_response(mock_connection)

        material_1_0 = response.compliance_by_specification_and_indicator[1].materials[0]
        assert material_1_0.substances[0].percentage_amount == 0.1
        mv_1_0 = MaterialValidator(material_1_0)
        assert mv_1_0.check_reference(record_history_identity="111111")
        material_1_0_result = [
            indicators.WatchListFlag.WatchListAllSubstancesBelowThreshold,
            indicators.RoHSFlag.RohsCompliant,
        ]
        assert mv_1_0.check_indicators(material_1_0_result)
        assert mv_1_0.check_bom_structure()
        assert mv_1_0.check_empty_children()

    def test_compliance_by_specification_and_indicator_substances(self, mock_connection):
        response = self.get_mocked_response(mock_connection)

        substance_0_coating_0_0 = response.compliance_by_specification_and_indicator[0].coatings[0].substances[0]
        assert substance_0_coating_0_0.percentage_amount == 0.0
        sv_0_0_0 = SubstanceValidator(substance_0_coating_0_0)
        assert sv_0_0_0.check_reference(record_history_identity="62345")
        substance_0_0_result = [
            indicators.WatchListFlag.WatchListNotImpacted,
            indicators.RoHSFlag.RohsNotImpacted,
        ]
        assert sv_0_0_0.check_indicators(substance_0_0_result)
        assert sv_0_0_0.check_bom_structure()

        substance_1_0 = response.compliance_by_specification_and_indicator[1].substances[0]
        assert substance_1_0.percentage_amount == 0.1
        sv_1_0 = SubstanceValidator(substance_1_0)
        assert sv_1_0.check_reference(record_history_identity="12345")
        substance_1_0_result = [
            indicators.WatchListFlag.WatchListBelowThreshold,
            indicators.RoHSFlag.RohsBelowThreshold,
        ]
        assert sv_1_0.check_indicators(substance_1_0_result)
        assert sv_1_0.check_bom_structure()

        substance_1_1 = response.compliance_by_specification_and_indicator[1].substances[1]
        assert substance_1_1.percentage_amount is None
        sv_1_1 = SubstanceValidator(substance_1_1)
        assert sv_1_1.check_reference(record_history_identity="34567")
        substance_1_1_result = [
            indicators.WatchListFlag.WatchListAboveThreshold,
            indicators.RoHSFlag.RohsAboveThreshold,
        ]
        assert sv_1_1.check_indicators(substance_1_1_result)
        assert sv_1_1.check_bom_structure()

        substance_1_material_0_0 = response.compliance_by_specification_and_indicator[1].materials[0].substances[0]
        assert substance_1_material_0_0.percentage_amount == 0.1
        sv_1_0_0 = SubstanceValidator(substance_1_material_0_0)
        assert sv_1_0_0.check_reference(record_history_identity="12345")
        substance_1_0_0_result = [
            indicators.WatchListFlag.WatchListBelowThreshold,
            indicators.RoHSFlag.RohsBelowThreshold,
        ]
        assert sv_1_0_0.check_indicators(substance_1_0_0_result)
        assert sv_1_0_0.check_bom_structure()

        substance_1_material_1_0 = response.compliance_by_specification_and_indicator[1].materials[1].substances[0]
        assert substance_1_material_1_0.percentage_amount == 0.1
        sv_1_1_0 = SubstanceValidator(substance_1_material_1_0)
        assert sv_1_1_0.check_reference(record_history_identity="12345")
        substance_1_1_0_result = [
            indicators.WatchListFlag.WatchListBelowThreshold,
            indicators.RoHSFlag.RohsBelowThreshold,
        ]
        assert sv_1_1_0.check_indicators(substance_1_1_0_result)
        assert sv_1_1_0.check_bom_structure()

        substance_1_material_1_1 = response.compliance_by_specification_and_indicator[1].materials[1].substances[1]
        assert substance_1_material_1_1.percentage_amount == 1.1
        sv_1_1_1 = SubstanceValidator(substance_1_material_1_1)
        assert sv_1_1_1.check_reference(record_history_identity="34567")
        substance_1_1_1_result = [
            indicators.WatchListFlag.WatchListAboveThreshold,
            indicators.RoHSFlag.RohsAboveThreshold,
        ]
        assert sv_1_1_1.check_indicators(substance_1_1_1_result)
        assert sv_1_1_1.check_bom_structure()

    def test_compliance_by_indicator(self, mock_connection):
        response = self.get_mocked_response(mock_connection)
        assert len(response.compliance_by_indicator) == 2
        result = [
            indicators.WatchListFlag.WatchListHasSubstanceAboveThreshold,
            indicators.RoHSFlag.RohsNonCompliant,
        ]
        assert all(
            [actual.flag == expected for actual, expected in zip(response.compliance_by_indicator.values(), result)]
        )

    def test_indicator_results_are_separate_objects(self, mock_connection):
        response = self.get_mocked_response(mock_connection)

        for result in response.compliance_by_specification_and_indicator:
            for k, v in result.indicators.items():
                assert k in self.query._indicators  # The indicator name should be the same (string equality)
                assert v is not self.query._indicators[k]  # The indicator object should be a copy (non-identity)

    def test_query_result_repr(self, mock_connection):
        response = self.get_mocked_response(mock_connection)
        assert repr(response) == "<SpecificationComplianceQueryResult: 2 SpecificationWithCompliance results>"

    def test_compliance_by_indicator_repr(self, mock_connection):
        response = self.get_mocked_response(mock_connection)
        for indicator in response.compliance_by_indicator.keys():
            assert indicator in repr(response.compliance_by_indicator)

    def test_compliance_by_specification_and_indicator_repr(self, mock_connection):
        response = self.get_mocked_response(mock_connection)
        assert "SpecificationWithComplianceResult" in repr(response.compliance_by_specification_and_indicator)
