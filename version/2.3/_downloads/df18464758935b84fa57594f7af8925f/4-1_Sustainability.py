# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.7
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# # Perform a sustainability query
#
# The following supporting files are required for this example:
#
# * [sustainability-bom-2412.xml](../supporting-files/sustainability-bom-2412.xml)
#
# For help on constructing an XML BoM, see [BoM examples](../6_BoMs/index.rst).

# <div class="alert alert-info">
#
# **Info:**
#
# This example uses an input file that is in the 24/12 XML BoM format. This structure requires Granta MI Restricted
# Substances and Sustainability Reports 2025 R2 or later.
#
# To run this example with an older version of the reports bundle, use
# [sustainability-bom-2301.xml](../supporting-files/sustainability-bom-2301.xml) instead. Some sections of this example
# will produce different results from the published example when this BoM is used.
# </div>

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
xml_file_path = "../supporting-files/sustainability-bom-2412.xml"
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
# - ``.parts``: Subparts of the assembly. Defined as ``PartWithSustainabilityResult`` objects.
# - ``.processes``: Joining and finishing processes applied to the assembly. Defined as
# ``ProcessWithSustainabilityResult`` objects.
# - ``.transport_stages``: Transportation of the assembly. Defined as a list of
# ``TransportWithSustainabilityResult`` objects.
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
# - ``.materials``: Materials that the part is made of. Defined as a list of
# ``MaterialWithSustainabilityResult`` objects.
# - ``.processes``: Joining and finishing processes applied to the part. Defined as a list of
# ``ProcessWithSustainabilityResult`` objects.
# - ``.transport_stages``: Transportation of the part. Defined as a list of
# ``TransportWithSustainabilityResult`` objects.
#
# The environmental impact of a leaf part includes the sum of the environmental impacts associated with
# the quantity of materials used in the part, processes applied to the part directly, and processes
# applied to materials in the part.

# #### **Materials**
#
# Materials are ``MaterialWithSustainabilityResult`` objects. They include the ``.processes`` property.
# This property consists of the primary and secondary processes applied to the mass of material, which
# are defined as a list of ``ProcessWithSustainabilityResult`` objects.
#
# The environmental impact of a material is calculated from database data and the mass of material used.
#
# Processes may appear as children of materials in the hierarchy, but the environmental impact of
# processes do *not* contribute to a parent material's environmental impact.

# #### **Processes**
#
# Processes are represented by ``ProcessWithSustainabilityResult`` objects. They include the
# ``.transport_stages`` property. This property consists of the transportation of the part
# during the manufacturing process, and is defined as a list of ``TransportWithSustainabilityResult``
# objects.
#
# The environmental impact of a process is calculated from database data and the dimensional details of
# the process defined in the BoM.
#
# Transport stages may appear as children of processes in the hierarchy, but the environmental impact of
# transport stages do *not* contribute to a parent process's environmental impact.

# ### The `BomSustainabilityQueryResult.transport` property
#
# The ``BomSustainabilityQueryResult.transport`` property contains the transport stages in the input
# BoM, which are defined as a list of ``TransportWithSustainabilityResult`` objects. Transport stages
# contain no BoM properties. The environmental impact of a transport stage is just the environmental
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
        yield from traverse_process(child_process, part_id)
    for child_transport in part.transport_stages:
        yield to_dict(child_transport, part_id)


def traverse_material(material, parent_id):
    yield to_dict(material, parent_id)
    for child_process in material.processes:
        yield from traverse_process(child_process, parent_id)


def traverse_process(process, parent_id):
    yield to_dict(process, parent_id)
    for child_transport in process.transport_stages:
        yield to_dict(child_transport, parent_id)


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
    elif isinstance(item, TransportWithSustainabilityResult):
        record.update({"type": "Transport", "name": item.name})
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
