import json
from connection import Connection, RoHSIndicator, WatchListIndicator

connection = Connection(url='http://localhost/mi_servicelayer',
                        dbkey='MI_Restricted_Substances',
                        autologon=True)

query = connection.create_query()

# Build an query with materials, specs, and parts. Run an impacted substances query
query.add_material(material_id='plastic-abs-pvc-flame')
query.add_specification(record_history_guid='516b2b9b-c4cf-419f-8caa-238ba1e7b7e5')
query.add_part(record_history_identity=564732)
stk_object = [{'dbkey': 'MI_Restricted_Substances',
               'table': 'MaterialUniverse',
               'record_guid': 'eef13c81-9b04-4af3-8d68-3524ffce7035'}]
query.from_stk(stk_references=stk_object)
substance_result = query.get_impacted_substances_for_legislations(['The SIN List 2.1 (Substitute It Now!)'])

with open('substance_result.json', 'w') as f:
    json.dump(substance_result, f)


# Add a substance, and run a compliance query
query.add_substance(cas_number='50-00-0', percentage_threshold=1.0)
andys_noxious_substance_indicator = WatchListIndicator(name="Andy's disliked substances",
                                                       legislation_names=['GADSL',
                                                                          'California Proposition 65 List'],
                                                       default_threshold_percentage=2)
rohs_indicator = RoHSIndicator(name="RoHS 2",
                               legislation_names=['EU Directive 2011/65/EU (RoHS 2)'],
                               default_threshold_percentage=0.01)
compliance_result = query.get_compliance_for_indicators([andys_noxious_substance_indicator, rohs_indicator])
with open('compliance_result.json', 'w') as f:
    json.dump(compliance_result, f)
