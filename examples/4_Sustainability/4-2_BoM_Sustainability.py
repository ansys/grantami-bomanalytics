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
# configuration for units. If a unit is not specified, the default unit is used. Default units for the
# analysis are:
# `MJ` for energy, `kg` for mass, and `km` for distance.

# +
xml_file_path = "supporting-files/bom-2301-assembly.xml"
with open(xml_file_path) as f:
    bom = f.read()

from ansys.grantami.bomanalytics import queries

query = queries.BomSustainabilityQuery().with_bom(bom)
# -

# Finally, run the query. A `BomSustainabilityQueryResult` object is returned, which contains the
# results of the analysis.

# +
result = cxn.run(query)

result
# -

# ## The ``BomSustainabilityQueryResult`` class
#
# ### Definition
#
# The structure of a BoM sustainabability query result mirrors the input BoM structure. However, each
# item in the result objects also includes the results of the sustainability analysis for that item.
# In addition to the properties described below, these objects also contain at least the following
# properties which define the results of the sustainability analysis:
#
# * ``.embodied_energy``
# * ``.climate_change``
#
# Additional properties are also available for each ``<ItemType>WithSustainabilityResult`` object,
# see the <<TODO: link to sustainability API >> for more details.

# ### The ``BomSustainabilityQueryResult.parts`` property
#
# The ``BomSustainabilityQueryResult.parts`` property contains the single 'root' part in the input
# BoM. This part in turn also has a ``.parts`` property, which contains the list of
# ``PartWithSustainabilityResult`` objects which are children of the root part. This structure
# continues recursively to define all parts in the input BoM. These parts can be of two types:
# assemblies, or leaf parts.
#
# ##### **Assemblies**
#
# Assemblies are ``PartWithSustainabilityResult`` objects that contain sub-parts. Assemblies do not
# contain materials directly.
#
# Assemblies include the following properties which describe child BoM items:
#
# - ``.parts``: the sub-parts of the assembly, defined as ``PartWithSustainabilityResult`` objects.
# - ``.processes``: the joining and finishing processes applied to the assembly, defined as
# ``ProcessWithSustainabilityResult`` objects.
#
# The environmental footprint of an assembly includes the sum of the environmental footprints of all
# sub-parts and processes applied to the assembly.
#
# ##### **Leaf parts**
#
# Leaf parts are ``PartWithSustainabilityResult`` objects that do not include sub-parts. Leaf parts
# can contain the materials they are made of as direct children.
#
# Leaf parts include the following properties:
#
# - ``.materials``: the materials that the part is made of, defined as a list
# ``MaterialWithSustainabilityResult`` objects.
# - ``.processes``: the joining and finishing processes applied to the part, defined as a list of
# ``ProcessWithSustainabilityResult`` objects.
#
# The environmental footprint of a leaf part includes the sum of the environmental footprints
# associated with the quantity of materials used in the part (see below for details), processes
# applied to the part directly, and processes applied to materials in the part.

# #### Materials
#
# Materials are ``MaterialWithSustainabilityResult`` objects. They include the following properties:
#
# - ``.processes``: the primary and secondary processes applied to the mass of material, defined as a
# list of ``ProcessWithSustainabilityResult`` objects.
#
# The environmental footprint of a material includes the environmental footprint associated with the
# mass of material used.

# #### Processes
#
# Processes are represented by ``ProcessWithSustainabilityResult`` objects. Processes contain no BoM
# properties. The environmental footprint of a process is just the environmental footprint associated
# with the processes itself.

# ### The `BomSustainabilityQueryResult.transport` property
#
# The ``BomSustainabilityQueryResult.transport`` property contains the transport stages in the input
# BoM, defined as a list of ``TrasportWithSustainabilityResult`` objects. Transport stages contain no
# BoM properties. The environmental footprint of a traansport stage is just the environmental
# footprint associated with the transport stage itself.

# ## Process the ``BomSustainabilityQueryResult`` object
#
# In order to visualize the results using [plotly](https://plotly.com/python/), the results will be
# loaded into a [pandas](https://pandas.pydata.org/) ``DataFrame``.
#
# The following cell defines functions which convert the BoM hierarchical structure into a flat list
# of items. Each function also converts each item into a dictionary of common values that the
# ``DataFrame`` can interpret.
#
# Each row in the DataFrame contains an ``id`` which uniquely identifies the item, and a ``parent_id``
# which defines the parent item. The ``.identity`` property is used as an identifier as it is unique
# across all BoM items, and populated even if not initially populated on the BoM items.

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


# -

# Now call the ``traverse_bom`` function and print the first two dictionaries, representing the root
# part and the first assembly in the BoM.

records = list(traverse_bom(result))
records[:2]

# Now, use the list of dictionaries to create a DataFrame. Display the first five rows of the
# DataFrame with the ``DataFrame.head()`` method.

import pandas as pd
df = pd.DataFrame.from_records(records)
df.head()

# Finally, visualize the data in a ``sunburst`` hierarchical chart:
#
# * The segments are represented hierarchically. The BoM is at the center, and items further down
# the hierarchy are further out in the plot.
# * Item type is represented by color.
# * The size of the segment represents the environmental footprint of that item.

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
    width=800,
    height=800,
)
# Disable sorting, so that items appear in the same order as in the BoM.
fig.update_traces(sort=False)
fig.show()
