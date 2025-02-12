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

# Next, create a sustainability query. The query accepts a single BoM as argument and an optional
# configuration for units. If a unit is not specified, the default unit is used. Default units for the
# analysis are ``MJ`` for energy, ``kg`` for mass, and ``km`` for distance.

# +
xml_file_path = "supporting-files/bom-2412-assembly.xml"
with open(xml_file_path) as f:
    bom = f.read()

from ansys.grantami.bomanalytics import queries

query = queries.BomSustainabilityQuery().with_bom(bom)
# -

# Finally, run the query. The ``BomSustainabilityQueryResult`` object that is returned contains the
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
# In addition to the described properties, these objects  contain at least the following
# properties that define the results of the sustainability analysis:
#
# * ``.embodied_energy``
# * ``.climate_change``
#
# Additional properties are also available for each ``<ItemType>WithSustainabilityResult`` object.
# For more information, see the
# [Sustainability API](https://bomanalytics.grantami.docs.pyansys.com/version/stable/api/sustainability/index.html).

# ### The ``BomSustainabilityQueryResult.parts`` property
#
# The ``BomSustainabilityQueryResult.parts`` property contains the single *root* part in the input
# BoM. This part in turn also has a ``.parts`` property, which contains the list of
# ``PartWithSustainabilityResult`` objects that are children of the root part. This structure
# continues recursively to define all parts in the input BoM. These parts can be of two types:
# assemblies or leaf parts.
#
# #### **Assemblies**
#
# Assemblies are ``PartWithSustainabilityResult`` objects that contain subparts. Assemblies do not
# contain materials directly.
#
# Assemblies include the following properties that describe child BoM items:
#
# - ``.parts``: Subparts of the assembly, which are defined as ``PartWithSustainabilityResult`` objects.
# - ``.processes``: Joining and finishing processes applied to the assembly, which are defined as
# ``ProcessWithSustainabilityResult`` objects.
#
# The environmental impact of an assembly includes the sum of the environmental impacts of all
# subparts and processes applied to the assembly.
#
# #### **Leaf parts**
#
# Leaf parts are ``PartWithSustainabilityResult`` objects that do not include subparts. Leaf parts
# can contain the materials they are made of as direct children.
#
# Leaf parts include the following properties:
#
# - ``.materials``: Materials that the part is made of, which are defined as a list
# ``MaterialWithSustainabilityResult`` objects.
# - ``.processes``: Joining and finishing processes applied to the part, which are defined as a list of
# ``ProcessWithSustainabilityResult`` objects.
#
# The environmental impact of a leaf part includes the sum of the environmental impacts
# associated with the quantity of materials used in the part, processes
# applied to the part directly, and processes applied to materials in the part.

# #### **Materials**
#
# Materials are ``MaterialWithSustainabilityResult`` objects. They include the ``.processes`` property.
# This property consists of the primary and secondary processes applied to the mass of material, which
# are defined as a list of ``ProcessWithSustainabilityResult`` objects.
#
# The environmental impact of a material is calculated from database data and the mass of material used.
# Even though processes appear as children of materials in the hierarchy, their environmental impact is
# not summed up in the parent material's impact, as opposed to the environmental impact of parts.

# #### **Processes**
#
# Processes are represented by ``ProcessWithSustainabilityResult`` objects. Processes are child items
# in the BoM and have no children themselves. The environmental impact of a process is calculated
# from database data and masses defined in the BoM.

# ### The `BomSustainabilityQueryResult.transport` property
#
# The ``BomSustainabilityQueryResult.transport`` property contains the transport stages in the input
# BoM, which are defined as a list of ``TransportWithSustainabilityResult`` objects. Transport stages contain no
# BoM properties. The environmental impact of a transport stage is just the environmental
# impact associated with the transport stage itself.

# ## Process the ``BomSustainabilityQueryResult`` object
#
# To visualize the results using [plotly](https://plotly.com/python/), the results are
# loaded into a [pandas](https://pandas.pydata.org/) ``DataFrame`` object.
#
# The following cell defines functions that convert the BoM hierarchical structure into a flat list
# of items. Each function also converts each item into a dictionary of common values that the
# ``DataFrame`` object can interpret.
#
# Each row in the ``DataFrame`` object contains an ``id`` that uniquely identifies the item and a ``parent_id``
# that defines the parent item. The ``.identity`` property is used as an identifier because it is unique
# across all BoM items. This property is populated even if not initially populated on the BoM items.

# +
def traverse_bom(query_response):
    # Identify top-level assembly, which includes transport stages contributions.
    top_level_assembly = query_response.part
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
        record.update({"type": "Transport", "name": item.name})
    elif isinstance(item, MaterialWithSustainabilityResult):
        record.update({"type": "Material", "name": item.name})
    elif isinstance(item, ProcessWithSustainabilityResult):
        record.update({"type": "Process", "name": item.name})
    return record


# -

# Now call the ``traverse_bom`` function and print the first two dictionaries, which represent the root
# part and the first assembly in the BoM.

records = list(traverse_bom(result))
records[:2]

# Now, use the list of dictionaries to create a pandas ``DataFrame`` object. Use the ``DataFrame.head()`` method
# to display the first five rows of the ``DataFrame`` object.

import pandas as pd
df = pd.DataFrame.from_records(records)
df.head()

# Finally, visualize the data in a ``sunburst`` hierarchical chart:
#
# * The segments are represented hierarchically. The BoM is at the center, and items further down
# the hierarchy are further out in the plot.
# * Item type is represented by color.
# * The size of the segment represents the environmental impact of that item.

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
