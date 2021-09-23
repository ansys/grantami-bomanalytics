from ansys.granta.bom_analytics import PartComplianceQuery, PartImpactedSubstanceQuery
from ..common import LEGISLATIONS, INDICATORS

part_numbers = ["DRILL", "main_frame"]


def test_impacted_substances(connection):
    response = (
        PartImpactedSubstanceQuery().add_part_numbers(part_numbers).add_legislations(LEGISLATIONS).execute(connection)
    )

    assert len(response.impacted_substances_by_part_and_legislation) == 2
    for part_results in response.impacted_substances_by_part_and_legislation:
        assert part_results.part_number in part_numbers
        assert len(part_results.legislations) in [1, 2]
        for name, legislation in part_results.legislations.items():
            assert len(legislation.substances) in [79, 7, 1]

    assert len(response.impacted_substances_by_legislation) == 2
    for name, legislation in response.impacted_substances_by_legislation.items():
        assert len(legislation) in [80, 7]

    assert len(response.impacted_substances) == 87


def test_compliance(connection):
    response = PartComplianceQuery().add_part_numbers(part_numbers).add_indicators(INDICATORS).execute(connection)

    assert len(response.compliance_by_part_and_indicator) == 2
    for part_results in response.compliance_by_part_and_indicator:
        assert part_results.part_number in part_numbers
        assert len(part_results.indicators) == len(INDICATORS)
        for child_part in part_results.parts:
            assert child_part.record_history_identity
        for indicator in INDICATORS:
            indicator_result = part_results.indicators[indicator.name]
            assert indicator_result.name == indicator.name
            assert indicator_result.flag
        assert not part_results.substances  # Empty list, no substances

    assert len(response.compliance_by_indicator) == 2
    for indicator in INDICATORS:
        indicator_result = response.compliance_by_indicator[indicator.name]
        assert indicator_result.name == indicator.name
        assert indicator_result.flag
