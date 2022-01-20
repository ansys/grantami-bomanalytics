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

# # [TECHDOCS]Determining Compliance for BoMs in External Data Sources

# ## Introduction

# It is common to deal with Bills of Materials or other data structures stored in a third party system. This
# example shows a scenario where compliance needs to be determined for a BoM-type structure in a JSON file,
# with the result added to the input file.

# Whilst it is possible that data would be available in a JSON file, the intention is that the approach presented
# here would be applicable for data in other formats, or data loaded from other software platform APIs.

# The external data source used in this example can be downloaded
# [here](supporting-files/source_data.json).

# ## Load the External Data

# First load the JSON file and use the `json` module
# to convert the text into a hierarchical structure of `dict` and `list` objects.

# + tags=[]
import json
from pprint import pprint

with open("supporting-files/source_data.json") as f:
    data = json.load(f)
pprint(data)
# -

# The list of components will be used frequently, so we can store this in a variable for convenience.

# + tags=[]
components = data["components"]
# -

# It is clear from viewing this data that some parts include multiple materials, and some materials appear in the JSON
# file more than once. However, the material compliance is not dependent on the component it is used in, and the
# compliance of a part only depends on the worst compliance status of the constituent materials. Therefore we can
# simplify the compliance query by get the compliance for the unique set of materials in the JSON file, and perform some
# data manipulation of the results.

# We can use a set comprehension to get the unique materials, which we can then cast into a list.

# + tags=[]
material_ids = {m for comp in components for m in comp["materials"]}
material_ids
# -

# ## Getting the Compliance Status

# Now we can feed the list of material IDs into a compliance query as shown in previous exercises.

# + tags=[]
from ansys.grantami.bomanalytics import Connection, indicators, queries

server_url = "http://my_grantami_service/mi_servicelayer"
cxn = Connection(server_url).with_credentials("user_name", "password").connect()
svhc = indicators.WatchListIndicator(
    name="SVHC",
    legislation_names=["REACH - The Candidate List"],
    default_threshold_percentage=0.1,
)
mat_query = (
    queries.MaterialComplianceQuery()
    .with_indicators([svhc])
    .with_material_ids(material_ids)
)
mat_results = cxn.run(mat_query)
mat_results
# -

# ## Post-Processing the Results

# The results above describe the compliance status for each material, but some further work needs to be performed to
# provide the compliance status for all the components in the original JSON.

# In the case where a component contains only one material, the result can simply be copied over.
# In the general case, moving from material compliance to component compliance just means taking
# the worst compliance across all the constituent materials.

# To do this, we first create a dictionary that maps a material ID to the indicator result returned by the query.

# + tags=[]
material_lookup = {mat.material_id: mat.indicators["SVHC"]
                   for mat in mat_results.compliance_by_material_and_indicator}
# -

# Next define a function that takes a list of material IDs and returns the worst compliance status for all of them.
# We can use the built-in `max()` function to do this, since `WatchListIndicator` objects can be compared with > and <
# operators. The convention is that a worse result is 'greater than' a better result.


# + tags=[]
def rollup_results(material_ids) -> str:
    indicator_results = [material_lookup[mat_id] for mat_id in material_ids]
    worst_result = max(indicator_results)
    return worst_result.flag.name


# -

# Now call this function for each component in a `dict` comprehension, giving us a mapping between part number
# and compliance status.

# + tags=[]
component_results = {comp["part_number"]: rollup_results(comp["materials"])
                     for comp in components}
component_results
# -

# These results include the text as defined by the API. However, let's say in this example we are using the compliance
# status to determine the approvals required to release the part in a design review process. As a result, we can define
# a mapping between compliance statuses and approval requirements.

# + tags=[]
flags = indicators.WatchListFlag
result_map = {
    flags.WatchListCompliant.name: "No Approval Required",
    flags.WatchListAllSubstancesBelowThreshold.name: "Level 1 Approval Required",
    flags.WatchListHasSubstanceAboveThreshold.name: "Level 2 Approval Required",
}
# -

# We can now use this dictionary to map from the Granta MI result to the approval requirements.

# + tags=[]
results = {part_number: result_map[result]
           for part_number, result in component_results.items()}
results
# -

# ## Write the Output

# For the final result, we can take our result `dict` and use it to extend the original JSON data structure with
# the approval requirements added in.

# +
components_with_result = []
for component in components:
    component_with_result = component
    part_number = component["part_number"]
    component_with_result["approval"] = results[part_number]
    components_with_result.append(component_with_result)

data_results = {}
data_results["components"] = components_with_result
# -

# Finally, printing the results shows the new data structure with the results included.

# + tags=[]
pprint(data_results)
# -

# ## Summary

# This example has aimed to show how a BoM-like data structure can be loaded from a neutral format and used as a
# starting point for compliance analysis. Whilst it is unlikely that the data structures and processing presented here
# will be an exact match for your requirements, it should at least demonstrate the principle for how to plug the BoM
# Analytics API into your processes.
