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

# This example shows how to use the ``bom_types`` subpackage to create a valid Granta MI XML
# BoM. This subpackage can be used to help construct a Granta 24/12-compliant XML BoM file to
# use with the BoM queries provided by this package. The code in this example shows how to generate
# a BoM from a representative CSV data source. The general approach can be applied to data
# in other formats or provided by other APIs.

# You can download the [CSV file](../supporting-files/glass_door.csv) used in this example.

# The result of this example is a Granta 24/12-compliant XML BoM file that is suitable for
# compliance or sustainability analysis with the Granta MI BoM Analytics API. For more information on the
# expected content of XML BoMs, see the Granta MI documentation.

# ## Load the external data

# First load the CSV file and use ``pandas`` to load the content in a dataframe.

# +
import pandas as pd

df = pd.read_csv("../supporting-files/glass_door.csv")
df.head()
# -

# ## Inspect the external data
# The CSV file describes the bill of materials for the door assembly introduced in the
# [Creating an XML BoM](./6-1_Creating_an_XML_BoM.ipynb) example.
# The door (24X6-30) contains two hinges (HA-42-Al) and a handle (H-S-BR-Dual), both fixed to the panel (P-30-L) with
# machine screws (DIN-7991-M8-20) and washers (N0403.12N.2). The door glass (321-51) is coated with a partially
# reflective polymer film (7000001298).
#
# The hierarchy of items within the BoM is defined by the order of items in the CSV and the ``BoM Level`` field. If an
# item has the BoM level *n*, then the item's parent is the first level preceding it in the CSV with a BoM level *n-1*.
#
# Each item includes an ``Item Type`` field that identifies the type of the item, here only ``Part`` or ``Material``.
# Additional fields are specific to the type of item.
#
# ### Part items
#
# Items that refer to parts only exist in the BoM and do not reference records in Granta MI. Their ``Name`` and ``ID``
# are defined only in the BoM to identify parts.
#
# The ``Quantity`` and ``Unit of measure`` fields describe the quantity of part expected in the parent. This can be
# done by specifying how many occurrences of a part are in an assembly, or for example for the glass door, the surface
# area of laminated glass.
#
# There are three types of components in the BoM:
#
#  - The product described by the BoM, whose ``BoM Level`` is ``1``.
#  - Assemblies which are made of sub-parts.
#    - Their mass isn't defined in the BoM because it can be computed by rolling up the mass of the sub-parts.
#  - Parts which are defined by their mass and the material they are made of.
#    - Their mass is defined via the ``Measured mass (per UoM)`` and ``Measured mass unit``. The units for the mass
#       must be consistent with the unit used to define the quantity of the part, so that when the quantity is
#       multiplied with the mass per UoM, it resolves to a mass. For example, the quantity of glass panel included in
#       the door is defined as a surface area ``1.51 m^2``, which requires the mass per unit of measure to be defined
#       as a mass per surface area ``19.6 kg/m^2``.
#
# For more information on the different options available for specifying part quantities and part masses, see the
# Granta MI documentation.
#
# ### Material items
#
# Items that refer to materials correspond to records in Granta MI that contain the relevant compliance or
# sustainability information for these items. As a result, these items contain both a human-readable ``Name`` field and
# an ``ID`` field. In this scenario, the system that provided the data source contains the Granta MI material
# assignments for each part based on the ``Material ID`` attribute, which is included in the ``ID`` field.
#
# Materials are described in terms of percentage of the parent part made of the material.

# ## Build the ``BillsOfMaterials`` object
#
# Import the ``eco2412`` sub-package and helper classes to build record and attribute references.

# +
from ansys.grantami.bomanalytics.bom_types import eco2412, AttributeReferenceBuilder, RecordReferenceBuilder

DB_KEY = "MI_Restricted_Substances"
TABLE_NAME = "MaterialUniverse"
# -

# Define a function that accepts a part row as input and returns a ``eco2412.Part`` object.

def make_part(item: pd.Series) -> eco2412.Part:
    mass = item["Measured mass (per UoM)"]
    if not pd.isna(mass):
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

# Define a function that accepts a material row as input and returns a ``eco2412.Material`` object. Materials are
# identified by their attribute value ``Material ID``, so the record reference is defined using a lookup value.

# +
material_id_reference = (
    AttributeReferenceBuilder(DB_KEY)
    .with_attribute_name("Material ID")
    .with_table_name(TABLE_NAME)
    .build()
)

def make_material(item: pd.Series) -> eco2412.Material:
    unit = item["Unit of measure"]
    if unit == "%":
        percentage = item["Quantity"]
    else:
        raise ValueError("Method 'make_material' only supports quantities defined as percentages.")

    material_reference = (
        RecordReferenceBuilder(db_key=DB_KEY)
        .with_lookup_value(lookup_value=item["ID"], lookup_attribute_reference=material_id_reference)
        .build()
    )
    return eco2412.Material(
        mi_material_reference=material_reference,
        identity=item["ID"],
        name=item["Name"],
        percentage=percentage,
    )


# -

# Iterate over the rows in the CSV file and convert to ``bom_types`` objects. Because items only ever appear after
# their parent, a list is used to keep track of possible parent items in the BoM.

# Instantiate the hierarchy with an empty BoM object
bom = eco2412.BillOfMaterials(components=[])
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
# used in a BoM query.

from ansys.grantami.bomanalytics import BoMHandler
bom_as_xml = BoMHandler().dump_bom(bom)
print(f"{bom_as_xml[:500]}...")
