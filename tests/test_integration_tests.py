import pytest

from ansys.grantami.bomanalytics import GrantaMIException, queries

from .common import INDICATORS, LEGISLATIONS
from .inputs import sample_bom_2301_complex, sample_bom_complex, sample_bom_custom_db

pytestmark = pytest.mark.integration

indicators = list(INDICATORS.values())


class TestMaterialQueries:
    ids = ["plastic-abs-pvc-flame", "plastic-pmma-pc"]

    def test_impacted_substances(self, parameterized_connection):
        query = queries.MaterialImpactedSubstancesQuery().with_material_ids(self.ids).with_legislations(LEGISLATIONS)
        response = parameterized_connection.run(query)
        assert response.impacted_substances
        assert response.impacted_substances_by_legislation
        assert response.impacted_substances_by_material[0].substances
        assert response.impacted_substances_by_material[0].substances_by_legislation

    def test_compliance(self, parameterized_connection):
        query = queries.MaterialComplianceQuery().with_material_ids(self.ids).with_indicators(indicators)
        response = parameterized_connection.run(query)
        assert response.compliance_by_indicator
        assert response.compliance_by_material_and_indicator


class TestPartQueries:
    ids = ["DRILL", "asm_flap_mating"]

    def test_impacted_substances(self, parameterized_connection):
        query = queries.PartImpactedSubstancesQuery().with_part_numbers(self.ids).with_legislations(LEGISLATIONS)
        response = parameterized_connection.run(query)

        assert response.impacted_substances
        assert response.impacted_substances_by_legislation
        assert response.impacted_substances_by_part[0].substances
        assert response.impacted_substances_by_part[0].substances_by_legislation

    def test_compliance(self, parameterized_connection):
        query = queries.PartComplianceQuery().with_part_numbers(self.ids).with_indicators(indicators)
        response = parameterized_connection.run(query)

        assert response.compliance_by_indicator
        assert response.compliance_by_part_and_indicator


class TestSpecificationQueries:
    ids = ["MIL-DTL-53039,TypeI", "AMS2404,Class1"]

    def test_impacted_substances(self, parameterized_connection):
        query = (
            queries.SpecificationImpactedSubstancesQuery()
            .with_specification_ids(self.ids)
            .with_legislations(LEGISLATIONS)
        )
        response = parameterized_connection.run(query)

        assert response.impacted_substances
        assert response.impacted_substances_by_legislation
        assert response.impacted_substances_by_specification[0].substances
        assert response.impacted_substances_by_specification[0].substances_by_legislation

    def test_compliance(self, parameterized_connection):
        query = queries.SpecificationComplianceQuery().with_specification_ids(self.ids).with_indicators(indicators)
        response = parameterized_connection.run(query)

        assert response.compliance_by_specification_and_indicator
        assert response.compliance_by_indicator


class TestSubstancesQueries:
    def test_compliance(self, parameterized_connection):
        query = (
            queries.SubstanceComplianceQuery()
            .with_cas_numbers(["50-00-0", "57-24-9"])
            .with_cas_numbers_and_amounts([("1333-86-4", 25), ("75-74-1", 50)])
            .with_indicators(indicators)
        )
        response = parameterized_connection.run(query)

        assert response.compliance_by_substance_and_indicator
        assert response.compliance_by_indicator


class TestBomQueries:
    @pytest.fixture
    def bom(self, parameterized_connection):
        if parameterized_connection._db_key == "MI_Restricted_Substances_Custom_Tables":
            return sample_bom_custom_db
        else:
            return sample_bom_complex

    def test_impacted_substances(self, bom, parameterized_connection):
        query = queries.BomImpactedSubstancesQuery().with_bom(bom).with_legislations(LEGISLATIONS)
        response = parameterized_connection.run(query)

        assert response.impacted_substances
        assert response.impacted_substances_by_legislation

    def test_compliance(self, bom, parameterized_connection):
        query = queries.BomComplianceQuery().with_bom(bom).with_indicators(indicators)
        response = parameterized_connection.run(query)

        assert response.compliance_by_part_and_indicator
        assert response.compliance_by_indicator


