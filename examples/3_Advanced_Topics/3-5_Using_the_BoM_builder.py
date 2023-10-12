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

# # Using the BoM Builder

# You might have to deal with BoMs or other data structures stored in third-party systems. This
# example desmonstrates how to use the ``bom_types`` sub-package to create a valid Granta MI XML BoM.

# Although it is unlikely that the data structures and processing presented here match your
# requirements, this example is intended to demonstrate the principles behind using the BoM
# schema Python bindings within your existing processes. It shows how a BoM-like data structure
# can be loaded from a neutral format and converted to the XML format expected by the Granta
# MI BoM Analytics API. The approach is applicable to data in other formats, or data loaded
# from other software platform APIs.

# You can [download](supporting-files/source_data_sustainability.json) the external data source used in this
# example.
#
# The result of this example is a BoM that is compliant with the XSD XML schema (version 23/01) and that is suitable
# for sustainability analysis with the Granta MI BoM Analytics API. Further information about the expected content of
# XML BoMs can be found on the online Granta MI documentation.

# ## Load the external data

# First load the JSON file and use the ``json`` module to convert the text into a hierarchical structure of ``dict`` and
# ``list`` objects.

# +
import json
from pprint import pprint

with open("supporting-files/source_data_sustainability.json") as f:
    data = json.load(f)
pprint(data[:3])
# -

# ## Inspect the external data
# The external data source defines a flat list of items. Each item has a ``type`` field, identifying the type of the
# item, a ``parent_part_identifier`` identifying the parent part in the hierarchy, as well as fields specific to each
# type of item.
#
# ### Components
# The external data source defines multiple types of component:
#
# - A single item of type ``Product``. The external data source describes the bill of materials for this product. All
# other items are expected to be children of this item.
# - Items of type ``Assembly``.
# - Items of type ``Part``.
#

# +
source_product = next(item for item in data if item["type"] == "Product")
source_product
# -

# +
source_assemblies = [item for item in data if item["type"] == "Assembly"]
source_assemblies[0]
# -

# +
source_parts = [item for item in data if item["type"] == "Part"]
source_parts[0]
# -

# ### Materials
# The third party system allows assignment from Granta MI. Materials are therefore described by a unique identifier to
# a Granta MI record (GUID). This ensures that data isn't duplicated: the material data is stored in Granta MI, and
# other systems refer to it by identifiers.
#
# In the external data source, materials are described by a ``name`` and a field that contains the GUID uniquely
# identifying the assigned material.
# The third-party system allows assignment of a single material per part, so there is no quantity associated with the
# material. It is assumed that the part referenced in the material's ``parent_part_identifier`` is made only of this
# material.

# +
source_materials = [item for item in data if item["type"] == "Material"]
source_materials[0]
# -

# ### Processes
# There are multiple types of processes described by the external data source:
#
# - ``MaterialFormingStep`` describes a process which formed a mass of material into a shaped component. The third
# party system defines a single forming process for each part. These processes will be mapped to ``Primary processes``
# in Granta MI Sustainability.
#
# - ``MaterialProcessingStep`` are optional extra processing steps applied after the main forming processing step.
# Given the format of the data exported from the third party system, processing steps include a ``step_order`` field,
# which describes the order in which processing steps are applied to the parent part. Processing steps define a
# ``mass_removed_in_kg`` field, describing the quantity of material removed during the step. These processes will be
# mapped to ``Secondary processes`` in Granta MI Sustainability.
# - ``PartProcessingStep`` are optional processes applied directly to parts. These processes will be mapped to
# ``Joining & Finishing processes`` in Granta MI sustainability.
#
# All processes are described by a human-readable name and include the GUID of the assigned Granta MI Process record.
# Similarly to materials, the third-party system does not store information about the process other than the reference
# to the Granta MI record, which defines the environmental footprint of the process.

# +
source_primary_processes = [item for item in data if item["type"] == "MaterialFormingStep"]
source_primary_processes[0]
# -

# +
source_secondary_processes = [item for item in data if item["type"] == "MaterialProcessingStep"]
source_secondary_processes[0]
# -

# +
source_joining_processes = [item for item in data if item["type"] == "PartProcessingStep"]
source_joining_processes[0]
# -

# ### Transports
# The external data source defines transport stages. These items of type ``Transport`` define the distance that
# is travelled during the step, and hold a reference to the assigned Granta MI Transport record, which defines the
# environmental footprint per distance for the transportation mode.

source_transports = [item for item in data if item["type"] == "Transport"]
source_transports[0]

# ## Build the BillOfMaterials
#
# The PyGranta BoM Analytics package provides a sub-package ``bom_types``, which implement Python bindings for the BoM
# XML schema. It facilitates serialization and deserialization of Granta MI BoMs to and from Python objects.
# This section shows how data from the external data source is processed to create BoM Python objects, which can then
# be used to generate an XML BoM.

# If you are using a database with custom names, change the database key value in the following cell and refer
# to the [Database specific configuration](../3_Advanced_Topics/3-3_Database-specific_configuration.ipynb) example to
# appropriately configure the connection before running any queries.

from ansys.grantami.bomanalytics import bom_types
DB_KEY = "MI_Restricted_Substances"

# ### Components
#
# The third-party system defines a ``part_identifier`` field that uniquely identifies parts. However, the
# Granta MI BoM schema requires a Part to define a ``Part number``. We will use the external ``part_identifier`` as a
# part number.
# First, create a ``bom_types.Part`` object for every item that maps to a BoM Part, and add it to a mapping indexed
# by the part number. This will allow us to identify the correct parent part to add materials and processes to.

