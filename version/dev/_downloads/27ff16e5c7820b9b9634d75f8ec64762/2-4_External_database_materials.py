# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.17.3
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# # Perform an impacted substances query on materials in an external database

# > Added in version 2.4. Requires MI Restricted Substances and Sustainability Reports 2026 R1 or later.

# Material records stored in other Granta MI databases can be included in impacted substances queries by providing the
# ``external_database_key`` argument to methods such as ``.with_record_history_guids()`` or ``.with_material_ids()``.
# This feature also works for compliance and sustainability queries. For more information, including pre-requisites, see
# the [Using external records in analysis](../../user_guide/external_records.rst) user guide.

# This example shows how to perform an impacted substances query on material records stored in an external database
# and how to interpret the results.

# ## Pre-requisites

# The example can be run using the MI_Training database that is included with Granta MI. However, to see the expected
# results, make the following additions to the MI Training database:
#
# 1. Create the following two static record link groups between the specified tables:
#   * The 'Design Data' table (MI Training) to the 'MaterialUniverse' table (Restricted Substances & Sustainability).
#   * The 'Composites Design Data' table (MI Training) to the 'MaterialUniverse' table (Restricted Substances &
#      Sustainability).
# 2. Create a Standard Name 'RS and Sustainability record', and map to both record link groups.
# 3. Link the following records:
#   * Link the MI Training Design Data record 'Nickel alloys, Inconel 718, Forging' to the MaterialUniverse record
#     'Nickel-chromium alloy, INCONEL 718, solution treated'
#   * Link the MI Training Composites Design Data record 'S-Glass Unitape S2/SP381, 3M, [0], CTD' to the
#     MaterialUniverse record 'Epoxy/S-glass fiber, UD prepreg, UD lay-up'.

# ## Connect to Granta MI

# Import the ``Connection`` class and create the connection. For more information, see the
# [Basic Usage](../0_Basic_usage.ipynb) example.

# +
from ansys.grantami.bomanalytics import Connection

server_url = "http://my_grantami_server/mi_servicelayer"
cxn = Connection(server_url).with_credentials("user_name", "password").connect()
# -

# ## Build and run the query

# The ``external_database_key`` argument is provided alongside the record history GUIDs of the material records to
# indicate that the records are stored in an external database.

# +
from ansys.grantami.bomanalytics import queries

EXTERNAL_DB_KEY = "MI_Training"
SIN_LIST = "SINList"

EPOXY_GLASS_GUID = "5f9563c4-17f8-4ed9-ae43-d48f025d9ce5"
INCONEL_GUID = "ce294339-e59d-4be1-a96c-f9e92adb71ac"

external_mat_query = (
    queries.MaterialImpactedSubstancesQuery()
    .with_record_history_guids(
        record_history_guids=[EPOXY_GLASS_GUID, INCONEL_GUID],
        external_database_key=EXTERNAL_DB_KEY,
    )
    .with_legislation_ids([SIN_LIST])
)
external_mat_query
# -

results = cxn.run(external_mat_query)
results

# ## Equivalent references

# The result objects reference the linked records in the Restricted Substances database. To allow results to be
# correlated back to the originally-specified external records, each result object includes an
# ``equivalent_references`` property.
#
# The ``equivalent_references`` property contains a list of references to the originally-specified external records.

# +
material_result = results.impacted_substances_by_material[0]
print(f"Record GUID (in RS database): {material_result.record_guid}")

external_reference = material_result.equivalent_references[0]
print(f"External database key: {external_reference.database_key}")
print(f"External record history GUID: {external_reference.record_history_guid}")
# -

# Use this to display the impacted substances for the Epoxy/Glass Fiber material only:

# +
from tabulate import tabulate

substances_by_external_material_record_guid = {}
for material in results.impacted_substances_by_material:
    substances = material.substances_by_legislation[SIN_LIST]
    substances_by_external_material_record_guid[material.equivalent_references[0].record_history_guid] = substances

rows = [(substance.cas_number, substance.max_percentage_amount_in_material)
    for substance in substances_by_external_material_record_guid[EPOXY_GLASS_GUID]]

print(f'Substances impacted by "{SIN_LIST}" in Epoxy/Glass Fiber (5/{len(rows)})')
print(tabulate(rows[:5], headers=["CAS Number", "Amount (wt. %)"]))
