import pytest

from ansys.grantami.bomanalytics import GrantaMIException, queries

from .common import INDICATORS, LEGISLATIONS
from .inputs import (
    sample_bom_1711,
    sample_bom_custom_db,
    sample_compliance_bom_1711,
    sample_sustainability_bom_2301,
)

pytestmark = pytest.mark.integration

indicators = list(INDICATORS.values())


class TestMaterialQueries:
    ids = ["plastic-abs-pvc-flame", "plastic-pmma-pc"]

    def test_impacted_substances(self, connection_with_db_variants):
        query = queries.MaterialImpactedSubstancesQuery().with_material_ids(self.ids).with_legislation_ids(LEGISLATIONS)
        response = connection_with_db_variants.run(query)
        assert response.impacted_substances
        assert response.impacted_substances_by_legislation
        assert response.impacted_substances_by_material[0].substances
        assert response.impacted_substances_by_material[0].substances_by_legislation

    def test_compliance(self, connection_with_db_variants):
        query = queries.MaterialComplianceQuery().with_material_ids(self.ids).with_indicators(indicators)
        response = connection_with_db_variants.run(query)
        assert response.compliance_by_indicator
        assert response.compliance_by_material_and_indicator


class TestPartQueries:
    ids = ["DRILL", "asm_flap_mating"]

    def test_impacted_substances(self, connection_with_db_variants):
        query = queries.PartImpactedSubstancesQuery().with_part_numbers(self.ids).with_legislation_ids(LEGISLATIONS)
        response = connection_with_db_variants.run(query)

        assert response.impacted_substances
        assert response.impacted_substances_by_legislation
        assert response.impacted_substances_by_part[0].substances
        assert response.impacted_substances_by_part[0].substances_by_legislation

    def test_compliance(self, connection_with_db_variants):
        query = queries.PartComplianceQuery().with_part_numbers(self.ids).with_indicators(indicators)
        response = connection_with_db_variants.run(query)

        assert response.compliance_by_indicator
        assert response.compliance_by_part_and_indicator


class TestSpecificationQueries:
    ids = ["MIL-DTL-53039,TypeI", "AMS2404,Class1"]

    def test_impacted_substances(self, connection_with_db_variants):
        query = (
            queries.SpecificationImpactedSubstancesQuery()
            .with_specification_ids(self.ids)
            .with_legislation_ids(LEGISLATIONS)
        )
        response = connection_with_db_variants.run(query)

        assert response.impacted_substances
        assert response.impacted_substances_by_legislation
        assert response.impacted_substances_by_specification[0].substances
        assert response.impacted_substances_by_specification[0].substances_by_legislation

    def test_compliance(self, connection_with_db_variants):
        query = queries.SpecificationComplianceQuery().with_specification_ids(self.ids).with_indicators(indicators)
        response = connection_with_db_variants.run(query)

        assert response.compliance_by_specification_and_indicator
        assert response.compliance_by_indicator


class TestSubstancesQueries:
    def test_compliance(self, connection_with_db_variants):
        query = (
            queries.SubstanceComplianceQuery()
            .with_cas_numbers(["50-00-0", "57-24-9"])
            .with_cas_numbers_and_amounts([("1333-86-4", 25), ("75-74-1", 50)])
            .with_indicators(indicators)
        )
        response = connection_with_db_variants.run(query)

        assert response.compliance_by_substance_and_indicator
        assert response.compliance_by_indicator


