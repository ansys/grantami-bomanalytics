# General configuration

MI_URL = "http://localhost/mi_servicelayer"
RS_DB_KEY = "MI_Restricted_Substances"
CUSTOM_DB_KEY = "MI_Restricted_Substances_Custom_Tables"
FOREIGN_DB_KEY = "MI_Restricted_Substances_Foreign"

DATA_FILENAME = "rs_data.json"

# 1_get_cleaned_db_entries.py

TABLE_INFORMATION = {
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

# Generally static unless the BoM Analytics Servers logic has changed, or these attributes have been added to the layout
# Both of these scenarios are unlikely
# dict[Table name: list[Attribute name]]
EXTRA_ATTRIBUTES = {
    "Coatings": ["Coating Code"],
    "Legislations and Lists": ["Legislation ID", "Short title"],
}

# Will generally be different for each release, and may be empty.
RENAMED_ATTRIBUTES = {
    # "Table name": {
    #     "Old attribute name": "New attribute name",
    # }
}

# 2_prepare_rs_db.py

# The layout and subset name must be consistent with the cleaner template
LAYOUT_TO_PRESERVE = "AttributesToKeep"
SUBSET_TO_PRESERVE = "RecordsToKeep"


# 3_modify_custom_rs_db.py

RS_CUSTOM_TABLE_NAME_MAPPING = {
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


# 4_create_foreign_database.py

FOREIGN_DB_NAME = "Restricted Substances Foreign Database"

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
    "Legislations and Lists, foreign table": [
        "Legislation ID",
        "Legislations and Lists, foreign table, foreign unique attribute",
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

FOREIGN_ATTRIBUTE_STANDARD_NAMES = {
    # Standard name: [(Table name 1: attribute name 1), (Table name 2: attribute name 2), ...]
    "Material ID": [
        ("MaterialUniverse, foreign table", "Material ID"),
        ("Materials - in house, foreign table", "Material ID"),
    ],
    "Legislation ID": [
        ("Legislations and Lists, foreign table", "Legislation ID"),
    ],
    "CAS number": [
        ("Restricted Substances, foreign table", "CAS number"),
    ],
    "EC number": [
        ("Restricted Substances, foreign table", "EC number"),
    ],
    "Specifications ID": [
        ("Specifications, foreign table", "Specification ID"),
    ],
    "Part number": [
        ("Products and parts, foreign table", "Part number"),
    ],
    "Identity": [
        ("MaterialUniverse, foreign table", "Material ID"),
        ("Materials - in house, foreign table", "Material ID"),
        ("ProcessUniverse, foreign table", "Process ID"),
        ("Legislations and Lists, foreign table", "Legislation ID"),
        ("Restricted Substances, foreign table", "CAS number"),
        ("Specifications, foreign table", "Specification ID"),
        ("Products and parts, foreign table", "Part number"),
        ("Locations, foreign table", "Location ID"),
        ("Transport, foreign table", "Transport ID"),
    ],
}


FOREIGN_XDB_LINK_GROUPS = {
    # Link group name: (Source table, Destination table)
    "MaterialUniverseLinkGroup": ("MaterialUniverse, foreign table", "MaterialUniverse"),
    "MaterialInHouseLinkGroup": ("Materials - in house, foreign table", "Materials - in house"),
    "ProcessUniverseLinkGroup": ("ProcessUniverse, foreign table", "ProcessUniverse"),
    "LocationLinkGroup": ("Locations, foreign table", "Locations"),
    "TransportLinkGroup": ("Transport, foreign table", "Transport"),
    "LegislationsLinkGroup": ("Legislations and Lists, foreign table", "Legislations and Lists"),
    "RestrictedSubstancesLinkGroup": ("Restricted Substances, foreign table", "Restricted Substances"),
    "SpecificationsLinkGroup": ("Specifications, foreign table", "Specifications"),
    "ProductsAndPartsLinkGroup": ("Products and parts, foreign table", "Products and parts"),
}


LINKING_CRITERIA = {
    # Link group name: (Attribute name, [Attribute value 1, attribute value 2, ...])
    "MaterialUniverseLinkGroup": (
        "Material ID",
        [
            "plastic-abs-pvc-flame",
            "glass-borosilicate-7050",
            "steel-1010-annealed",
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
    "LegislationsLinkGroup": (
        "Legislation ID",
        [
            "Candidate_AnnexXV",
            "Prop65",
            "SINList",
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
