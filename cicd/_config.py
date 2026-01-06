# ------------------ General configuration ------------------

MI_URL = "http://localhost/mi_servicelayer"
"""Granta MI Service Layer URL"""

RS_DB_KEY_CURRENT = "MI_Restricted_Substances"
"""Current Restricted Substances & Sustainability database key"""

RS_DB_KEY_NEW = "MI_Restricted_Substances_NewVersion"
"""New Restricted Substances & Sustainability database key"""

CUSTOM_DB_KEY_NEW = "MI_Restricted_Substances_NewVersion_CustomTables"
"""New Restricted Substances & Sustainability database key for the 'custom tables' variant."""

FOREIGN_DB_KEY = "MI_Restricted_Substances_Foreign_Test"
"""Restricted Substances & Sustainability database key for the foreign test database."""

MI_TRAINING_DB_KEY = "MI_Training"
"""Granta MI Training database key."""

DATA_FILENAME = "rs_data.json"
"""
Filename of the data interchange file defining the reduced set of data to be preserved in a Restricted Substances &
Sustainability database.

Created during step 1 (1_get_cleaned_db_entries.py) by extracting data from the current PyGranta BoM Analytics test
database, and consumed during step 2 (2_prepare_rs_db.py) by creating the relevant schema objects in a vanilla
Restricted Substances & Sustainability database.
"""

# ------------------ 1_get_cleaned_db_entries.py ------------------

TABLE_INFORMATION = {
    # Table name: {"layout": Layout name, "subset": Subset name}
    "MaterialUniverse": {"layout": "All attributes", "subset": "All materials"},
    "Materials - in house": {"layout": "All attributes", "subset": "All materials"},
    "Products and parts": {"layout": "All attributes", "subset": "All products and parts"},
    "Specifications": {"layout": "All properties", "subset": "All specifications"},
    "Coatings": {"layout": "All properties", "subset": "All coatings"},
    "Restricted Substances": {"layout": "Restricted substances", "subset": "All substances"},
    "Legislations and Lists": {"layout": "Legislations", "subset": "All legislations"},
    "Locations": {"layout": "All locations", "subset": "All locations"},
    "ProcessUniverse": {"layout": "All processes", "subset": "All processes"},
    "Transport": {"layout": "All transport", "subset": "All transport"},
}
"""
Contains the name of the subset and the layout to be used for each table.

Only attributes in the specified layout and records in the specified subset will be exported into the json data file
provided in DATA_FILENAME.
"""

EXTRA_ATTRIBUTES = {
    # Table name: list[Attribute name]
    "Coatings": ["Coating Code"],
    "Legislations and Lists": ["Legislation ID", "Short title"],
}
"""
Contains additional attributes to be written to DATA_FILENAME if they do not exist within the layout specified in
TABLE_INFORMATION.

This would need to be modified if the BoM Analytics Service requires additional attributes not in a standard layout, or
if an attribute has been added to the default layout. Both scenarios are unlikely.
"""

RENAMED_ATTRIBUTES = {
    # "Table name": {
    #     "Old attribute name": "New attribute name",
    # }
}
"""
Maps old attribute names to new names.

Required if attributes have changed name between database versions. Will generally be different for each release, and
may be empty if no attributes have been renamed.
"""

# ------------------ 2_prepare_rs_db.py ------------------

LAYOUT_TO_PRESERVE = "AttributesToKeep"
"""
Layout which contains the attributes to retain when cleaning the database.

This layout name is referenced in the cleaner XML template.
"""

SUBSET_TO_PRESERVE = "RecordsToKeep"
"""
Subset which contains the records to retain when cleaning the database.

This subset name is referenced in the cleaner XML template.
"""

# ------------------ 3_modify_custom_rs_db.py ------------------

CUSTOM_DB_NAME = "Restricted Substances Custom Tables"
"""Database name for the 'custom table' variant of the Restricted Substances & Sustainability database."""

RS_CUSTOM_TABLE_NAME_MAPPING = {
    # Vanilla table name: Custom table name
    "MaterialUniverse": "My Material Universe",
    "Materials - in house": "My Materials",
    "Specifications": "specs",
    "Products and parts": "Parts 'n' Products",
    "Restricted Substances": "Chemicals",
    "Coatings": "Coverings",
    "Locations": "Places",
    "ProcessUniverse": "Methods",
    "Transport": "Locomotion",
}
"""Table renaming map for creating the 'custom table' variant of the Restricted Substances & Sustainability database."""

