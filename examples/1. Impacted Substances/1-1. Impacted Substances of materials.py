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

# # Performing an Impacted Substances Query

# There are two types of query that can be run; Impacted Substances queries and Compliance queries. Both types of
# queries involve resolving the substances associated with some item, but whereas the Impacted Substances query just
# returns the substances in a flat list, the Compliance query compares those substances with a set of Indicators
# (themselves based on legislations) and determines compliance.

# This example shows how to perform an Impacted Substance query and how to interpret the results.

# ## Connecting to Granta MI

# First set the log level to INFO, so we can see some key facts about the connection process.

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Then import the bom analytics module and create the connection

from ansys.grantami.bomanalytics import Connection

cxn = Connection('http://localhost/mi_servicelayer').with_autologon().build()

# ## MaterialImpactedSubstancesQuery

# This is the simplest type of query, and in Granta MI terms simply resolves the 'Substances in this Material' tabular
# link to return a list of substances in the material.

# The query is assembled by providing a list of material references and legislations of interest. The query will return
# the intersections of substances that are both in the specified materials and affected by the specified legislations.

PPS_ID = 'plastic-pps-generalpurpose'
PC_ID = 'plastic-pc-20carbonfiber'
SIN_LIST = 'The SIN List 2.1 (Substitute It Now!)'
REACH = 'REACH - The Candidate List'

from ansys.grantami.bomanalytics import queries
mat_query = queries.MaterialImpactedSubstancesQuery()
mat_query = mat_query.with_material_ids([PPS_ID, PC_ID]).with_legislations([REACH, SIN_LIST])

results = cxn.run(mat_query)
results

# An Impacted Substances query result object contains three properties:
# `impacted_substances_by_material_and_legislation`, `impacted_substances_by_legislation`, and `impacted_substances`.
# They provide different views of the impacted substances, but for a query with a single material and single
# legislation, they essentially provide the same results:

# ### impacted_substances_by_material_and_legislation

# This property is structured first as a list of `materialWithImpactedSubstancesResult` objects, each of which contains
# a dictionary of `LegislataionResult` objects, keyed by the legislation name. The `LegislationResult` object then
# contains a list of `ImpactedSubstance` objects, which represent the actual substances impacted by the legislation.

# First index the `impacted_substances_by_material_and_legislation` list by material ID, since that's what we've used
# to reference our materials.

substances_by_material = {}
for material in results.impacted_substances_by_material_and_legislation:
    substances_by_material[material.material_id] = material.legislations[SIN_LIST].substances

# Then use the `tabulate` package to print a table of the substances and their quantities in the material.

from tabulate import tabulate
rows = [[substance.cas_number, substance.max_percentage_amount_in_material]
        for substance in substances_by_material[PC_ID]]
print(f'Substances impacted by "{SIN_LIST}" in "{PC_ID}" (first 10 only, {len(rows)} total)')
print(tabulate(rows[:10], headers=['CAS Number', 'Amount (wt. %)']))

# ### impacted_substances_by_legislation

# This property merges the results across all materials, resulting in a single dictionary of legislations that contain
# all impacted substances for all materials.

substances = results.impacted_substances_by_legislation[SIN_LIST]
rows = [[substance.cas_number, substance.max_percentage_amount_in_material] for substance in substances]
print(f'Substances impacted by "{SIN_LIST}" in all materials (first 10 only, {len(rows)} total)')
print(tabulate(rows[:10], headers=['CAS Number', 'Amount (wt. %)']))

# ### impacted_substances

# This property reduces the granularity further to produce a single flattened list of materials across all legislations.
# This is the simplest response.

substances = results.impacted_substances
rows = [[substance.cas_number, substance.max_percentage_amount_in_material] for substance in substances]
print(f"Impacted substances across all materials and legislations (first 10 only, {len(rows)} total)")
print(tabulate(rows[:10], headers=['CAS Number', 'Amount (wt. %)']))