class TestMissingDatabase:
    @pytest.fixture
    def connection_missing_db(self, connection):
        connection.set_database_details(database_key="MI_Missing_Database")
        return connection

    def test_missing_database_raises_grantami_exception(self, connection_missing_db):
        query = queries.MaterialImpactedSubstancesQuery().with_material_ids(["mat_id"]).with_legislations(LEGISLATIONS)
        with pytest.raises(GrantaMIException) as e:
            connection_missing_db.run(query)
        assert str(e.value) == "None of the record references resolved to material records in 'MI_Missing_Database'."


def test_missing_table_raises_grantami_exception(connection):
    query = queries.BomImpactedSubstancesQuery().with_bom(sample_bom_custom_db).with_legislations(LEGISLATIONS)
    with pytest.raises(GrantaMIException) as e:
        connection.run(query)
    assert "Table name" in str(e.value) and "not found in database" in str(e.value)


def test_yaml(parameterized_connection):
    api_def = parameterized_connection._get_yaml()
    assert len(api_def) > 0


def test_licensing(parameterized_connection):
    resp = parameterized_connection._get_licensing_information()
    assert resp.restricted_substances is True
    assert resp.sustainability is True


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

    def test_withdrawn_records_are_not_included(self, connection_write_custom_db):
        results = self._run_query(connection_write_custom_db)

        assert not results.messages

    def test_withdrawn_records_return_warning_messages_if_not_acting_as_read(self, connection_write_custom_db):
        del connection_write_custom_db.rest_client.headers["X-Granta-ActAsReadUser"]
        results = self._run_query(connection_write_custom_db)

        assert any(
            "has 1 substance row(s) having more than one linked substance. " in msg.message for msg in results.messages
        )


class TestSpecLinkDepth:
    spec_ids = ["MIL-DTL-53039,TypeII"]
    legislation_ids = ["Candidate_AnnexXV"]

    def test_legislation_is_affected_with_link_depth_one(self, connection_custom_db):
        connection_custom_db.maximum_spec_link_depth = 1

        query = (
            queries.SpecificationImpactedSubstancesQuery()
            .with_specification_ids(self.spec_ids)
            .with_legislations(self.legislation_ids)
        )
        response = connection_custom_db.run(query)
        assert len(response.impacted_substances) == 1
        assert response.impacted_substances[0].cas_number == "872-50-4"
        assert len(response.impacted_substances_by_legislation) == 1
        legislation_name = self.legislation_ids[0]
        assert legislation_name in response.impacted_substances_by_legislation
        impacted_by_reach = response.impacted_substances_by_legislation[legislation_name]
        assert len(impacted_by_reach) == 1
        assert impacted_by_reach[0].cas_number == "872-50-4"

    def test_legislation_is_not_affected_with_no_links(self, connection_custom_db):
        connection_custom_db.maximum_spec_link_depth = 0

        query = (
            queries.SpecificationImpactedSubstancesQuery()
            .with_specification_ids(self.spec_ids)
            .with_legislations(self.legislation_ids)
        )
        response = connection_custom_db.run(query)
        assert len(response.impacted_substances) == 0


# TODO test with custom db?
class TestSustainabilityBomQueries:
    def test_sustainability_summary_query(self, connection):
        query = queries.BomSustainabilitySummaryQuery()
        query.with_bom(sample_bom_2301_complex)
        response = connection.run(query)

        assert response.process.name == "Processes"
        assert response.material.name == "Material"
        assert response.transport.name == "Transport"
        assert len(response.phases_summary) == 3

        assert len(response.material_details) == 3
        all_others = next(mat for mat in response.material_details if mat.identity == "Other")

    def test_sustainability_query(self, connection):
        query = queries.BomSustainabilityQuery()
        query.with_bom(sample_bom_2301_complex)
        response = connection.run(query)
