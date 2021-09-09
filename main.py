from connection import Connection
from indicators import WatchListIndicator, RoHSIndicator


connection = Connection(url='http://localhost/mi_servicelayer',
                        dbkey='MI_Restricted_Substances',
                        autologon=True)

andys_noxious_substance_indicator = WatchListIndicator(name="Andy's disliked substances",
                                                       legislation_names=['GADSL', 'California Proposition 65 List'],
                                                       default_threshold_percentage=2)

material_query = connection.create_material_query()
material_query.add_record_by_material_id('plastic-abs-pvc-flame')
stk_object = [{'dbkey': 'MI_Restricted_Substances',
               'record_guid': 'eef13c81-9b04-4af3-8d68-3524ffce7035'}]
material_query.add_stk_records(stk_object)
material_query.add_legislation('The SIN List 2.1 (Substitute It Now!)')
substance_result = material_query.get_impacted_substances()
print(substance_result)

rohs_indicator = RoHSIndicator(name="RoHS 2",
                               legislation_names=['EU Directive 2011/65/EU (RoHS 2)'],
                               default_threshold_percentage=0.01)
material_query.add_indicator(rohs_indicator)
compliance_result = material_query.get_compliance()
print(compliance_result)

spec_query = connection.create_specification_query()
spec_query.add_record_by_record_history_guid('516b2b9b-c4cf-419f-8caa-238ba1e7b7e5')
spec_query.add_legislation('The SIN List 2.1 (Substitute It Now!)')
print(spec_query.get_impacted_substances())

part_query = connection.create_part_query()
part_query.add_record_by_record_history_identity(564732)
part_query.add_legislation('The SIN List 2.1 (Substitute It Now!)')
print(part_query.get_impacted_substances())

substance_query = connection.create_substance_query()
substance_query.add_record_by_cas_number('50-00-0', 1.0)
substance_query.add_indicator(andys_noxious_substance_indicator)
rohs_indicator = RoHSIndicator(name="RoHS 2",
                               legislation_names=['EU Directive 2011/65/EU (RoHS 2)'],
                               default_threshold_percentage=0.01)
substance_query.add_indicator(rohs_indicator)
print(substance_query.get_compliance())

bom_query = connection.create_bom_query()
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
                                <dbKey xmlns="http://www.grantadesign.com/12/05/GrantaBaseTypes">MI_Product_Risk</dbKey>
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
                                <dbKey xmlns="http://www.grantadesign.com/12/05/GrantaBaseTypes">MI_Product_Risk</dbKey>
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

bom_query.set_bom(bom)
bom_query.add_indicator(rohs_indicator)
bom_query.add_indicator(andys_noxious_substance_indicator)
bom_response = bom_query.get_compliance()
print(bom_response)
