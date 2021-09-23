from ansys.granta.bom_analytics import BomComplianceQuery, BomImpactedSubstanceQuery
from ..common import LEGISLATIONS, INDICATORS


bom = r"""<PartsEco xmlns="http://www.grantadesign.com/17/11/BillOfMaterialsEco" id="B0">
    <Components>
        <Part id="A0">
            <Quantity Unit="Each">2</Quantity>
            <PartNumber>123456789</PartNumber>
            <Name>Part One</Name>
            <Components>
                <Part>
                    <Quantity Unit="Each">1</Quantity>
                    <MassPerUom Unit="kg/Part">2</MassPerUom>
                    <PartNumber>987654321</PartNumber>
                    <Name>New Part One</Name>
                    <Substances>
                        <Substance>
                            <Percentage>66</Percentage>
                            <MISubstanceReference>
                                <dbKey xmlns="http://www.grantadesign.com/12/05/GrantaBaseTypes">MI_Restricted_Substances</dbKey>
                                <recordGUID xmlns="http://www.grantadesign.com/12/05/GrantaBaseTypes">41656452-1b2c-4ded-ad1b-1df8b3cf6e7e</recordGUID>
                                <recordHistoryGUID xmlns="http://www.grantadesign.com/12/05/GrantaBaseTypes">af1cb650-6db5-49d6-b4a2-0eee9a090207</recordHistoryGUID>
                            </MISubstanceReference>
                            <Name>Lead oxide</Name>
                        </Substance>
                    </Substances>
                </Part>
                <Part>
                    <Quantity Unit="Each">1</Quantity>
                    <MassPerUom Unit="kg/Part">2</MassPerUom>
                    <PartNumber>3333</PartNumber>
                    <Name>Part Two</Name>
                    <Materials>
                        <Material>
                            <Percentage>80</Percentage>
                            <MIMaterialReference>
                                <dbKey xmlns="http://www.grantadesign.com/12/05/GrantaBaseTypes">MI_Restricted_Substances</dbKey>
                                <recordGUID xmlns="http://www.grantadesign.com/12/05/GrantaBaseTypes">9ec40360-0cd7-44a4-9c8b-56d53452ae2c</recordGUID>
                                <recordHistoryGUID xmlns="http://www.grantadesign.com/12/05/GrantaBaseTypes">ab4147f6-0e97-47f0-be53-cb5d17dfa82b</recordHistoryGUID>
                            </MIMaterialReference>
                        </Material>
                    </Materials>
                </Part>
            </Components>
        </Part>
    </Components>
    <Notes>
        <Notes>Part with substance</Notes>
        <ProductName>Part with substance</ProductName>
    </Notes>
</PartsEco>"""


def test_impacted_substances(connection):
    response = BomImpactedSubstanceQuery().set_bom(bom).add_legislations(LEGISLATIONS).execute(connection)

    assert len(response.impacted_substances_by_legislation) == len(LEGISLATIONS)
    for legislation in LEGISLATIONS:
        assert legislation in response.impacted_substances_by_legislation
        substances = response.impacted_substances_by_legislation[legislation]
        assert len(substances) in [3, 39]

    assert len(response.impacted_substances) == 42


def test_compliance(connection):
    response = BomComplianceQuery().set_bom(bom).add_indicators(INDICATORS).execute(connection)

    assert len(response.compliance_by_part_and_indicator) == 1
    for bom_results in response.compliance_by_part_and_indicator:
        assert len(bom_results.indicators) == len(INDICATORS)
        for indicator in INDICATORS:
            indicator_result = bom_results.indicators[indicator.name]
            assert indicator_result.name == indicator.name
            assert indicator_result.flag
        assert bom_results.parts
        assert len(bom_results.substances) == 0

    assert len(response.compliance_by_indicator) == 2
    for indicator in INDICATORS:
        indicator_result = response.compliance_by_indicator[indicator.name]
        assert indicator_result.name == indicator.name
        assert indicator_result.flag
