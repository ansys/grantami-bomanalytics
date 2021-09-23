from ansys.granta.bom_analytics import (
    MaterialImpactedSubstanceQuery,
    MaterialComplianceQuery,
)

from ..common import LEGISLATIONS, INDICATORS

material_ids = ["plastic-abs-pvc-flame", "plastic-pmma-pc"]


def test_impacted_substances(connection):
    response = (
        MaterialImpactedSubstanceQuery()
        .add_material_ids(material_ids)
        .add_legislations(LEGISLATIONS)
        .execute(connection)
    )
    assert response.impacted_substances
    assert response.impacted_substances_by_legislation
    assert response.impacted_substances_by_material_and_legislation


def test_compliance(connection):
    response = MaterialComplianceQuery().add_material_ids(material_ids).add_indicators(INDICATORS).execute(connection)
    assert response.compliance_by_indicator
    assert response.compliance_by_material_and_indicator
