from query_managers import BoMComplianceQuery, BoMImpactedSubstancesQuery

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
                                <recordGUID xmlns="http://www.grantadesign.com/12/05/GrantaBaseTypes">
                                    41656452-1b2c-4ded-ad1b-1df8b3cf6e7e
                                </recordGUID>
                                <recordHistoryGUID xmlns="http://www.grantadesign.com/12/05/GrantaBaseTypes">
                                    af1cb650-6db5-49d6-b4a2-0eee9a090207
                                </recordHistoryGUID>
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
                                <recordGUID xmlns="http://www.grantadesign.com/12/05/GrantaBaseTypes">
                                    15069d02-9475-4f05-8810-57de68a2e9cc
                                </recordGUID>
                                <recordHistoryGUID xmlns="http://www.grantadesign.com/12/05/GrantaBaseTypes">
                                    12ef41e5-0417-409e-b94b-bc79e7787db9
                                </recordHistoryGUID>
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
    response = BoMImpactedSubstancesQuery(connection) \
                   .set_bom(bom) \
                   .add_legislations(['The SIN List 2.1 (Substitute It Now!)']) \
                   .execute()
    pass


def test_compliance(connection, indicators):
    response = BoMComplianceQuery(connection) \
        .set_bom(bom) \
        .add_indicators(indicators) \
        .execute()

