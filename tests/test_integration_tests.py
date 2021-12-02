import pytest
from .inputs import sample_bom, sample_bom_complex
from ansys.grantami.bomanalytics import queries
from .common import LEGISLATIONS, INDICATORS


class TestMaterialQueries:
    ids = ["plastic-abs-pvc-flame", "plastic-pmma-pc"]

    def test_impacted_substances(self, connection):
        query = queries.MaterialImpactedSubstancesQuery().with_material_ids(self.ids).with_legislations(LEGISLATIONS)
        response = connection.run(query)
        assert response.impacted_substances
        assert response.impacted_substances_by_legislation
        assert response.impacted_substances_by_material_and_legislation

    def test_compliance(self, connection):
        query = queries.MaterialComplianceQuery().with_material_ids(self.ids).with_indicators(INDICATORS)
        response = connection.run(query)
        assert response.compliance_by_indicator
        assert response.compliance_by_material_and_indicator


class TestPartQueries:
    ids = ["DRILL", "asm_flap_mating"]

    def test_impacted_substances(self, connection):
        query = queries.PartImpactedSubstancesQuery().with_part_numbers(self.ids).with_legislations(LEGISLATIONS)
        response = connection.run(query)

        assert response.impacted_substances
        assert response.impacted_substances_by_legislation
        assert response.impacted_substances_by_part_and_legislation

    def test_compliance(self, connection):
        query = queries.PartComplianceQuery().with_part_numbers(self.ids).with_indicators(INDICATORS)
        response = connection.run(query)

        assert response.compliance_by_indicator
        assert response.compliance_by_part_and_indicator


class TestSpecificationQueries:
    ids = ["MIL-C-20218,TypeII", "MIL-PRF-24635,TypeII,Class1"]

    def test_impacted_substances(self, connection):
        query = (
            queries.SpecificationImpactedSubstancesQuery()
            .with_specification_ids(self.ids)
            .with_legislations(LEGISLATIONS)
        )
        response = connection.run(query)

        assert response.impacted_substances_by_specification_and_legislation
        assert response.impacted_substances_by_legislation
        assert response.impacted_substances

    def test_compliance(self, connection):
        query = queries.SpecificationComplianceQuery().with_specification_ids(self.ids).with_indicators(INDICATORS)
        response = connection.run(query)

        assert response.compliance_by_specification_and_indicator
        assert response.compliance_by_indicator


class TestSubstancesQueries:
    def test_compliance(self, connection):
        query = (
            queries.SubstanceComplianceQuery()
            .with_cas_numbers(["50-00-0", "57-24-9"])
            .with_cas_numbers_and_amounts([("1333-86-4", 25), ("75-74-1", 50)])
            .with_indicators(INDICATORS)
        )
        response = connection.run(query)

        assert response.compliance_by_substance_and_indicator
        assert response.compliance_by_indicator


@pytest.mark.parametrize("bom", [sample_bom, sample_bom_complex])
class TestBomQueries:
    def test_impacted_substances(self, bom, connection):
        query = queries.BomImpactedSubstancesQuery().with_bom(bom).with_legislations(LEGISLATIONS)
        response = connection.run(query)

        assert response.impacted_substances_by_legislation
        assert response.impacted_substances

    def test_compliance(self, bom, connection):
        query = queries.BomComplianceQuery().with_bom(bom).with_indicators(INDICATORS)
        response = connection.run(query)

        assert response.compliance_by_part_and_indicator
        assert response.compliance_by_indicator


def test_yaml(connection):
    assert connection.run(queries.Yaml)
