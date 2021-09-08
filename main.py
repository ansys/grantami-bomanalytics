import json
from connection_named_params import Connection, RoHSIndicator, WatchListIndicator

connection = Connection(url='http://localhost/mi_servicelayer',
                        dbkey='MI_Restricted_Substances')

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
