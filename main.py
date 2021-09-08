from connection import Connection
from indicators import WatchListIndicator, RoHSIndicator


connection = Connection(url='http://localhost/mi_servicelayer',
                        dbkey='MI_Restricted_Substances',
                        autologon=True)

andys_noxious_substance_indicator = WatchListIndicator(name="Andy's disliked substances",
                                                       legislation_names=['GADSL', 'California Proposition 65 List'],
                                                       default_threshold_percentage=2)

material_query = connection.create_material_query()
material_query.add_material_id('plastic-abs-pvc-flame')
stk_object = [{'dbkey': 'MI_Restricted_Substances',
               'record_guid': 'eef13c81-9b04-4af3-8d68-3524ffce7035'}]
material_query.add_stk_record(stk_object)
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
spec_query.add_record_history_guid('516b2b9b-c4cf-419f-8caa-238ba1e7b7e5')
spec_query.add_legislation('The SIN List 2.1 (Substitute It Now!)')
print(spec_query.get_impacted_substances())

part_query = connection.create_part_query()
part_query.add_record_history_identity(564732)
part_query.add_legislation('The SIN List 2.1 (Substitute It Now!)')
print(part_query.get_impacted_substances())

# Add a substance, and run a compliance query
substance_query = connection.create_substance_query()
substance_query.add_cas_number('50-00-0', 1.0)
substance_query.add_indicator(andys_noxious_substance_indicator)
rohs_indicator = RoHSIndicator(name="RoHS 2",
                               legislation_names=['EU Directive 2011/65/EU (RoHS 2)'],
                               default_threshold_percentage=0.01)
substance_query.add_indicator(rohs_indicator)
print(substance_query.get_compliance())
