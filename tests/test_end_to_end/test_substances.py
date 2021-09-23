from ansys.granta.bom_analytics import SubstanceComplianceQuery
from ..common import INDICATORS


def test_compliance(connection):
    response = (
        SubstanceComplianceQuery()
        .add_cas_numbers(["50-00-0", "57-24-9"])
        .add_cas_numbers_with_amounts([("1333-86-4", 25), ("75-74-1", 50)])
        .add_indicators(INDICATORS)
        .execute(connection)
    )

    assert len(response.compliance_by_substance_and_indicator) == 4
    for sub_results in response.compliance_by_substance_and_indicator:
        assert sub_results.cas_number in ["50-00-0", "57-24-9", "1333-86-4", "75-74-1"]
        assert len(sub_results.indicators) == len(INDICATORS)
        for ind in INDICATORS:
            indicator_result = sub_results.indicators[ind.name]
            assert indicator_result.name == ind.name
            assert indicator_result.flag

    assert len(response.compliance_by_indicator) == 2
    for indicator in INDICATORS:
        indicator_result = response.compliance_by_indicator[indicator.name]
        assert indicator_result.name == indicator.name
        assert indicator_result.flag
