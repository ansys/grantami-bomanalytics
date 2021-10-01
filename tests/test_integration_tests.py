from .common import (
    pathlib,
    queries,
    LEGISLATIONS,
    INDICATORS,
)


class TestMaterialQueries:
    ids = ["plastic-abs-pvc-flame", "plastic-pmma-pc"]

    def test_impacted_substances(self, connection):
        query = queries.MaterialImpactedSubstances().add_material_ids(self.ids).add_legislations(LEGISLATIONS)
        response = connection.run(query)
        assert response.impacted_substances
        assert response.impacted_substances_by_legislation
        assert response.impacted_substances_by_material_and_legislation

    def test_compliance(self, connection):
        query = queries.MaterialCompliance().add_material_ids(self.ids).add_indicators(INDICATORS)
        response = connection.run(query)
        assert response.compliance_by_indicator
        assert response.compliance_by_material_and_indicator


class TestPartQueries:
    ids = ["DRILL", "main_frame"]

    def test_impacted_substances(self, connection):
        query = queries.PartImpactedSubstances().add_part_numbers(self.ids).add_legislations(LEGISLATIONS)
        response = connection.run(query)

        assert response.impacted_substances
        assert response.impacted_substances_by_legislation
        assert response.impacted_substances_by_part_and_legislation

    def test_compliance(self, connection):
        query = queries.PartCompliance().add_part_numbers(self.ids).add_indicators(INDICATORS)
        response = connection.run(query)

        assert response.compliance_by_indicator
        assert response.compliance_by_part_and_indicator


class TestSpecificationQueries:
    ids = ["MIL-C-20218,TypeII", "MIL-PRF-24635,TypeII,Class1"]

    def test_impacted_substances(self, connection):
        query = queries.SpecificationImpactedSubstances().add_specification_ids(self.ids).add_legislations(LEGISLATIONS)
        response = connection.run(query)

        assert response.impacted_substances_by_specification_and_legislation
        assert response.impacted_substances_by_legislation
        assert response.impacted_substances

    def test_compliance(self, connection):
        query = queries.SpecificationCompliance().add_specification_ids(self.ids).add_indicators(INDICATORS)
        response = connection.run(query)

        assert response.compliance_by_specification_and_indicator
        assert response.compliance_by_indicator


class TestSubstancesQueries:
    def test_compliance(self, connection):
        query = (
            queries.SubstanceCompliance()
            .add_cas_numbers(["50-00-0", "57-24-9"])
            .add_cas_numbers_with_amounts([("1333-86-4", 25), ("75-74-1", 50)])
            .add_indicators(INDICATORS)
        )
        response = connection.run(query)

        assert response.compliance_by_substance_and_indicator
        assert response.compliance_by_indicator


class TestBomQueries:
    bom_path = pathlib.Path(__file__).parent / "bom.xml"
    with open(bom_path, "r") as f:
        bom = f.read()

    def test_impacted_substances(self, connection):
        query = queries.BomImpactedSubstances().set_bom(self.bom).add_legislations(LEGISLATIONS)
        response = connection.run(query)

        assert response.impacted_substances_by_legislation
        assert response.impacted_substances

    def test_compliance(self, connection):
        query = queries.BomCompliance().set_bom(self.bom).add_indicators(INDICATORS)
        response = connection.run(query)

        assert response.compliance_by_part_and_indicator
        assert response.compliance_by_indicator