class TestBomQueries:
    @pytest.fixture
    def bom(self, connection_with_db_variants):
        if connection_with_db_variants._db_key == "MI_Restricted_Substances_Custom_Tables":
            return sample_bom_custom_db
        else:
            return sample_compliance_bom_1711

    @pytest.fixture
    def bom2301(self):
        _bom = sample_bom_1711.replace(
            "http://www.grantadesign.com/17/11/BillOfMaterialsEco",
            "http://www.grantadesign.com/23/01/BillOfMaterialsEco",
        )
        return _bom

    def test_impacted_substances(self, bom, connection_with_db_variants):
        query = queries.BomImpactedSubstancesQuery().with_bom(bom).with_legislation_ids(LEGISLATIONS)
        response = connection_with_db_variants.run(query)

        assert response.impacted_substances
        assert response.impacted_substances_by_legislation

        assert connection_with_db_variants.last_response.request.url.endswith("bom1711")

    def test_compliance(self, bom, connection_with_db_variants):
        query = queries.BomComplianceQuery().with_bom(bom).with_indicators(indicators)
        response = connection_with_db_variants.run(query)

        assert response.compliance_by_part_and_indicator
        assert response.compliance_by_indicator

        assert connection_with_db_variants.last_response.request.url.endswith("bom1711")

    def test_impacted_substances_2301(self, connection, bom2301):
        query = queries.BomImpactedSubstancesQuery().with_bom(bom2301).with_legislation_ids(LEGISLATIONS)
        response = connection.run(query)

        assert connection.last_response.request.url.endswith("bom2301")

    def test_compliance_2301(self, connection, bom2301):
        query = queries.BomComplianceQuery().with_bom(bom2301).with_indicators(indicators)
        response = connection.run(query)

        assert connection.last_response.request.url.endswith("bom2301")


class TestMissingDatabase:
    @pytest.fixture
    def connection_missing_db(self, connection):
        connection.set_database_details(database_key="MI_Missing_Database")
        return connection

    def test_missing_database_raises_grantami_exception(self, connection_missing_db):
        query = (
            queries.MaterialImpactedSubstancesQuery().with_material_ids(["mat_id"]).with_legislation_ids(LEGISLATIONS)
        )
        with pytest.raises(
            GrantaMIException,
            match="Legislation ID 'SINList' does not correspond to a legislation record in database "
            "'MI_Missing_Database'",
        ):
            connection_missing_db.run(query)


def test_missing_table_raises_grantami_exception(connection):
    query = queries.BomImpactedSubstancesQuery().with_bom(sample_bom_custom_db).with_legislation_ids(LEGISLATIONS)
    with pytest.raises(GrantaMIException) as e:
        connection.run(query)
    assert "Table name" in str(e.value) and "not found in database" in str(e.value)


def test_yaml(connection_with_db_variants):
    api_def = connection_with_db_variants._get_yaml()
    assert len(api_def) > 0


def test_licensing(connection_with_db_variants):
    resp = connection_with_db_variants._get_licensing_information()
    assert resp.restricted_substances is True
    assert resp.sustainability is True


class TestActAsReadUser:
    def _run_query(self, connection):
        MATERIAL_ID = "plastic-abs-pc-flame"
        LEGISLATION_ID = "SINList"
        mat_query = (
            queries.MaterialImpactedSubstancesQuery()
            .with_material_ids([MATERIAL_ID])
            .with_legislation_ids([LEGISLATION_ID])
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
            .with_legislation_ids(self.legislation_ids)
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
            .with_legislation_ids(self.legislation_ids)
        )
        response = connection_custom_db.run(query)
        assert len(response.impacted_substances) == 0


DEFAULT_TOLERANCE = 0.01


