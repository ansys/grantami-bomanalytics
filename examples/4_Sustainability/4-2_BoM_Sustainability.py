# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.15.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# # Perform a BoM sustainability query
#
# The following supporting files are required for this example:
#
# * [bom-2301-assembly.xml](supporting-files/bom-2301-assembly.xml)

# ## Run a BoM sustainability query
#
# First, connect to Granta MI.

# +
from ansys.grantami.bomanalytics import Connection

server_url = "http://my_grantami_server/mi_servicelayer"
cxn = Connection(server_url).with_credentials("user_name", "password").connect()
# -

# Next, create a sustainability query. The query accepts a single BoM as argument, as well as optional
# configuration for units. If a unit is not specified, the default unit is used. Default units for the analysis are:
# `MJ` for energy, `kg` for mass, and `km` for distance.

# +
xml_file_path = "supporting-files/bom-2301-assembly.xml"
with open(xml_file_path) as f:
    bom = f.read()

from ansys.grantami.bomanalytics import queries

query = queries.BomSustainabilityQuery().with_bom(bom)
result = cxn.run(query)

result
# -

# ## Sustainability query result
#
# ### Definition
#
# The structure of a BoM sustainabability query result is similar to the input BoM structure.
#
# #### Query result
#
# The ``BomSustainabilityQueryResult`` class defines two properties:
#
# - ``parts``: list of top-level parts of the BoM and their calculated environmental footprint.
# - ``transport_stages``: list of transport stages defined in the BoM and their calculated environmental footprint.
#
# #### Parts
#
# Parts can be of two types: assemblies, or leaf parts.
#
# ##### **Assemblies**
#
# Assemblies are parts that define sub-parts. They do not define materials.
#
# Assemblies include:
#
# - ``parts``: list of sub-parts in the assembly.
# - ``processes``: list of joining and finishing processes applied to the assembly.
#
# The environmental footprint of an assembly describes the sum of all sub-parts and processes applied to the assembly.
#
# ##### **Leaf parts**
#
# Leaf parts are parts which do not include sub-parts. They can define the material they are made of.
#
# Leaf parts can include:
#
# - ``materials``: list of materials that the part is made of.
# - ``processes``: list of joining and finishing processes applied to the part.
#
# The environmental footprint of a leaf part includes the environmental footprint associated with the quantity of
# materials used (see below for details) and processes applied to the part.
#
# #### Materials
#
# Materials can include:
#
# - ``processes``: list of primary and secondary processes applied to the mass of material.
#
# The environmental footprint of a material includes the environmental footprint associated with the mass of material
# used and the environmental footprint of all primary and secondary processes applied.
#
# #### Processes
#
# Processes have no children.
#
# ### Processing
#
# In order to visualize the results using [plotly](https://plotly.com/python/), the results will be loaded into a
# [pandas](https://pandas.pydata.org/) ``DataFrame``.
#
# Methods defined in the following cell help convert the BoM hierarchical structure into a flat list of items, as well
# as converting each item into a dictionary of common values that the ``DataFrame`` will be able to interpret.
# Importantly, each value in the resulting list includes its ``id`` and ``parent_id``, which are critical to preserve a
# sense of hierarchy. The ``identity`` property is used as an identifier as it is unique across all BoM items, and
# populated even if not initially populated on the BoM items.

# +
def traverse_bom(query_response):
    # Identify top-level assembly, which includes transport stages contributions.
    top_level_assembly = query_response.parts[0]
    top_level_assembly_id = top_level_assembly.identity
    yield to_dict(top_level_assembly, "")
    for part in top_level_assembly.parts:
        yield from traverse_part(part, top_level_assembly_id)
    for transport in query_response.transport_stages:
        yield to_dict(transport, top_level_assembly_id)

def traverse_part(part, parent_id):
    yield to_dict(part, parent_id)
    part_id = part.identity
    for child_part in part.parts:
        yield from traverse_part(child_part, part_id)
    for child_material in part.materials:
        yield from traverse_material(child_material, part_id)
    for child_process in part.processes:
        yield to_dict(child_process, part_id)

def traverse_material(material, parent_id):
    yield to_dict(material, parent_id)
    for child_process in material.processes:
        yield to_dict(child_process, parent_id)

from ansys.grantami.bomanalytics._item_results import (
    PartWithSustainabilityResult,
    TransportWithSustainabilityResult,
    MaterialWithSustainabilityResult,
    ProcessWithSustainabilityResult,
)

def to_dict(item, parent):
    record = {
        "id": item.identity,
        "parent_id": parent,
        "embodied energy [MJ]": item.embodied_energy.value,
        "climate change [kg CO2-eq]": item.climate_change.value,
    }
    if isinstance(item, PartWithSustainabilityResult):
        record.update({"type": "Part", "name": item.input_part_number})
    elif isinstance(item, TransportWithSustainabilityResult):
        record.update({"type": "Transport", "name": item.identity})
    elif isinstance(item, MaterialWithSustainabilityResult):
        record.update({"type": "Material", "name": item.name})
    elif isinstance(item, ProcessWithSustainabilityResult):
        record.update({"type": "Process", "name": item.name})
    return record

records = list(traverse_bom(result))
# -

import pandas as pd
df = pd.DataFrame.from_records(
    records,
    columns=["type", "parent_id", "id", "name", "embodied energy [MJ]", "climate change [kg CO2-eq]"],
)
df

# Finally, visualize the data in a ``sunburst`` hierarchical chart. Colors represent the type of items. Size of
# sections represent the environmental footprint on an item.
# A similar visualization can be performed to represent the climate change property of each item.

# +
import plotly.express as px

fig = px.sunburst(
    df,
    names=df["name"],
    ids=df["id"],
    parents=df["parent_id"],
    values=df["embodied energy [MJ]"],
    branchvalues="total",
    color=df["type"],
    title="Embodied energy [MJ] breakdown",
)
# Disable sorting, so that items appear in the same order as in the BoM.
fig.update_traces(sort=False)
fig.show()