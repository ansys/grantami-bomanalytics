# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
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

# # Create an XML BoM using Python

# The `bom_types` namespace can be used in conjunction with the `BoMHandler` class to
# create and manipulate BoMs for analysis. This example demonstrates creating a BoM for
# a laminated glass door and then uses the BoM as the input to a compliance query.

# The door contains two hinges and a handle, both fixed to the frame with machine screws and
# washers, the door glass is coated with a partially reflective polymer film.

# Most installations of Granta MI will use the default database key and table names:

DB_KEY = "MI_Restricted_Substances"
TABLE_NAME = "MaterialUniverse"

# The structure of an XML BoM is hierarchical, individual parts belong to assemblies which can
# belong to larger assemblies. It is possible to construct the BoM in one statement, but this
# example uses the recommended approach of building each part up from objects that represent
# smaller sub-assemblies.

# It is possible to have the same part in multiple places in the BoM, so we define two helper functions
# to create a copy of a part and set the quantity.

# +
import copy

from ansys.grantami.bomanalytics.bom_types.eco2412 import BillOfMaterials, Material, Part, UnittedValue
from ansys.grantami.bomanalytics.bom_types.gbt1205 import MIRecordReference

def add_part_to_assembly_with_count(child: Part, count: int) -> Part:
    return add_part_to_assembly_with_quantity(child, float(count), "Each")

def add_part_to_assembly_with_quantity(child: Part, quantity: float, unit: str) -> Part:
    assigned_part = copy.deepcopy(child)
    assigned_part.quantity = UnittedValue(quantity, unit=unit)
    return assigned_part
# -

# Material references define abstract references to Granta MI records, and so can be reused.
# Material references can be defined in different ways.

# The following references are created using different types of GUID. Record GUIDs identify a
# specific version of the record, while Record History GUIDs identify the latest accessible
# version of the record.

laminated_glass_reference = MIRecordReference(db_key=DB_KEY, record_guid="85ed8b21-c2e6-4c43-8ec3-4c12a44c820c")
hardened_stainless_reference = MIRecordReference(db_key=DB_KEY, record_guid="fcc49a93-6b92-4751-9b85-f00b7769190d")
nylon_pa6_reference = MIRecordReference(db_key=DB_KEY, record_history_guid="1c7884dd-80ed-4661-89d6-4b6e56a08ed7")

# Some databases also have unique identifiers for materials. If these are Short Text attributes
# they can be used as lookup values, for example in MaterialUniverse we can use the "Material ID"
# attribute.

# +
from ansys.grantami.bomanalytics.bom_types import AttributeReferenceBuilder

material_id_reference = (AttributeReferenceBuilder(DB_KEY)
                         .with_attribute_name("Material ID")
                         .with_table_name(TABLE_NAME)
                         .build())

pet_film_reference = MIRecordReference(
    db_key=DB_KEY,
    lookup_attribute_reference=material_id_reference,
    lookup_value="plastic-pet"
)
annealed_stainless_reference = MIRecordReference(
    db_key=DB_KEY,
    lookup_attribute_reference=material_id_reference,
    lookup_value="stainless-304-annealed"
)
aluminium_319_reference = MIRecordReference(
    db_key=DB_KEY,
    lookup_attribute_reference=material_id_reference,
    lookup_value="aluminum-319-0-moldcast-t6"
)
steel_1015_reference = MIRecordReference(
    db_key=DB_KEY,
    lookup_attribute_reference=material_id_reference,
    lookup_value="steel-1015-normalized"
)
# -

# Nylon washers exist in multiple parts, so define these first. The part number has no effect
# on the analysis and simply identifies each part in the result.

washer_part = Part(
    part_number="N0403.12N.2",
    mass_per_unit_of_measure=UnittedValue(2., "g/Part"),
    materials=[Material(mi_material_reference=nylon_pa6_reference, percentage=100.)]
)

# Start with sub-assemblies and assemble the BoM.
# The hinge assembly consists of two casting parts, four washers, and two machine screws

# +
hinge_casting_a = Part(
    part_number="HA-42-Al(A)",
    mass_per_unit_of_measure=UnittedValue(146., "g/Part"),
    materials=[Material(mi_material_reference=aluminium_319_reference, percentage=100.)]
)

hinge_casting_b = Part(
    part_number="HA-42-Al(B)",
    mass_per_unit_of_measure=UnittedValue(220., "g/Part"),
    materials=[Material(mi_material_reference=aluminium_319_reference, percentage=100.)]
)

machine_screw_part = Part(
    part_number="DIN-7991-M8-20",
    mass_per_unit_of_measure=UnittedValue(8.6, "g/Part"),
    materials=[Material(mi_material_reference=hardened_stainless_reference, percentage=100.)]
)

