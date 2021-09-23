from ansys.granta.bom_analytics import (
    SpecificationComplianceQuery,
    SpecificationImpactedSubstanceQuery,
)
from ..common import LEGISLATIONS, INDICATORS


def test_impacted_substances(connection):
    response = (
        SpecificationImpactedSubstanceQuery()
        .add_record_history_guids(["516b2b9b-c4cf-419f-8caa-238ba1e7b7e5"])
        .add_specification_ids(["MIL-C-20218,TypeII"])
        .add_legislations(LEGISLATIONS)
        .execute(connection)
    )

    assert len(response.impacted_substances_by_specification_and_legislation) == 2
    for spec_results in response.impacted_substances_by_specification_and_legislation:
        if spec_results.record_history_guid:
            assert spec_results.record_history_guid == "516b2b9b-c4cf-419f-8caa-238ba1e7b7e5"
        if spec_results.specification_id:
            assert spec_results.specification_id == "MIL-C-20218,TypeII"
        assert len(spec_results.legislations) == 1
        assert "The SIN List 2.1 (Substitute It Now!)" in spec_results.legislations
        leg = spec_results.legislations["The SIN List 2.1 (Substitute It Now!)"]
        assert leg.name == "The SIN List 2.1 (Substitute It Now!)"
        assert leg.substances

    assert len(response.impacted_substances_by_legislation) == 1
    for name, legislation in response.impacted_substances_by_legislation.items():
        assert len(legislation) == 4

    assert len(response.impacted_substances) == 4


def test_compliance(connection):
    response = (
        SpecificationComplianceQuery()
        .add_record_history_guids(["516b2b9b-c4cf-419f-8caa-238ba1e7b7e5"])
        .add_specification_ids(["MIL-C-20218,TypeII"])
        .add_indicators(INDICATORS)
        .execute(connection)
    )

    assert len(response.compliance_by_specification_and_indicator) == 2
    for spec_results in response.compliance_by_specification_and_indicator:
        if spec_results.record_history_guid:
            assert spec_results.record_history_guid == "516b2b9b-c4cf-419f-8caa-238ba1e7b7e5"
        if spec_results.specification_id:
            assert spec_results.specification_id == "MIL-C-20218,TypeII"
        assert len(spec_results.indicators) == len(INDICATORS)
        for ind in INDICATORS:
            ind_res = spec_results.indicators[ind.name]
            assert ind_res.name == ind.name
            assert ind_res.flag

    assert len(response.compliance_by_indicator) == 2
    for indicator in INDICATORS:
        indicator_result = response.compliance_by_indicator[indicator.name]
        assert indicator_result.name == indicator.name
        assert indicator_result.flag