# ------------------ 4_create_foreign_database.py ------------------

FOREIGN_DB_NAME = "Restricted Substances Foreign Database"
"""Database name for the foreign database."""

FOREIGN_SCHEMA = {
    # Table name: [Attribute name 1, Attribute name 2, ...]
    "MaterialUniverse, foreign table": ["Material ID", "MaterialUniverse, foreign table, foreign unique attribute"],
    "Materials - in house, foreign table": [
        "Material ID",
        "Materials - in house, foreign table, foreign unique attribute",
    ],
    "ProcessUniverse, foreign table": [
        "Process ID",
        "ProcessUniverse, foreign table, foreign unique attribute",
    ],
    "Restricted Substances, foreign table": [
        "CAS number",
        "EC number",
        "Restricted Substances, foreign table, foreign unique attribute",
    ],
    "Specifications, foreign table": [
        "Specification ID",
        "Specifications, foreign table, foreign unique attribute",
    ],
    "Products and parts, foreign table": [
        "Part number",
        "Products and parts, foreign table, foreign unique attribute",
    ],
    "Locations, foreign table": [
        "Location ID",
        "Locations, foreign table, foreign unique attribute",
    ],
    "Transport, foreign table": [
        "Transport ID",
        "Transport, foreign table, foreign unique attribute",
    ],
}
"""
New tables and attributes to create in the foreign database.

All attributes are assumed to be STXT.
"""

FOREIGN_ATTRIBUTE_STANDARD_NAMES = {
    # Standard name: [(Table name 1: attribute name 1), (Table name 2: attribute name 2), ...]
    "Material ID": [
        ("MaterialUniverse, foreign table", "MaterialUniverse, foreign table, foreign unique attribute"),
        ("Materials - in house, foreign table", "Materials - in house, foreign table, foreign unique attribute"),
    ],
    "CAS number": [
        ("Restricted Substances, foreign table", "CAS number"),
    ],
    "EC number": [
        ("Restricted Substances, foreign table", "EC number"),
    ],
    "Specification ID": [
        ("Specifications, foreign table", "Specifications, foreign table, foreign unique attribute"),
    ],
    "Part number": [
        ("Products and parts, foreign table", "Products and parts, foreign table, foreign unique attribute"),
    ],
    "Identity": [
        ("MaterialUniverse, foreign table", "MaterialUniverse, foreign table, foreign unique attribute"),
        ("Materials - in house, foreign table", "Materials - in house, foreign table, foreign unique attribute"),
        ("ProcessUniverse, foreign table", "ProcessUniverse, foreign table, foreign unique attribute"),
        ("Restricted Substances, foreign table", "CAS number"),
        ("Specifications, foreign table", "Specifications, foreign table, foreign unique attribute"),
        ("Products and parts, foreign table", "Products and parts, foreign table, foreign unique attribute"),
        ("Locations, foreign table", "Locations, foreign table, foreign unique attribute"),
        ("Transport, foreign table", "Transport, foreign table, foreign unique attribute"),
    ],
}
"""Attribute standard naming mapping to create in the foreign database."""

FOREIGN_XDB_LINK_GROUPS = {
    # Link group name: (Source table, Destination table)
    "MaterialUniverseLinkGroup": ("MaterialUniverse, foreign table", "MaterialUniverse"),
    "MaterialInHouseLinkGroup": ("Materials - in house, foreign table", "Materials - in house"),
    "ProcessUniverseLinkGroup": ("ProcessUniverse, foreign table", "ProcessUniverse"),
    "LocationLinkGroup": ("Locations, foreign table", "Locations"),
    "TransportLinkGroup": ("Transport, foreign table", "Transport"),
    "RestrictedSubstancesLinkGroup": ("Restricted Substances, foreign table", "Restricted Substances"),
    "SpecificationsLinkGroup": ("Specifications, foreign table", "Specifications"),
    "ProductsAndPartsLinkGroup": ("Products and parts, foreign table", "Products and parts"),
}
"""
Cross-database record link groups to create between the foreign database and the primary Restricted Substances &
Sustainability database.

Link groups are created with an automatically generated reverse name of "<Link group name> (reverse)".
"""

