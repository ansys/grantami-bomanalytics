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

# + [markdown] tags=[]
# # Perform a part impacted substances query
# -

# A part impacted substances query is used to determine the substances associated with a part that are impacted by one
# or more defined legislations. The part record can represent either a single component, a subassembly, or a finished
# product. Thus, the substances can be associated with either the part record itself or any other record that
# the part directly or indirectly references.

# This example shows how to perform an Impacted Substance query on part records and how to process the results.

# ## Connect to Granta MI

# Import the ``Connection`` class and create the connection. For more information, see the
# [Basic Usage](../0_Basic_usage.ipynb) example.

# + tags=[]
from ansys.grantami.bomanalytics import Connection

server_url = "http://my_grantami_server/mi_servicelayer"
cxn = Connection(server_url).with_credentials("user_name", "password").connect()
# -

# + [markdown] tags=[]
# ## Build and run the query
# -

# The query is assembled by providing lists of part references and legislations of interest. The query returns
# the substances that are present in the specified parts and are impacted by the specified legislations.
#
# In this example, the ``DRILL`` part is used. In contrast to the Material version of this query shown in
# a previous example, this part does not reference any substances directly. Instead, it references
# subcomponents, which in turn reference materials, which then reference substances. The Part Impacted Substances
# Query flattens all these layers of complexity and aggregates them together into a single list.

# First specify some constants that contain the part and legislation references to use.

# + tags=[]
DRILL = "DRILL"
WING = "asm_flap_mating"
SIN_LIST = "SINList"
REACH = "Candidate_AnnexXV"
# -

# Next, import the ``queries`` module and build the query with the references in the previous cell.

# + tags=[]
from ansys.grantami.bomanalytics import queries

part_query = (
    queries.PartImpactedSubstancesQuery()
    .with_part_numbers([DRILL, WING])
    .with_legislation_ids([SIN_LIST, REACH])
)
# -

# Finally, run the query. Passing a ``PartImpactedSubstancesQuery`` object to the ``Connection.run()`` method returns a
# ``PartImpactedSubstancesQueryResult`` object.

# + tags=[]
part_result = cxn.run(part_query)
part_result
# -

# A ``PartImpactedSubstancesQueryResult`` object contains three properties:
# ``impacted_substances_by_part``, ``impacted_substances_by_legislation``, and ``impacted_substances``. They provide
# different views of the impacted substances at different levels of granularity.

# ## Group results by part

# This property is structured first as a list of ``PartWithImpactedSubstancesResult`` objects, each of which contains
# a dictionary of lists of ``ImpactedSubstance`` objects keyed by legislation or a single flat list of all
# substances.

# You can simplify the structure because you are only using part numbers. First, create a
# dictionary that maps part numbers to lists of substances impacted by the ``SIN_LIST``.

# + tags=[]
substances_by_part = {}
for part in part_result.impacted_substances_by_part:
    part_substances = part.substances_by_legislation[SIN_LIST]
    substances_by_part[part.part_number] = part_substances
# -

# Then use the ``tabulate`` package to print a table of the substances and their quantities for the wing assembly only.

# + tags=[]
from tabulate import tabulate

rows = [(substance.cas_number, substance.max_percentage_amount_in_material)
        for substance in substances_by_part[WING]]

print(f'Substances impacted by "{SIN_LIST}" in "{WING}"')
print(tabulate(rows, headers=["CAS Number", "Amount (wt. %)"]))
# -

# ## Group results by legislation

# This property merges the results across all parts, returning a single dictionary of legislations that contain
# all impacted substances for all parts.

# As before, use the ``tabulate`` package to print a table of substances. This time include substances in
# all parts, but only those on the ``SIN_LIST``.

# + tags=[]
part_substances_sin = part_result.impacted_substances_by_legislation[SIN_LIST]
rows = [(substance.cas_number, substance.max_percentage_amount_in_material)
        for substance in part_substances_sin]
print(f'Substances impacted by "{SIN_LIST}" in all parts (5/{len(rows)})')
print(tabulate(rows[:5], headers=["CAS Number", "Amount (wt. %)"]))
# -

# ## Generate results as a flat list

# This property reduces the granularity further, producing a single flattened list of substances across all legislations
# and for all parts.

# Use the ``tabulate`` package to print a third table of substances. Because you are using the
# ``impacted_substances`` property, you only have one list of ``ImpactedSubstance`` objects, which covers both
# legislations and both the parts specified above.

# + tags=[]
part_substances_all = part_result.impacted_substances
rows = [(substance.cas_number, substance.max_percentage_amount_in_material)
        for substance in part_substances_all]
print(f'Impacted substances across all legislations in "DRILL" (5/{len(rows)})')
print(tabulate(rows[:5], headers=["CAS Number", "Amount (wt. %)"]))
# -
