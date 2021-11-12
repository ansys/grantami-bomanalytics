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

# ## PartImpactedSubstancesQuery

# A similar query can be performed on Parts, Specifications, and on an XML Bill of Materials. All work in essentially
# the same way, where instead of only looking at direct links to materials, the API will resolve links to substances
# through all possible linking paths. This union of substances will be returned in the same way as for Materials.
#
# Some potential paths from a part to a substance are listed below:
#
# * Part -> substance
# * Part -> material -> substance
# * Part -> part -> material -> substance
# * Part -> part -> specification -> specification -> coating -> substance
#
# In this example, the 'Drill' component will be used, which contains some of these paths described above. The query
# resolves all links to all substances and aggregates them together into a single list.

SIN_LIST = 'The SIN List 2.1 (Substitute It Now!)'
REACH = 'REACH - The Candidate List'

from ansys.grantami.bomanalytics import queries
part_query = queries.PartImpactedSubstancesQuery().with_part_numbers(['DRILL']).with_legislations([SIN_LIST, REACH])
part_result = cxn.run(part_query)

# First print the results just for the REACH legislation (we have only specified one part, so we can use the
# `impacted_substances_by_legislation` property.

from tabulate import tabulate
part_substances_reach = part_result.impacted_substances_by_legislation[REACH]
rows = [[substance.cas_number, substance.max_percentage_amount_in_material] for substance in part_substances_reach]
print(f'Substances impacted by "{REACH}" in "DRILL" (first 10 only, {len(rows)} total)')
print(tabulate(rows[:10], headers=['CAS Number', 'Amount (wt. %)']))

# Finally, print the results for all legislations

part_substances_all = part_result.impacted_substances
rows = [[substance.cas_number, substance.max_percentage_amount_in_material] for substance in part_substances_all]
print(f'Impacted substances across all legislations in "DRILL" (first 10 only, {len(rows)} total)')
print(tabulate(rows[:10], headers=['CAS Number', 'Amount (wt. %)']))
