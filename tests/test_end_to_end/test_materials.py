from ansys.granta.bom_analytics import (
    MaterialImpactedSubstanceQuery,
    MaterialComplianceQuery,
    WatchListIndicator,
    RoHSIndicator,
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

    assert len(response.impacted_substances_by_material_and_legislation) == 2
    for mat_results in response.impacted_substances_by_material_and_legislation:
        assert mat_results.material_id in material_ids
        assert len(mat_results.legislations) == len(LEGISLATIONS)
        for legislation in LEGISLATIONS:
            assert legislation in mat_results.legislations
            this_legislation = mat_results.legislations[legislation]
            assert this_legislation.name == legislation
            assert this_legislation.substances

    assert len(response.impacted_substances_by_legislation) == len(LEGISLATIONS)
    for name, legislation in response.impacted_substances_by_legislation.items():
        assert len(legislation) == 64 or len(legislation) == 5

    assert len(response.impacted_substances) == 69


def test_compliance(connection):
    response = MaterialComplianceQuery().add_material_ids(material_ids).add_indicators(INDICATORS).execute(connection)

    assert len(response.compliance_by_material_and_indicator) == 2
    for mat_results in response.compliance_by_material_and_indicator:
        assert mat_results.material_id in material_ids
        assert len(mat_results.indicators) == len(INDICATORS)
        for indicator in INDICATORS:
            indicator_result = mat_results.indicators[indicator.name]
            assert indicator_result.name == indicator.name
            assert indicator_result.flag in [
                WatchListIndicator.available_flags.WatchListAboveThreshold,
                RoHSIndicator.available_flags.RohsNotImpacted,
            ]
        assert len(mat_results.substances) in [51, 17]

    assert len(response.compliance_by_indicator) == 2
    for indicator in INDICATORS:
        indicator_result = response.compliance_by_indicator[indicator.name]
        assert indicator_result.name == indicator.name
        assert indicator_result.flag in [
            WatchListIndicator.available_flags.WatchListAboveThreshold,
            RoHSIndicator.available_flags.RohsNotImpacted,
        ]
