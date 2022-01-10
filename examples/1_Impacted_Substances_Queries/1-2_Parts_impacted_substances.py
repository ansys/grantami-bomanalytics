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
# # [TECHDOCS]Performing a Part Impacted Substances Query
# -

# A Part Impacted Substances Query is used to extract the substances associated with a part that are impacted by one or
# more defined legislations. The part record can represent either a single component, a sub-assembly, or a finished
# product, and therefore the substances can be associated with either the part record itself, or any other record that
# the part directly or indirectly references.

# This example shows how to perform an Impacted Substance query on part records, and how to process the results.

# ## Connecting to Granta MI

# Import the `Connection` class and create the connection. See the Getting Started example for more detail.

# + tags=[]
from ansys.grantami.bomanalytics import Connection

server_url = "http://my_grantami_service/mi_servicelayer"
cxn = Connection(server_url).with_credentials("user_name", "password").connect()
# -

# + [markdown] tags=[]
# ## Building and Running the Query
# -

# The query is assembled by providing a list of part references and legislations of interest. The query will return
# the substances that are present in the specified parts and are impacted by the specified legislations.
#
# In this example, the 'Drill' part will be used. In contrast to the Material version of this query shown in
# a previous example, the Drill part does not reference any substances directly. Instead, it references
# sub-components, which in turn reference materials, which then reference substances. The Part Impacted Substances
# Query flattens all these layers of complexity and aggregates them together into a single list.

# First specify some constants that contain the part and legislation references we will use.

# + tags=[]
DRILL = "DRILL"
WING = "asm_flap_mating"
SIN_LIST = "The SIN List 2.1 (Substitute It Now!)"
REACH = "REACH - The Candidate List"
# -

# Next import the queries module and build the query with the references in the previous cell.

# + tags=[]
from ansys.grantami.bomanalytics import queries

part_query = (
    queries.PartImpactedSubstancesQuery()
    .with_part_numbers([DRILL, WING])
    .with_legislations([SIN_LIST, REACH])
)
# -

# Finally, run the query. Passing a `PartImpactedSubstancesQuery` object to the `Connection.run()` method returns a
# `PartImpactedSubstancesQueryResult` object.

# + tags=[]
part_result = cxn.run(part_query)
part_result
# -

# A `PartImpactedSubstancesQueryResult` object contains three properties:
# `impacted_substances_by_part`, `impacted_substances_by_legislation`, and `impacted_substances`. They provide different
# views of the impacted substances at different levels of granularity.

# ## impacted_substances_by_part

# This property is structured first as a list of `partWithImpactedSubstancesResult` objects, each of which contains
# a dictionary of lists of `ImpactedSubstance` objects keyed by legislation, or a single flat list of all
# substances.

# First, we can simplify the structure somewhat because we are only using only Part Numbers. The cell below creates a
# dictionary that maps Part Numbers to lists of substances impacted by the 'SIN List'.

# + tags=[]
substances_by_part = {}
for part in part_result.impacted_substances_by_part:
    part_substances = part.substances_by_legislation[SIN_LIST]
    substances_by_part[part.part_number] = part_substances
# -

# Then use the `tabulate` package to print a table of the substances and their quantities for the Wing assembly only.

# + tags=[]
from tabulate import tabulate

rows = [(substance.cas_number, substance.max_percentage_amount_in_material)
        for substance in substances_by_part[WING]]

print(f'Substances impacted by "{SIN_LIST}" in "{WING}"')
print(tabulate(rows, headers=["CAS Number", "Amount (wt. %)"]))
# -

# ## impacted_substances_by_legislation

# This property merges the results across all parts, resulting in a single dictionary of legislations that contain
# all impacted substances for all parts.

# Again we use the `tabulate` package to print a table of substances, but this time we are including the substances in
# all parts, but again limited to the SIN List only.

# + tags=[]
part_substances_sin = part_result.impacted_substances_by_legislation[SIN_LIST]
rows = [(substance.cas_number, substance.max_percentage_amount_in_material)
        for substance in part_substances_sin]
print(f'Substances impacted by "{SIN_LIST}" in all parts (10/{len(rows)})')
print(tabulate(rows[:10], headers=["CAS Number", "Amount (wt. %)"]))
# -

# ## impacted_substances

# This property reduces the granularity further to produce a single flattened list of substances across all legislations
# for all parts.

# The cell below uses the `tabulate` package to print a table of substances. Because we are using the
# `impacted_substances` property, we only have one list of `ImpactedSubstance` objects which covers both legislations
# and both parts.

# + tags=[]
part_substances_all = part_result.impacted_substances
rows = [(substance.cas_number, substance.max_percentage_amount_in_material)
        for substance in part_substances_all]
print(f'Impacted substances across all legislations in "DRILL" (10/{len(rows)})')
print(tabulate(rows[:10], headers=["CAS Number", "Amount (wt. %)"]))
