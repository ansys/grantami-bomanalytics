# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
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

# # Creating a Bill of Materials from an external data source

# This example demonstrates how to use the ``bom_types`` sub-package to create a valid Granta MI XML
# BoM. This sub-package can be used to help construct a Granta 23/01-compliant XML BoM file to be
# used with the BoM queries provided by this package. The code in this example shows how to generate
# a BoM from a representative JSON data source, and so the general approach can be applied to data
# in other formats or provided by other APIs.

# You can download the external data source used in this example
# [here](supporting-files/source_data_sustainability.json).

# The result of this example is a Granta 23/01-compliant XML BoM file that is suitable for
# sustainability analysis with the Granta MI BoM Analytics API. For further information about the
# expected content of XML BoMs, consult the online Granta MI documentation or your ACE
# representative.

# ## Load the external data

# First load the JSON file and use the ``json`` module, which converts the text into a hierarchical
# structure of ``dict`` and ``list`` objects.

# +
import json
from pprint import pprint

with open("supporting-files/source_data_sustainability.json") as f:
    data = json.load(f)
pprint(data[:3])
# -

# ## Inspect the external data
# The external data source defines a flat list of items. Each item has at least the following:
#
# - A ``type`` field, which identifies the type of the item.
# - A ``parent_part_identifier`` field, which identifies the parent part in the hierarchy.
#
# Items that refer to components do not have an equivalent record in Granta MI, and so they
# contain only the fields described above, and the quantity and mass field.
#
# Items that refer to materials, processes, and transport steps correspond to records in Granta MI
# which contain the relevant sustainability metrics for these items. As a result, these items
# contain both a human-readable ``name`` field and a ``Granta_MI_Record_GUID`` field. In this
# scenario, the system that provided the data source contains the direct material assignments from
# Granta MI.

# ### Components
# The external data source defines three different types of component:
#
# - A single item of type ``Product``. The external data source describes the bill of materials for
#   this product. All other items are expected to be children of this item.
# - Items of type ``Assembly``.
# - Items of type ``Part``.
#
# Extract the items into separate lists based on the ``type`` field. The ``Product`` item is stored
# in a variable directly because there can only be one product per BoM by definition.

source_product = next(item for item in data if item["type"] == "Product")
source_product

source_assemblies = [item for item in data if item["type"] == "Assembly"]
source_assemblies[0]

source_parts = [item for item in data if item["type"] == "Part"]
source_parts[0]

# ### Materials
# The third-party system only allows assignment of a single material per part, and so there is no
# 'quantity' associated with the material. It is assumed that the part is made entirely of the
# referenced material.
#
# Extract the material items into a list based on the ``type`` field.

source_materials = [item for item in data if item["type"] == "Material"]
source_materials[0]

# ### Processes
# The external data source defines three different types of process:
#
# - ``MaterialFormingStep`` items describe a process which forms a mass of material into a shaped
#   component. In this scenario, the third party system defines a single forming process for each
#   part. These processes will be mapped to ``Primary processes`` in the Granta MI BoM.
# - ``MaterialProcessingStep`` items describe extra processing steps applied after the main forming
#   processing step. These items include ``step_order`` and ``mass_removed_in_kg`` fields, which
#   together fully describe the material removal. These processes will be mapped to
#   ``Secondary processes`` in the Granta MI BoM.
# - ``PartProcessingStep`` items describe processes applied directly to parts. These processes will
#   be mapped to ``Joining & Finishing processes`` in the Granta MI BoM.
#
# Extract the process items into lists based on their ``type`` fields.

source_primary_processes = [item for item in data if item["type"] == "MaterialFormingStep"]
source_primary_processes[0]

source_secondary_processes = [item for item in data if item["type"] == "MaterialProcessingStep"]
source_secondary_processes[0]

source_joining_processes = [item for item in data if item["type"] == "PartProcessingStep"]
source_joining_processes[0]

# ### Transports
# The external data source defines transport stages. These items of type ``Transport`` contain a
# ``distance_in_km`` field which contains the distance covered by the transport step.
#
# Extract the transport items into a list based on their ``type`` fields.