# +
components = {}

# Product
product_id = source_product["part_identifier"]
components[product_id] = bom_types.Part(part_number=product_id, quantity=bom_types.UnittedValue(value=1.0, unit="Each"))

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
# -

pprint(components)

# Now that all the parts have been instantiated, the hierarchy can be defined. While the external data source defines
# the hierarchy using references between objects in a flat data structure, a Granta MI BoM represents the hierarchy by
# including a child object as a property of the parent.
# The following cell iterates over all source parts and assemblies again, and appends child parts to their
# parents' ``components`` property.

# +
for item in source_assemblies + source_parts:
    item_id = item["part_identifier"]
    parent_item_id = item["parent_part_identifier"]
    item_bom_definition = components[item_id]
    parent_item_bom_definition = components[parent_item_id]
    parent_item_bom_definition.components.append(item_bom_definition)

pprint(components)
# -

# ### Materials
#
# Materials can now be added to parts. In a Granta MI BoM, the structure is hierarchical and each ``Part``
# defines its material via the ``Part.materials`` property. ``Material`` objects only then need to define the
# reference to the record in Granta MI.
#
# There are multiple possible ways of identifying Granta MI records in the BoM. In this example, the external data
# source holds references to Granta MI records by record GUIDs. The GUIDs will be used to instantiate
# ``MIRecordReference`` objects.

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

# ### Processes
#
# Some processes apply directly to parts and can already be added to parts in the hierarchy.
# The order in which processes are applied can be important. The external system defines a ``step_order`` field, which
# represents the order in which processes are applied to the parent part. We first sort the processes by ``step_order``
# to ensure that they are added to the ``Part`` in the same order as defined by the external data source.
#
# The example external data only includes one type of part processes, which are quantified using a length. The Granta
# MI BoM schema has support for different ``DimensionType`` values: this is to represent the impact of a process based
# on its most representative dimension. For example, welding generally is defined by the welding path length, whereas
# a coating operation is best quantified by the affected surface area.
# A simple mapping defines a lookup between the unit found in the external data source and the dimension type used in
# the corresponding ``Process``.

# +
unit_to_dimension_type = {
    "m": bom_types.DimensionType.Length,
}

# Sort items before iterating
source_joining_processes.sort(key=lambda item: (item["parent_part_identifier"], item["step_order"]))

for item in source_joining_processes:
    parent_part_id = item["parent_part_identifier"]
    process = bom_types.Process(
        mi_process_reference=make_record_reference(item),
        identity=item["name"],
        dimension_type=unit_to_dimension_type[item["quantity_unit"]],
        quantity_affected=bom_types.UnittedValue(value=item["quantity"], unit=item["quantity_unit"]),
        )
    components[parent_part_id].processes.append(process)
# -

# Finally, primary and secondary processes can be added. In the external data source, processes only refer to the
# parent, as it is assumed that there is only a single material per part.
# The Granta MI BoM schema allows multiple materials per part, but sustainability analysis can only be performed on
# BoMs with a single material per part.
# Since there is only one material per part, we can use the ``parent_part_identifier`` of processes to resolve the part
# in the mapping defined earlier, retrieve the single material, and assign the process to the material.
# The single primary process must be the first in the list. Then, secondary processes can be added to the list, in the
# order defined by ``step_order``.
#
# ``MaterialFormingStep`` processes from the external data source are all mapped to ``Process`` with a ``Mass``
# dimension type. This is the default value for processes whose environmental impact is calculated based on the mass
# of material that goes through the process. This mass is calculated from the final mass of the part and mass removed
# during additional processing steps. See the online Granta MI documentation for more information about mass
# calculations.
# ``MaterialProcessingStep`` processes from the external data source are mapped to ``Process`` with a ``MassRemoved``
# dimension type. For this type of processes, the environmental impact is calculated from the mass of material removed.

# +
for item in source_primary_processes:
    parent_part_id = item["parent_part_identifier"]
    process = bom_types.Process(
        mi_process_reference=make_record_reference(item),
        identity=item["name"],
        dimension_type=bom_types.DimensionType.Mass,
        percentage_of_part_affected=100.0
    )
    components[parent_part_id].materials[0].processes.append(process)

source_secondary_processes.sort(key=lambda item: (item["parent_part_identifier"], item["step_order"]))
for item in source_secondary_processes:
    parent_part_id = item["parent_part_identifier"]
    process = bom_types.Process(
        mi_process_reference=make_record_reference(item),
        identity=item["name"],
        dimension_type=bom_types.DimensionType.MassRemoved,
        quantity_affected=bom_types.UnittedValue(
            value=item["mass_removed_in_kg"],
            unit="kg",
        )
    )
    components[parent_part_id].materials[0].processes.append(process)
# -

# ### BillOfMaterials
#
# Now that the all parts, materials, and processes have been processed and redefined in a hierarchical structure, build
# a ``BillOfMaterials`` object, assign the top-level product as the single component, and add the transport stages,
# which apply to the whole product.

# +
bom = bom_types.BillOfMaterials(components=[components[product_id]])

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


# Use the ``BomHandler`` helper class to serialize the object to XML. The resulting string can be used in a
# sustainability query. See [Sustainability examples](../4_Sustainability/index.rst).

from ansys.grantami.bomanalytics import BoMHandler
bom_as_xml = BoMHandler().dump_bom(bom)
print(bom_as_xml)