class TestSustainabilityBomQueries:
    def _check_percentages_add_up(self, items):
        assert sum(item.embodied_energy_percentage for item in items) == pytest.approx(100)
        assert sum(item.climate_change_percentage for item in items) == pytest.approx(100)

    def test_sustainability_summary_query(self, connection):
        query = queries.BomSustainabilitySummaryQuery()
        query.with_bom(sample_sustainability_bom_2301)
        response = connection.run(query)

        assert not response.messages, "\n".join([f"{m.severity}: {m.message}" for m in response.messages])

        assert response.process.name == "Processes"
        assert response.material.name == "Material"
        assert response.transport.name == "Transport"
        assert len(response.phases_summary) == 3

        # Check overall percentages add up
        self._check_percentages_add_up(response.phases_summary)

        # Check expected summaries for materials
        assert len(response.material_details) == 3
        material_names = [m.identity for m in response.material_details]
        expected_material_names = ["beryllium-beralcast191-cast", "stainless-astm-cn-7ms-cast", "steel-1010-annealed"]
        assert all(expected_name in material_names for expected_name in expected_material_names)
        self._check_percentages_add_up(response.material_details)

        # Spot check one material summary
        beryllium_summary = next(m for m in response.material_details if m.identity == "beryllium-beralcast191-cast")
        assert len(beryllium_summary.contributors) == 1
        assert beryllium_summary.contributors[0].name == "Part1.D"
        assert beryllium_summary.contributors[0].part_number == "Part1.D[LeafPart]"
        assert beryllium_summary.contributors[0].material_mass_before_processing.value == pytest.approx(0.027)
        assert beryllium_summary.mass_after_processing.value == pytest.approx(0.024)
        assert beryllium_summary.mass_before_processing.value == pytest.approx(0.027)
        assert beryllium_summary.material_reference.record_guid is not None
        assert beryllium_summary.climate_change.value == pytest.approx(15.52, DEFAULT_TOLERANCE)
        assert beryllium_summary.climate_change_percentage == pytest.approx(54.32, DEFAULT_TOLERANCE)
        assert beryllium_summary.embodied_energy.value == pytest.approx(117.55, DEFAULT_TOLERANCE)
        assert beryllium_summary.embodied_energy_percentage == pytest.approx(41.04, DEFAULT_TOLERANCE)

        # Check expected summaries for primary processes
        assert len(response.primary_processes_details) == 3
        expected_primary_processes = [
            ("Primary processing, Casting", "stainless-astm-cn-7ms-cast"),
            ("Primary processing, Casting", "steel-1010-annealed"),
            ("Other", None),
        ]
        primary_processes = [(p.process_name, p.material_identity) for p in response.primary_processes_details]
        assert primary_processes == expected_primary_processes
        self._check_percentages_add_up(response.primary_processes_details)

        # Spot check primary process
        primary_process = response.primary_processes_details[1]
        assert primary_process.climate_change.value == pytest.approx(14.54, DEFAULT_TOLERANCE)
        assert primary_process.embodied_energy.value == pytest.approx(210.68, DEFAULT_TOLERANCE)
        assert primary_process.climate_change_percentage == pytest.approx(39.40, DEFAULT_TOLERANCE)
        assert primary_process.embodied_energy_percentage == pytest.approx(39.22, DEFAULT_TOLERANCE)
        assert primary_process.material_reference.record_guid is not None
        assert primary_process.process_reference.record_guid is not None

        # Check expected summaries for secondary processes
        assert len(response.secondary_processes_details) == 4
        expected_secondary_processes = [
            ("Secondary processing, Grinding", "steel-1010-annealed"),
            ("Secondary processing, Machining, coarse", "stainless-astm-cn-7ms-cast"),
            ("Machining, fine", "steel-1010-annealed"),
            ("Other", None),
        ]
        secondary_processes = [(p.process_name, p.material_identity) for p in response.secondary_processes_details]
        assert secondary_processes == expected_secondary_processes
        self._check_percentages_add_up(response.secondary_processes_details)

        # Spot check secondary process
        secondary_process = response.secondary_processes_details[0]
        assert secondary_process.climate_change.value == pytest.approx(0.127, DEFAULT_TOLERANCE)
        assert secondary_process.embodied_energy.value == pytest.approx(1.95, DEFAULT_TOLERANCE)
        assert secondary_process.climate_change_percentage == pytest.approx(44.94, DEFAULT_TOLERANCE)
        assert secondary_process.embodied_energy_percentage == pytest.approx(44.94, DEFAULT_TOLERANCE)
        assert secondary_process.material_reference.record_guid is not None
        assert secondary_process.process_reference.record_guid is not None

        # Check expected summaries for J&F processes
        assert len(response.joining_and_finishing_processes_details) == 1
        jf_process = response.joining_and_finishing_processes_details[0]

        # Spot check one J&F process
        assert jf_process.process_name == "Joining and finishing, Welding, electric"
        assert jf_process.material_identity is None
        assert jf_process.climate_change.value == pytest.approx(0.23, DEFAULT_TOLERANCE)
        assert jf_process.embodied_energy.value == pytest.approx(3.21, DEFAULT_TOLERANCE)
        assert jf_process.climate_change_percentage == 100.0
        assert jf_process.embodied_energy_percentage == 100.0
        assert jf_process.process_reference.record_guid is not None

        # Check transports
        assert len(response.transport_details) == 3
        self._check_percentages_add_up(response.transport_details)
        transports = [t.name for t in response.transport_details]
        assert transports == [
            "Port to airport by truck",
            "Country 1 to country 2 by air",
            "Airport to distributor by truck",
        ]

        # Spot check one transport
        transport = response.transport_details[0]
        assert transport.climate_change.value == pytest.approx(0.345, DEFAULT_TOLERANCE)
        assert transport.embodied_energy.value == pytest.approx(5.23, DEFAULT_TOLERANCE)
        assert transport.climate_change_percentage == pytest.approx(6.44, DEFAULT_TOLERANCE)
        assert transport.embodied_energy_percentage == pytest.approx(6.809, DEFAULT_TOLERANCE)
        assert transport.distance.value == 350.0

    def test_sustainability_query(self, connection):
        query = queries.BomSustainabilityQuery()
        query.with_bom(sample_sustainability_bom_2301)
        response = connection.run(query)

        assert not response.messages, "\n".join([f"{m.severity}: {m.message}" for m in response.messages])

        # Product
        product = response.part
        assert not product.processes
        assert not product.materials

        assert product.input_part_number == "Part1[ProductAssembly]"
        assert product._reference_value is None
        assert product.reported_mass.value == pytest.approx(4.114, DEFAULT_TOLERANCE)
        assert product.climate_change.value == pytest.approx(71.40, DEFAULT_TOLERANCE)
        assert product.embodied_energy.value == pytest.approx(908.04, DEFAULT_TOLERANCE)

        assert len(product.parts) == 5

        # Subassembly
        subassembly = product.parts[0]
        assert len(subassembly.parts) == 2
        assert len(subassembly.processes) == 1
        assert not subassembly.materials

        assert subassembly.input_part_number == "Part1.1[SubAssembly]"
        assert subassembly._reference_value is None
        assert subassembly.reported_mass.value == pytest.approx(1.45, DEFAULT_TOLERANCE)
        assert subassembly.climate_change.value == pytest.approx(29.996, DEFAULT_TOLERANCE)
        assert subassembly.embodied_energy.value == pytest.approx(419.21, DEFAULT_TOLERANCE)

        # JF process
        jf_process = subassembly.processes[0]
        assert jf_process.climate_change.value == pytest.approx(0.23, DEFAULT_TOLERANCE)
        assert jf_process.embodied_energy.value == pytest.approx(3.217, DEFAULT_TOLERANCE)
        assert jf_process.record_guid is not None

        # Leaf part
        leaf_part = product.parts[1]

        assert not leaf_part.parts
        assert not leaf_part.processes
        assert len(leaf_part.materials) == 1

        assert leaf_part.input_part_number == "Part1.A[LeafPart]"
        assert leaf_part._reference_value is None
        assert leaf_part.climate_change.value == pytest.approx(1.62, DEFAULT_TOLERANCE)
        assert leaf_part.embodied_energy.value == pytest.approx(23.23, DEFAULT_TOLERANCE)
        assert leaf_part.reported_mass.value == pytest.approx(0.61, DEFAULT_TOLERANCE)

        # Leaf part -> Material
        material = leaf_part.materials[0]

        assert len(material.processes) == 2

        assert material.record_guid is not None
        assert material.climate_change.value == pytest.approx(0.939, DEFAULT_TOLERANCE)
        assert material.embodied_energy.value == pytest.approx(12.63, DEFAULT_TOLERANCE)
        assert material.reported_mass.value == pytest.approx(0.61, DEFAULT_TOLERANCE)
        assert material.recyclable is True
        assert material.functional_recycle is True
        assert material.biodegradable is False

        # Primary process
        primary_process = material.processes[0]
        assert primary_process.record_guid is not None
        assert primary_process.climate_change.value == pytest.approx(0.643, DEFAULT_TOLERANCE)
        assert primary_process.embodied_energy.value == pytest.approx(9.908, DEFAULT_TOLERANCE)

        # Secondary process
        secondary_process = material.processes[1]
        assert secondary_process.record_guid is not None
        assert secondary_process.climate_change.value == pytest.approx(0.043, DEFAULT_TOLERANCE)
        assert secondary_process.embodied_energy.value == pytest.approx(0.661, DEFAULT_TOLERANCE)

        # Transports
        assert len(response.transport_stages) == 3

        transport = response.transport_stages[0]
        assert transport.name == "Port to airport by truck"
        assert transport.climate_change.value == pytest.approx(0.345, DEFAULT_TOLERANCE)
        assert transport.embodied_energy.value == pytest.approx(5.23, DEFAULT_TOLERANCE)
        assert transport.record_guid is not None