source_transports = [item for item in data if item["type"] == "Transport"]
source_transports[0]

# ## Build the BillOfMaterials object
#
# The PyGranta BoM Analytics package provides the ``bom_types`` sub-package, which implements
# serialization and deserialization between the Granta 23/01 BoM XML schema and Python objects. This
# section shows how data from the external data source is processed to create BoM Python objects,
# which can then be serialized to an XML BoM.

# If you are using a customized database, change the database key value in the following cell
# and refer to the
# [Database specific configuration](3-3_Database-specific_configuration.ipynb) example to
# appropriately configure the connection before running any queries.

from ansys.grantami.bomanalytics import bom_types
DB_KEY = "MI_Restricted_Substances"

# ### Components
#
# The external system defines a ``part_identifier`` field that uniquely identifies parts. However,
# the Granta MI BoM schema requires a Part to define a ``Part number``. Use the external
# ``part_identifier`` as a part number.
#
# First, create a ``bom_types.Part`` object for every item that maps to a BoM Part, and add it to a
# dictionary indexed by the part number. This will allow us to identify the correct parent part
# when adding materials and processes.

# +
components = {}

# Product
product_id = source_product["part_identifier"]
components[product_id] = bom_types.Part(
    part_number=product_id,
    quantity=bom_types.UnittedValue(
        value=1.0,
        unit="Each"
    )
)

# Assemblies
for item in source_assemblies:
    item_id = item["part_identifier"]
    components[item_id] = bom_types.Part(
        part_number=item_id,
        quantity=bom_types.UnittedValue(
            value=item["quantity_in_parent"],
            unit="Each",
        )
    )

# Parts
for item in source_parts:
    item_id = item["part_identifier"]
    components[item_id] = bom_types.Part(
        part_number=item_id,
        quantity=bom_types.UnittedValue(
            value=item["quantity_in_parent"],
            unit="Each",
        ),
        mass_per_unit_of_measure=bom_types.UnittedValue(
            value=item["part_mass_in_kg"],
            unit="kg/Each"
        )
    )

print(f"The components dict contains {len(components)} items.")
# -

# Next, define the hierarchy. The external data source defines a hierarchy by reference (i.e. the
# child part contains the identity of the parent part), but the Granta MI BoM represents the
# hierarchy via the BoM structure (i.e. a parent part contains all child parts as properties on the
# parent).
#
# The following cell iterates over all source parts and assemblies again, and appends child parts to
# their parents' ``components`` property.

for item in source_assemblies + source_parts:
    item_id = item["part_identifier"]
    parent_item_id = item["parent_part_identifier"]
    item_bom_definition = components[item_id]
    parent_item_bom_definition = components[parent_item_id]
    parent_item_bom_definition.components.append(item_bom_definition)

# ### Materials
#
# Next, create ``bom_types.Material`` objects for each material, and add the materials to their
# parent part object.
#
# There are multiple possible ways of identifying Granta MI records in the BoM. In this example, the
# external data source holds references to Granta MI records by record GUIDs, and so the GUIDs will
# be used to instantiate the required ``MIRecordReference`` objects.

# +
def make_record_reference(item, db_key=DB_KEY):
    return bom_types.MIRecordReference(
        db_key=db_key,
        record_guid=item["Granta_MI_Record_GUID"]
    )


for item in source_materials:
    parent_part_id = item["parent_part_identifier"]
    material = bom_types.Material(
        mi_material_reference=make_record_reference(item),
        identity=item["name"],
        percentage=100.0,
        )
    components[parent_part_id].materials.append(material)
# -

# ### Processes
#
# In general, the order in which processes are applied is significant and can affect the result. To
# ensure consistency, the external system defines a ``step_order`` field, which represents the order
# in which processes are applied to the parent part or material. The cells in this section first
# sort the processes by ``step_order`` to ensure that they are added to the BoM correctly.
#
# First, apply primary and secondary processes to materials. In the external data source, the parent
# of a process item is always the parent part, but sustainability analysis expects only a single
# material can be assigned to each part. As a result, the process can be moved from the part to the
# material when constructing the Granta BoM.
#
# ``MaterialFormingStep`` processes from the external data source are all mapped to ``Process`` with
# a ``Mass`` dimension type. This is the default value for processes whose environmental impact is
# calculated based on the mass of material that goes through the process. This mass is calculated
# from the final mass of the part and mass removed during additional processing steps. See the
# online Granta MI documentation for more information about mass calculations.

