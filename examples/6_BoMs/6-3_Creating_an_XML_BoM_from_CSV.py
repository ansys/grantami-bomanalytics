# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.17.2
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# # Create an XML BoM from a CSV data source

# ## This example shows how to use the ``bom_types`` subpackage to create a valid Granta MI XML
# BoM. This subpackage can be used to help construct a Granta 24/12-compliant XML BoM file to
# use with the BoM queries provided by this package. The code in this example shows how to generate
# a BoM from a representative CSV data source. The general approach can be applied to data
# in other formats or provided by other APIs.

# You can download the [csv file](../supporting-files/glass_door.csv) used in this example.

# The result of this example is a Granta 24/12-compliant XML BoM file that is suitable for
# compliance analysis with the Granta MI BoM Analytics API. For more information on the
# expected content of XML BoMs, see the Granta MI documentation.

# ## Load the external data

# First load the CSV file and use ``pandas`` to load the content in a dataframe.

# +
import pandas

df = pandas.read_csv("../supporting-files/glass_door.csv")
df.head()

# + [markdown] jp-MarkdownHeadingCollapsed=true
# ## Inspect the external data
# The external data source defines a flat list of items.
#
# Hierarchy of items within the BoM is defined by the order of items in the list and the ``BoM Level`` field.
#
# Each item has at least the following:
#
# - A ``Item Type`` field that identifies the type of the item.
# - ``Quantity`` and ``Unit of measure`` fields that describe the quantity of the item. Typically, materials are described
#   in terms of percentage of the parent part made of the material, and components are described in terms of number of
#   occurrences of the part in the parent part.
#
# ### Components
#
# Items that refer to components do not have an equivalent record in Granta MI. Their names and ID are defined only in
# the BoM.
#
# There are three types of components in the BoM:
#  
#  - The product described by the BoM, whose ``BoM Level`` is ``1``.
#  - Assemblies which are made of sub-parts.
#  - Parts which are defined by their mass and the material they are made of.
#
# ### Materials
#
# Items that refer to materials correspond to records in Granta MI that contain the relevant compliance information
# for these items. As a result, these items contain both a human-readable ``Name`` field and a ``ID`` field. In this
# scenario, the system that provided the data source contains the direct material assignments from
# Granta MI and the ``ID`` fields contains the value of the ``Material ID`` attribute for the material records.
# -

# ## Build the ``BillsOfMaterials`` object
#
# Instantiate a ``BillsOfMaterials`` object. It will be populated with content as the content of the csv is processed.

# +
from ansys.grantami.bomanalytics.bom_types import eco2412, gbt1205

DB_KEY = "MI_Restricted_Substances"
TABLE_NAME = "MaterialUniverse"

bom = eco2412.BillOfMaterials(components=[])


# -

# Define a method to process a row that represents a part and create the appropriate object.
#
# In this example, parts are specified in two differents ways:
#
#  - Via non-mass units. For example ``HA-42-Al`` is included twice in its parent ``24X6-30``, and its mass is defined as mass per occurence of the part.
#  - Via mass units. For example ``321-51`` is present in the BoM and specified as a surface area. Its mass is therefore defined as a mass per surface area.
#
# For more information on the different options available for specifying part quantities and part masses, see the Granta MI documentation.

def make_part(item: pandas.Series) -> eco2412.Part:
    mass = item["Measured mass (per UoM)"]
    if not pandas.isna(mass):
        mass_per_unit_of_measure = eco2412.UnittedValue(
            value=mass,
            unit=item["Measured mass unit"],
        )
    else:
        mass_per_unit_of_measure = None
    return eco2412.Part(
        part_number=item["ID"],
        part_name=item["Name"],
        quantity=eco2412.UnittedValue(value=item["Quantity"], unit=item["Unit of measure"]),
        mass_per_unit_of_measure=mass_per_unit_of_measure,
    )

# Define a method to process a row that represents a material and instantiate a ``eco2412.Material``. Materials are identified by their attribute value ``Material ID``, so the record reference is defined using a lookup value.

# +
material_id_reference = gbt1205.MIAttributeReference(
    db_key=DB_KEY,
    table_reference=gbt1205.PartialTableReference(table_name=TABLE_NAME),
    attribute_name="Material ID",
)

def make_material(item: pandas.Series) -> eco2412.Material:
    unit = item["Unit of measure"]
    if unit == "%":
        percentage = item["Quantity"]
    else:
        raise ValueError("Method 'make_material' only supports quantities defined as percentages.")
    return eco2412.Material(
        mi_material_reference=gbt1205.MIRecordReference(
            db_key=DB_KEY,
            lookup_attribute_reference=material_id_reference,
            lookup_value=item["ID"]
        ),
        identity=item["ID"],
        name=item["Name"],
        percentage=percentage,
    )


# -

# Iterate over the rows in the CSV file and convert to ``bom_types`` objects. Because items only ever appear after their parent, a list is used to keep track of possible parent items in the BoM.

# Instantiate the hierarchy with the empty BoM object
path = [bom]
for _, item_row in df.iterrows():
    item_level = item_row["BoM Level"]
    parent = path[item_level - 1]

    item_type = item_row["Item Type"]
    if item_type == "Part":
        item = make_part(item_row)
        parent.components.append(item)
    elif item_type == "Material":
        item = make_material(item_row)
        parent.materials.append(item)
    else:
        raise ValueError(f"Unsupported 'Item Type': '{item_type}'")
        
    # Update the hierarchy with the newly created item
    path = path[:item_level] + [item]

# ## Serialize the BoM
#
# Use the ``BomHandler`` helper class to serialize the object to XML. The resulting string can be
# used in a compliance query. For more information, see the
# [Compliance examples](../3_Compliance_Queries/index.rst).

from ansys.grantami.bomanalytics import BoMHandler
bom_as_xml = BoMHandler().dump_bom(bom)
print(f"{bom_as_xml[:500]}...")
