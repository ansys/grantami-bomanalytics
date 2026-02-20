# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# # Perform a material impacted substances query

# A Material Impacted Substances Query is used to identify the substances associated with a material that are impacted
# by one or more defined legislations.

# This example shows how to perform an Impacted Substance query on material records, and how to process the results.

# ## Connecting to Granta MI

# Import the ``Connection`` class and create the connection. See the [Getting Started](../0_Getting_started.ipynb)
# example for more detail.

# + tags=[]
from ansys.grantami.bomanalytics import Connection

server_url = "http://my_grantami_server/mi_servicelayer"
cxn = Connection(server_url).with_credentials("user_name", "password").connect()
# -

# ## Building and running the query

# The query is assembled by providing lists of material references and legislations of interest. The query will return
# the substances that are present in the specified materials and are impacted by the specified legislations.

# First specify some constants that contain the material and legislation references we will use.

# + tags=[]
PPS_ID = "plastic-pps-generalpurpose"
PC_ID = "plastic-pc-20carbonfiber"
SIN_LIST = "The SIN List 2.1 (Substitute It Now!)"
REACH = "REACH - The Candidate List"
# -

# Next import the ``queries`` module and build the query with the references in the previous cell.

# + tags=[]
from ansys.grantami.bomanalytics import queries

mat_query = (
    queries.MaterialImpactedSubstancesQuery()
    .with_material_ids([PPS_ID, PC_ID])
    .with_legislations([REACH, SIN_LIST])
)
# -

# Finally, run the query. Passing a ``MaterialImpactedSubstancesQuery`` object to the ``Connection.run()`` method
# returns a ``MaterialImpactedSubstancesQueryResult`` object.

# + tags=[]
results = cxn.run(mat_query)
results
# -

# A ``MaterialImpactedSubstancesQueryResult`` object contains three properties:
# ``impacted_substances_by_material``, ``impacted_substances_by_legislation``, and ``impacted_substances``. They provide
# different views of the impacted substances at different levels of granularity.

# ## View results grouped by material

# This property is structured first as a list of ``materialWithImpactedSubstancesResult`` objects, each of which
# contains a dictionary of lists of ``ImpactedSubstance`` objects keyed by legislation or a single flat list of all
# substances.

# First, we can simplify the structure somewhat because we are only using Material IDs. The cell below creates a
# dictionary that maps Material IDs to lists of substances impacted by the 'SIN List'.

# + tags=[]
substances_by_material = {}
for material in results.impacted_substances_by_material:
    substances = material.substances_by_legislation[SIN_LIST]
    substances_by_material[material.material_id] = substances
# -

# Then use the ``tabulate`` package to print a table of the substances and their quantities for the polycarbonate
# material only.

# + tags=[]
from tabulate import tabulate

rows = [(substance.cas_number, substance.max_percentage_amount_in_material)
    for substance in substances_by_material[PC_ID]]

print(f'Substances impacted by "{SIN_LIST}" in "{PC_ID}" (10/{len(rows)})')
print(tabulate(rows[:10], headers=["CAS Number", "Amount (wt. %)"]))
# -

# ## View results grouped by legislation

# This property merges the results across all materials, resulting in a single dictionary of legislations that contain
# all impacted substances for all materials.

# Again we use the ``tabulate`` package to print a table of substances, but this time we are including the substances in
# all materials, but again limited to the SIN List only.

# + tags=[]
material_substances_sin = results.impacted_substances_by_legislation[SIN_LIST]
rows = [(substance.cas_number, substance.max_percentage_amount_in_material)
    for substance in material_substances_sin]
print(f'Substances impacted by "{SIN_LIST}" in all materials (10/{len(rows)})')
print(tabulate(rows[:10], headers=["CAS Number", "Amount (wt. %)"]))
# -

# ## View results as a flat list

# This property reduces the granularity further to produce a single flattened list of substances across all legislations
# for all materials.

# The cell below uses the ``tabulate`` package to print a table of substances. Because we are using the
# ``impacted_substances`` property, we only have one list of ``ImpactedSubstance`` objects which covers both
# legislations and both materials.

# + tags=[]
material_substances_all = results.impacted_substances
rows = [(substance.cas_number, substance.max_percentage_amount_in_material)
    for substance in material_substances_all]
print(f"Impacted substances for all materials and legislations (10/{len(rows)})")
print(tabulate(rows[:10], headers=["CAS Number", "Amount (wt. %)"]))
# -
