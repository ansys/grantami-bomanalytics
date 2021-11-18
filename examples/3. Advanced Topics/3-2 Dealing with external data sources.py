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

# # Dealing with External Data Sources

# ## Introduction

# It is common to deal with Bills of Materials or other data structures stored in a third party system or format. This
# example shows an example of such a sitation applied to a simple JSON file structure, and produces a similar file
# as an output with compliance results added. This approach can be used to build an integration with third-party systems
# such as PLM or ERP systems.

# This example also uses materials from MaterialUniverse, but would work equally well using In House materials.

# ## Accessing the External Data

# Since this example is dealing with a JSON data structure, we can simply load it as a file and use the json library
# to convert the text into a hierarchical set of dicts and lists.

# + tags=[]
import json
from pprint import pprint
with open("../supporting-files/source_data.json") as f:
    data = json.load(f)
pprint(data)
# -

# The list of components will be used frequently, so store this in a variable for convenience.

# + tags=[]
components = data['components']
# -

# ## Getting the Compliance Status

# Some materials appear in the JSON file more than once. However, since the compliance of a material only depends on the
# material (and not the component it is used in), we only need to get the compliance for the material once. We can use
# a set to ensure we have only one copy of each material.

# + tags=[]
material_ids = {material for component in components for material in component['materials']}
material_ids = list(material_ids)
material_ids
# -

# Now we can feed the list of material IDs into a compliance query as shown in previous exercises.

# + tags=[]
from ansys.grantami.bomanalytics import Connection, queries, indicators
cxn = Connection("http://localhost/mi_servicelayer").with_autologon().build()
svhc = indicators.WatchListIndicator(name="SVHC",
                                     legislation_names=["REACH - The Candidate List"],
                                     default_threshold_percentage=0.1)
mat_query = queries.MaterialComplianceQuery().with_indicators([svhc]).with_material_ids(material_ids)
mat_results = cxn.run(mat_query)
mat_results
# -

# ## Post-Processing the Results

# We now have results from Granta MI that tell us the compliance status for each material, but this isn't precisely the
# question we are asking. We need to determine the compliance status for each component. In the case where a component
# contains only one material, the result can simply be copied over.

# However, in the case where a component contains multiple materials we need to perform some additional calculations.
# In these situations, the compliance of the component will be determined by the worst result for all materials in that
# component.

# To do this, we first create a dictionary that maps a material ID to the indicator result returned by the query.

material_lookup = {mat.material_id: mat.indicators['SVHC'] for mat in mat_results.compliance_by_material_and_indicator}

# Next define a function that takes a list of material IDs and returns the worst compliance status for all of them.
# We can use the built-in max() function to do this, since the WatchListIndicator functions can be compared with > and <
# operators, where a worse result is 'greater than' a better result.


def rollup_material_results(material_ids) -> indicators.WatchListFlag:
    indicator_results = [material_lookup[mat_id] for mat_id in material_ids]
    worst_result = max(indicator_results)
    return worst_result.flag.name


# Now call this function for the list of materials on each component.

component_results = [rollup_material_results(component['materials']) for component in components]
component_results

# These results include the text as defined by the API. However, let's say in this example we are using the compliance
# status to determine the approvals required to release the part in a design review process. As a result, we can define
# a mapping between compliance statuses and approval requirements.

result_map = {indicators.WatchListFlag.WatchListCompliant.name: "No Approval Required",
              indicators.WatchListFlag.WatchListAllSubstancesBelowThreshold.name: "Level 1 Approval Required",
              indicators.WatchListFlag.WatchListHasSubstanceAboveThreshold.name: "Level 2 Approval Required"}

# We can now use this dictionary to map from the Granta MI result to the approval requirements.

results = [result_map[res] for res in component_results]
results

# ## Final Steps

# To finish the example, we can create a new results dict and add both the results and the component information for
# each component.

new_components = []
for component, result in zip(components, results):
    new_component = {}
    new_component['compliance'] = result
    new_component.update(component)
    new_components.append(new_component)

data_results = {}
data_results['components'] = new_components

# Finally, printing the results shows the compliance result.

pprint(data_results)

# ## Summary

# This example has aimed to show how a BoM-like data structure can be loaded from a neutral format and used as a
# starting point for compliance analysis. Whilst it is unlikely that the data structures and processing presented here
# will be an exact match for your requirements, it should at least demonstrate the principle for how to plug the BoM
# Analytics API into your processes.
