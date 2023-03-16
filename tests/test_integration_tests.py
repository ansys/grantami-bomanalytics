import pytest
from .inputs import sample_bom_complex, sample_bom_custom_db
from ansys.grantami.bomanalytics import queries, GrantaMIException
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


@pytest.mark.parametrize(
    "configurable_connection, bom",
    [(False, sample_bom_complex), (True, sample_bom_custom_db)],
    indirect=["configurable_connection"],
)
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


@pytest.mark.parametrize("configurable_connection", ["MI_Missing_Database"], indirect=["configurable_connection"])
def test_missing_database_raises_grantami_exception(configurable_connection):
    query = queries.MaterialImpactedSubstancesQuery().with_material_ids(["mat_id"]).with_legislations(LEGISLATIONS)
    with pytest.raises(GrantaMIException) as e:
        configurable_connection.run(query)
    assert "None of the record references resolved to material records in 'MI_Missing_Database'." == str(e.value)


def test_missing_table_raises_grantami_exception(default_connection):
    query = queries.BomImpactedSubstancesQuery().with_bom(sample_bom_custom_db).with_legislations(LEGISLATIONS)
    with pytest.raises(GrantaMIException) as e:
        default_connection.run(query)
    assert "Table name" in str(e.value) and "not found in database" in str(e.value)


@pytest.mark.parametrize("configurable_connection", [True, False], indirect=True)
def test_yaml(configurable_connection):
    assert configurable_connection.run(queries.Yaml)


class TestActAsReadUser:
    def _run_query(self, connection):
        MATERIAL_ID = "plastic-abs-pc-flame"
        LEGISLATION_ID = "The SIN List 2.1 (Substitute It Now!)"
        mat_query = (
            queries.MaterialImpactedSubstancesQuery()
            .with_material_ids([MATERIAL_ID])
            .with_legislations([LEGISLATION_ID])
        )
        results = connection.run(mat_query)
        return results

    @pytest.mark.parametrize("configurable_connection", [True], indirect=True)
    def test_withdrawn_records_are_not_included(self, configurable_connection):
        results = self._run_query(configurable_connection)

        assert not results.messages

    @pytest.mark.parametrize("configurable_connection", [True], indirect=True)
    def test_withdrawn_records_return_warning_messages_if_not_acting_as_read(self, configurable_connection):
        del configurable_connection.rest_client.headers["X-Granta-ActAsReadUser"]
        results = self._run_query(configurable_connection)

        assert any(
            "has 1 substance row(s) having more than one linked substance. " in msg.message for msg in results.messages
        )
