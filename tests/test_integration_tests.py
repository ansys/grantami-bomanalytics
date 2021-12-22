import pytest
from .inputs import sample_bom_complex, sample_bom_custom_db
from ansys.grantami.bomanalytics import queries
from .common import LEGISLATIONS, INDICATORS

pytestmark = pytest.mark.integration

indicators = list(INDICATORS.values())


@pytest.mark.parametrize("configurable_connection", [True, False], indirect=True)
class TestMaterialQueries:
    ids = ["plastic-abs-pvc-flame", "plastic-pmma-pc"]

    def test_impacted_substances(self, configurable_connection):
        query = queries.MaterialImpactedSubstancesQuery().with_material_ids(self.ids).with_legislations(LEGISLATIONS)
        response = configurable_connection.run(query)
        assert response.impacted_substances
        assert response.impacted_substances_by_legislation
        assert response.impacted_substances_by_material[0].substances
        assert response.impacted_substances_by_material[0].substances_by_legislation

    def test_compliance(self, configurable_connection):
        query = queries.MaterialComplianceQuery().with_material_ids(self.ids).with_indicators(indicators)
        response = configurable_connection.run(query)
        assert response.compliance_by_indicator
        assert response.compliance_by_material_and_indicator


@pytest.mark.parametrize("configurable_connection", [True, False], indirect=True)
class TestPartQueries:
    ids = ["DRILL", "asm_flap_mating"]

    def test_impacted_substances(self, configurable_connection):
        query = queries.PartImpactedSubstancesQuery().with_part_numbers(self.ids).with_legislations(LEGISLATIONS)
        response = configurable_connection.run(query)

        assert response.impacted_substances
        assert response.impacted_substances_by_legislation
        assert response.impacted_substances_by_part[0].substances
        assert response.impacted_substances_by_part[0].substances_by_legislation

    def test_compliance(self, configurable_connection):
        query = queries.PartComplianceQuery().with_part_numbers(self.ids).with_indicators(indicators)
        response = configurable_connection.run(query)

        assert response.compliance_by_indicator
        assert response.compliance_by_part_and_indicator


@pytest.mark.parametrize("configurable_connection", [True, False], indirect=True)
class TestSpecificationQueries:
    ids = ["MIL-DTL-53039,TypeI", "AMS2404,Class1"]

    def test_impacted_substances(self, configurable_connection):
        query = (
            queries.SpecificationImpactedSubstancesQuery()
            .with_specification_ids(self.ids)
            .with_legislations(LEGISLATIONS)
        )
        response = configurable_connection.run(query)

        assert response.impacted_substances
        assert response.impacted_substances_by_legislation
        assert response.impacted_substances_by_specification[0].substances
        assert response.impacted_substances_by_specification[0].substances_by_legislation

    def test_compliance(self, configurable_connection):
        query = queries.SpecificationComplianceQuery().with_specification_ids(self.ids).with_indicators(indicators)
        response = configurable_connection.run(query)

        assert response.compliance_by_specification_and_indicator
        assert response.compliance_by_indicator


@pytest.mark.parametrize("configurable_connection", [True, False], indirect=True)
class TestSubstancesQueries:
    def test_compliance(self, configurable_connection):
        query = (
            queries.SubstanceComplianceQuery()
            .with_cas_numbers(["50-00-0", "57-24-9"])
            .with_cas_numbers_and_amounts([("1333-86-4", 25), ("75-74-1", 50)])
            .with_indicators(indicators)
        )
        response = configurable_connection.run(query)

        assert response.compliance_by_substance_and_indicator
        assert response.compliance_by_indicator


@pytest.mark.parametrize("configurable_connection, bom",
                         [(False, sample_bom_complex), (True, sample_bom_custom_db)],
                         indirect=["configurable_connection"])
class TestBomQueries:
    def test_impacted_substances(self, bom, configurable_connection):
        query = queries.BomImpactedSubstancesQuery().with_bom(bom).with_legislations(LEGISLATIONS)
        response = configurable_connection.run(query)

        assert response.impacted_substances
        assert response.impacted_substances_by_legislation

    def test_compliance(self, bom, configurable_connection):
        query = queries.BomComplianceQuery().with_bom(bom).with_indicators(indicators)
        response = configurable_connection.run(query)

        assert response.compliance_by_part_and_indicator
        assert response.compliance_by_indicator


@pytest.mark.parametrize("configurable_connection", [True, False], indirect=True)
def test_yaml(configurable_connection):
    assert configurable_connection.run(queries.Yaml)