for item in source_primary_processes:
    process = bom_types.Process(
        mi_process_reference=make_record_reference(item),
        identity=item["name"],
        dimension_type=bom_types.DimensionType.Mass,
        percentage=100.0
    )
    # Use the parent part identifier to retrieve the part created earlier
    parent_part_id = item["parent_part_identifier"]
    # Append the process to the part via the assigned material
    components[parent_part_id].materials[0].processes.append(process)

# Next, apply secondary processes to materials. These are added sequentially to the list of
# processes on the material object, in the same order as defined by the ``step_order`` field.
#
# ``MaterialProcessingStep`` processes from the external data source are mapped to ``Process`` with
# a ``MassRemoved`` dimension type. For this type of processes, the environmental impact is
# calculated based on the mass of material removed.

# Sort the list of secondary processes by the ``step_order`` field.
source_secondary_processes.sort(key=lambda item: (item["parent_part_identifier"], item["step_order"]))
for item in source_secondary_processes:
    process = bom_types.Process(
        mi_process_reference=make_record_reference(item),
        identity=item["name"],
        dimension_type=bom_types.DimensionType.MassRemoved,
        quantity=bom_types.UnittedValue(
            value=item["mass_removed_in_kg"],
            unit="kg",
        )
    )
    parent_part_id = item["parent_part_identifier"]
    components[parent_part_id].materials[0].processes.append(process)

# Finally, apply joining and finishing processes to the part.
#
# The example external data only includes part processes characterized by the length dimension.
# However, the Granta MI BoM schema has support for different ``DimensionType`` values depending on
# the process. For example, welding is typically defined by a welding path length, but a coating
# operation would be best quantified by an area.

# +
unit_to_dimension_type = {
    "m": bom_types.DimensionType.Length,
}

source_joining_processes.sort(key=lambda item: (item["parent_part_identifier"], item["step_order"]))

for item in source_joining_processes:
    process = bom_types.Process(
        mi_process_reference=make_record_reference(item),
        identity=item["name"],
        # Map the unit in the input file to the DimensionType enum.
        dimension_type=unit_to_dimension_type[item["quantity_unit"]],
        quantity=bom_types.UnittedValue(
            value=item["quantity"],
            unit=item["quantity_unit"]
        ),
    )
    parent_part_id = item["parent_part_identifier"]
    components[parent_part_id].processes.append(process)
# -

# ### BillOfMaterials
#
# The original root part can now be retrieved from the ``components`` dictionary. This ``Part`` item
# contains the entire structure of parts, materials, and process objects. The cell below extracts
# this component from the dictionary of all components, deletes the dictionary, and prints
# an arbitrary property of the root component to illustrate this structure.

root_component = components[source_product["part_identifier"]]
del components
print(root_component.components[0].components[1].materials[0].processes[1].identity)

# The final step is to create a ``BillOfMaterials`` object and add the root component and transport
# stages. Note that the transport stages are added to the ``BillOfMaterials`` object itself, not to
# a specific component.

# +
bom = bom_types.BillOfMaterials(components=[root_component])

transports = [
    bom_types.TransportStage(
        name=item["name"],
        mi_transport_reference=make_record_reference(item),
        distance=bom_types.UnittedValue(value=item["distance_in_km"], unit="km")
    )
    for item in source_transports
]
bom.transport_phase = transports
# -

# # Serialize the BoM
#
# Use the ``BomHandler`` helper class to serialize the object to XML. The resulting string can be
# used in a sustainability query. See [Sustainability examples](../4_Sustainability/index.rst).

from ansys.grantami.bomanalytics import BoMHandler
bom_as_xml = BoMHandler().dump_bom(bom)
print(f"{bom_as_xml[:500]}...")