hinge_assembly = Part(
    part_number="HA-42-Al",
    components=[
        add_part_to_assembly_with_count(hinge_casting_a, 1),
        add_part_to_assembly_with_count(hinge_casting_b, 1),
        add_part_to_assembly_with_count(washer_part, 4),
        add_part_to_assembly_with_count(machine_screw_part, 2),
    ]
)
# -

# The handle assembly consists of two stainless steel handles, two mild steel pins, four
# nylon washers and a pair of grub screws. The pin screws into part B and is retained in
# part A with a grub screw.

# +
handle_part_a = Part(
    part_number="H-S-BR-A",
    mass_per_unit_of_measure=UnittedValue(472., "g/Part"),
    materials=[Material(mi_material_reference=annealed_stainless_reference, percentage=100.)]
)

handle_part_b = Part(
    part_number="H-S-BR-B",
    mass_per_unit_of_measure=UnittedValue(464., "g/Part"),
    materials=[Material(mi_material_reference=annealed_stainless_reference, percentage=100.)]
)

handle_pin_part = Part(
    part_number="H-PIN-12",
    mass_per_unit_of_measure=UnittedValue(46.5, "g/Part"),
    materials=[Material(mi_material_reference=steel_1015_reference, percentage=100.)]
)

handle_grub_screw_part = Part(
    part_number="SSF-M4-6-A2",
    mass_per_unit_of_measure=UnittedValue(1.3, "g/Part"),
    materials=[Material(mi_material_reference=hardened_stainless_reference, percentage=100.)]
)

handle_assembly = Part(
    part_number="H-S-BR-Dual",
    components=[
        add_part_to_assembly_with_count(handle_part_a, 1),
        add_part_to_assembly_with_count(handle_part_b, 1),
        add_part_to_assembly_with_count(handle_pin_part, 2),
        add_part_to_assembly_with_count(washer_part, 4),
        add_part_to_assembly_with_count(handle_grub_screw_part, 2)
    ]
)
# -

# The glass panel consists of a laminated glass door and a layer of PET solar control
# film.

# +
glass_panel = Part(
    part_number="321-51",
    mass_per_unit_of_measure=UnittedValue(19.6, "kg/m^2"),
    materials=[Material(mi_material_reference=laminated_glass_reference, percentage=100.)])

solar_control_film = Part(
    part_number="7000001298",
    mass_per_unit_of_measure=UnittedValue(340., "g/m^2"),
    materials=[Material(mi_material_reference=pet_film_reference, percentage=100.)]
)

panel_assembly = Part(
    part_number="P-30-L",
    components=[
        add_part_to_assembly_with_quantity(glass_panel, 1.51, "m^2"),
        add_part_to_assembly_with_quantity(solar_control_film, 1.51, "m^2"),
    ]
)
# -

# The whole door assembly is then a combination of two hinges, one handle assembly and one
# door panel.

door_assembly = Part(
    part_number="24X6-30",
    components=[
        add_part_to_assembly_with_count(hinge_assembly, 2),
        add_part_to_assembly_with_count(handle_assembly, 1),
        add_part_to_assembly_with_count(panel_assembly, 1),
    ]
)

# Generate a BoM from the door assembly part, and dump the BoM to XML.

# +
from ansys.grantami.bomanalytics import BoMHandler

door_assembly_bom = BillOfMaterials(components=[door_assembly])
bom_handler = BoMHandler()

rendered_bom = bom_handler.dump_bom(door_assembly_bom)
rendered_bom.splitlines()[0:10]
# -

# Now that you have created an XML BoM, run a compliance query to determine whether the BoM complies
# with a specific legislation.
# First, connect to Granta MI.

# +
from ansys.grantami.bomanalytics import Connection

server_url = "http://my_grantami_server/mi_servicelayer"
cxn = Connection(server_url).with_credentials("user_name", "password").connect()
# -

# The compliance BoM query accepts a single XML BoM as a string and one or more indicators. In
# this case we perform a query against the SIN list, using the RoHS indicator with a threshold
# of 0.1%.

# +
from ansys.grantami.bomanalytics import indicators, queries

sin_list = indicators.WatchListIndicator(
    name="EU REACH Candidate List",
    legislation_ids=["Candidate_AnnexXV"],
    default_threshold_percentage=0.1,
)

compliance_query = (
    queries.BomComplianceQuery()
    .with_bom(rendered_bom)
    .with_indicators([sin_list])
)

compliance_result = cxn.run(compliance_query)
compliance_result
# -

# The ``BomComplianceQueryResult`` object returned after running the compliance query contains a list of
# ``PartWithComplianceResult`` objects.
# The following cell prints the compliance status of the BoM.

root_part = compliance_result.compliance_by_part_and_indicator[0]
print(f"BoM Compliance Status: {root_part.indicators['EU REACH Candidate List'].flag.name}")
