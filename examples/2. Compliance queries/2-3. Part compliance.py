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

# ## Connecting to Granta MI

# First set the log level to INFO, so we can see some key facts about the connection process.

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Then import the bom analytics module and create the connection

from ansys.grantami.bomanalytics import Connection

cxn = Connection('http://localhost/mi_servicelayer').with_autologon().build()

# ## Defining an Indicator

# In contrast to an ImpactedSubstances query, a Compliance query determines compliance against 'Indicators' as opposed
# to directly against legislations.
#
# There are two types of Indicator, which result in compliance being evaluated in similar but slightly different ways.
# In this example we will look at a Watch List indicator only, but the principles can be applied to a RoHS indicator.

from ansys.grantami.bomanalytics import indicators

svhc_indicator = indicators.WatchListIndicator(name="SVHC",
                                               legislation_names=["REACH - The Candidate List"],
                                               default_threshold_percentage=0.1)


# The cell above creates an Indicator against which compliance can be determined. The complete rules for compliance
# can be seen in the Restricted Substances documentation, but essentially if a substance appears in the queried item
# that is impacted by one of the legislations defined above, that item is non compliant.

# ## Part Compliance Query

# A part compliance query generally returns the largest and most complex data structure. Parts in Granta MI can
# reference one of the following child item types:
#
# - Parts
# - Specifications
# - Materials
# - Substances
#
# Since a part can contain another part, this can result in a bom of arbitrary complexity. Specifications can also
# reference other specifications, which is another route to complex BoMs.

from ansys.grantami.bomanalytics import queries
part_query = queries.PartComplianceQuery().with_part_numbers(['DRILL']).with_indicators([svhc_indicator])

part_result = cxn.run(part_query)

# Similar to a material compliance result, the part compliance result contains the compliance status for each part
# passed into the query. However, since a part can reference additional child items, the structure is more complex.

# First print the results for the DRILL record.

drill = part_result.compliance_by_part_and_indicator[0]
print(f"Drill compliance status: {drill.indicators['SVHC'].flag.name}")

# This tells us that the drill assembly contains an SVHC above the 0.1% threshold.

# We can print the parts below this part that also contain an SVHC above the threshold. The parts referenced by the
# 'drill' part are available in the `parts` property.

above_threshold_flag = svhc_indicator.available_flags.WatchListHasSubstanceAboveThreshold
parts_contain_svhcs = [part for part in drill.parts if part.indicators['SVHC'] >= above_threshold_flag]
print(f"{len(parts_contain_svhcs)} parts that contain SVHCs")
for part in parts_contain_svhcs:
    print(f"Part: {part.record_history_identity}")

# This process can be performed recursively to show a structure of each part that contains SVHCs either directly or
# indirectly. The cells below implement the code above in a function that can be called recursively, and then call it
# on the drill assembly.


def recursively_print_parts_with_svhcs(parts, depth=0):
    parts_contain_svhcs = [part for part in parts if part.indicators['SVHC'] >= above_threshold_flag]
    for part in parts_contain_svhcs:
        print(f"{'  '*depth}- Part: {part.record_history_identity}")
        recursively_print_parts_with_svhcs(part.parts, depth+1)


recursively_print_parts_with_svhcs(drill.parts)

# This can be extended further to include materials in the recursive iteration.


def recursively_print_parts_with_svhcs(parts, depth=0):
    parts_contain_svhcs = [part for part in parts if part.indicators['SVHC'] >= above_threshold_flag]
    for part in parts_contain_svhcs:
        print(f"{'  '*depth}- Part: {part.record_history_identity}")
        recursively_print_parts_with_svhcs(part.parts, depth+1)
        print_materials_with_svhcs(part.materials, depth+1)


def print_materials_with_svhcs(materials, depth=0):
    mats_contain_svhcs = [mat for mat in materials if mat.indicators['SVHC'] >= above_threshold_flag]
    for mat in mats_contain_svhcs:
        print(f"{'  '*depth}- Material: {mat.record_history_identity}")


recursively_print_parts_with_svhcs(drill.parts)
