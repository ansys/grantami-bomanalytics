from ansys.grantami.bomanalytics import indicators

LEGISLATIONS = ["The SIN List 2.1 (Substitute It Now!)", "Canadian Chemical Challenge"]

two_legislation_indicator = indicators.WatchListIndicator(
    name="Two legislations",
    legislation_names=["GADSL", "California Proposition 65 List"],
    default_threshold_percentage=2,
)
one_legislation_indicator = indicators.RoHSIndicator(
    name="One legislation",
    legislation_names=["EU Directive 2011/65/EU (RoHS 2)"],
    default_threshold_percentage=0.01,
)

INDICATORS = {"Two legislations": two_legislation_indicator, "One legislation": one_legislation_indicator}

CUSTOM_TABLES = [
    ("material_universe_table_name", "My Material Universe"),
    ("in_house_materials_table_name", "My Materials"),
    ("specifications_table_name", "specs"),
    ("products_and_parts_table_name", "Parts 'n' Products"),
    ("substances_table_name", "Chemicals"),
    ("coatings_table_name", "Coverings"),
]
