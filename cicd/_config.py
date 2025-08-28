MI_URL = "http://localhost/mi_servicelayer"
DB_KEY = "MI_Restricted_Substances"

DATA_FILENAME = "rs_data.json"

LAYOUT_TO_PRESERVE = "AttributesToKeep"
SUBSET_TO_PRESERVE = "RecordsToKeep"

RS_DB_KEY = "MI_Restricted_Substances"
CUSTOM_DB_KEY = "MI_Restricted_Substances_Custom_Tables"
FOREIGN_DB_KEY = "MI_Restricted_Substances_Foreign"

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

FOREIGN_RS_LINK_GROUPS = {
    # Link group name: (Source table, Destination table)
    "MaterialUniverseLinkGroup": ("MaterialUniverse", "MaterialUniverse, foreign table"),
    "MaterialInHouseLinkGroup": ("Materials - in house", "Materials - in house, foreign table"),
    "ProcessUniverseLinkGroup": ("ProcessUniverse", "ProcessUniverse, foreign table"),
    "LocationLinkGroup": ("Locations", "Locations, foreign table"),
    "TransportLinkGroup": ("Transport", "Transport, foreign table"),
    "LegislationsLinkGroup": ("Legislations and Lists", "Legislations and Lists, foreign table"),
    "RestrictedSubstancesLinkGroup": ("Restricted Substances", "Restricted Substances, foreign table"),
    "SpecificationsLinkGroup": ("Specifications", "Specifications, foreign table"),
    "ProductsAndPartsLinkGroup": ("Products and parts", "Products and parts, foreign table"),
}

RS_UNIQUE_ID_STANDARD_NAMES = {
    "MaterialUniverse": ["Material ID"],
    "Materials - in house": ["Material ID"],
    "Legislations and Lists": ["Legislation ID"],
    "Restricted Substances": ["CAS number", "EC number"],
    "Specifications": ["Specification ID"],
    "Products and parts": ["Part number"],
}


FOREIGN_RS_LINKS = {
    # Link group name: Attribute name, Record ID
    "MaterialUniverseLinkGroup": ("Material ID", "plastic-abs-pvc-flame"),
}