MI_TRAINING_XDB_LINK_GROUPS = {
    # Link group name: (Source table, Destination table, Reverse name)
    "Equivalent MaterialUniverse record (Metals)": (
        "Design Data",
        "MaterialUniverse",
        "Equivalent Design Data records",
    ),
    "Equivalent MaterialUniverse record (Composites)": (
        "Composite Design Data",
        "MaterialUniverse",
        "Equivalent Composite Design Data records",
    ),
}
"""
Cross-database record link groups to create between the MI Training database and the primary Restricted Substances &
Sustainability database.
"""


LINKING_CRITERIA = {
    # Link group name: (Attribute name, [Attribute value 1, attribute value 2, ...])
    "MaterialUniverseLinkGroup": (
        "Material ID",
        [
            "plastic-abs-pvc-flame",
            "glass-borosilicate-7050",
            "steel-1010-annealed",
            "plastic-pmma-pc",
        ],
    ),
    "MaterialInHouseLinkGroup": (
        "Material ID",
        [
            "Cu_ETP",
            "2345",
        ],
    ),
    "ProcessUniverseLinkGroup": (
        "Process ID",
        [
            "sustainability_casting",
            "sustainability_machining_fine",
            "sustainability_welding_electric",
        ],
    ),
    "LocationLinkGroup": (
        "Location ID",
        [
            "GLO",
            "RER",
            "RAS",
        ],
    ),
    "TransportLinkGroup": (
        "Transport ID",
        [
            "Aircraft, long haul dedicated-freight",
            "Train, diesel",
            "Truck 7.5-16t, EURO 3",
        ],
    ),
    "RestrictedSubstancesLinkGroup": (
        "CAS number",
        [
            "10108-64-2",
            "1306-23-6",
            "7723-14-0",
        ],
    ),
    "SpecificationsLinkGroup": (
        "Specification ID",
        [
            "MIL-DTL-53039,TypeI",
            "MIL-A-8625,TypeIII,Class1",
            "AMS2404,Class1",
        ],
    ),
    "ProductsAndPartsLinkGroup": (
        "Part number",
        [
            "EX-1678",
            "DRILL",
            "asm_flap_mating",
        ],
    ),
}
"""
Link creation definitions for attribute-based linking between foreign and primary records.

The primary record is identified by finding the record with the attribute value populated for the specified attribute
name.
"""


GUID_LINKING_CRITERIA = {
    # Link group name: (Local history GUID, Foreign history GUID)
    "Equivalent MaterialUniverse record (Metals)": [
        (
            "5b1df472-a92e-4317-b9a8-e1672335bc2e",  # AMS 6250 Plate
            "d0237d48-ddd2-4916-b24c-86ba51f25b52",  # 250, maraged
        ),
        (
            "ce294339-e59d-4be1-a96c-f9e92adb71ac",  # Inconel 718, Forging
            "b7ff507a-80c9-48ab-b489-4dc5663e57c1",  # Inconel 718 solution treated
        ),
    ],
    "Equivalent MaterialUniverse record (Composites)": [
        (
            "5f9563c4-17f8-4ed9-ae43-d48f025d9ce5",  # CTD
            "a1adca06-ddcb-4f64-a686-3bb4d38e16ed",  # UD lay-up
        ),
        (
            "e5b404b3-3b41-4a3b-810b-573289c0fe76",  # ETD
            "a1adca06-ddcb-4f64-a686-3bb4d38e16ed",  # UD lay-up
        ),
        (
            "358fe02d-eca6-421f-898d-82894ec823bb",  # ETW 150F
            "a1adca06-ddcb-4f64-a686-3bb4d38e16ed",  # UD lay-up
        ),
        (
            "bec85b53-e111-4144-b43c-55b6504c76ee",  # ETW 180F
            "a1adca06-ddcb-4f64-a686-3bb4d38e16ed",  # UD lay-up
        ),
        (
            "5d7f34bf-e2db-413e-9407-a3a03aa3878f",  # RTD
            "a1adca06-ddcb-4f64-a686-3bb4d38e16ed",  # UD lay-up
        ),
    ],
}
"""
Link creation definitions with which to link foreign and primary records, based on record GUIDs.

The primary and foreign records are identified directly by their record history GUIDs.
"""
