"""
get_cleaned_db_entries.py
-------------------------

This script is the first step in the process for updating the test databases. It extracts the attributes and records
from a current version into a format that can be used to generate an updated version.

Set the value of MI_URL and DB_KEY as appropriate for your setup, the values of table_information, extra_attributes,
and renamed_attributes should be OK for the current release.

table_information
=================

table_information contains the name of the subset and the layout to be used. Attributes in the layout specified, and
records in the subset specified, will be exported into the json data file

extra_attributes
================

extra_attributes contains any attributes that should be copied across if they do not exist within the specified layout.

renamed_attributes
==================

renamed_attributes contains a map of old name to new name for any attributes that have changed name between the current
version of the database and the new version.
"""

import json
import logging
from pathlib import Path

from GRANTA_MIScriptingToolkit import granta as mpy
from ansys.grantami.serverapi_openapi import api, models
from ansys.openapi.common import Unset

from cicd.connection import Connection

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)

MI_URL = "http://localhost/mi_servicelayer"
DB_KEY = "MI_Restricted_Substances"
OUTPUT_FILE_NAME = Path("./rs_data.json").resolve()

logger.info(f"Connecting to MI at {MI_URL} with AutoLogon")
s = mpy.Session(MI_URL, autologon=True)
db = s.get_db(db_key=DB_KEY)
api_client = Connection(api_url=MI_URL).with_autologon().connect()

tables_api = api.SchemaTablesApi(api_client)
attributes_api = api.SchemaAttributesApi(api_client)
layouts_api = api.SchemaLayoutsApi(api_client)
layout_sections_api = api.SchemaLayoutSectionsApi(api_client)

table_information = {
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
extra_attributes = {"Coatings": ["Coating Code"], "Legislations and Lists": ["Legislation ID", "Short title"]}

# Will generally be different for each release, and may be empty.
# dict[Table name: dict[Current attribute name: New attribute name]]
renamed_attributes = {"Products and parts": {"General comments": "Comments"}}

info = {}
logger.info(f"Reading records and attributes from database '{DB_KEY}'")
logger.info("Getting Table Information")
tables = tables_api.get_tables(database_key=DB_KEY)
table_name_map = {table.name: table for table in tables.tables}
for table_name, table_details in table_information.items():
    logger.info(f"--Processing table '{table_name}'")
    table = db.get_table(table_name)
    layout_name = table_details["layout"]
    subset_name = table_details["subset"]
    logger.info(f"----Fetching attributes in layout '{layout_name}")
    renamed_attributes_for_table = renamed_attributes.get(table_name, [])
    table_info = table_name_map[table_name]
    table_layouts = layouts_api.get_layouts(database_key=DB_KEY, table_guid=table_info.guid)
    layout_map = {layout.name: layout for layout in table_layouts.layouts}
    layout_item = layout_map[layout_name]
    sections_response = layout_sections_api.get_layout_sections(
        database_key=DB_KEY, table_guid=table_info.guid, layout_guid=layout_item.guid, show_full_detail=True
    )
    layout_info = [section.to_dict() for section in sections_response.layout_sections if section.section_items]
    if table_name in extra_attributes:
        # Add extra attribute information to a section in the layout
        table_attributes = attributes_api.get_attributes(database_key=DB_KEY, table_guid=table_info.guid)
        attribute_name_map = {attribute.name: attribute for attribute in table_attributes.attributes}
        added_items = []
        relevant_attribute_names = extra_attributes[table_name]
        for extra_attribute_name in relevant_attribute_names:
            attribute_info = attribute_name_map[extra_attribute_name]
            added_items.append(
                models.GrantaServerApiSchemaLayoutsLayoutAttributeItem(
                    attribute_type=attribute_info.type,
                    underlying_entity_guid=attribute_info.guid,
                    name=attribute_info.name,
                    meta_attributes=[],
                    tabular_columns=None,
                    read_only=False,
                    required=False,
                    guid="",
                )
            )
        layout_info.append(
            models.GrantaServerApiSchemaLayoutsFullLayoutSection(
                name="Extra Attributes",
                section_items=added_items,
                display_names={},
                guid="",
            ).to_dict()
        )
    if len(renamed_attributes_for_table) > 0:
        logger.info(f"----Remapping attribute names")
        for section in layout_info:
            for item in section["section_items"]:
                if item["name"] in renamed_attributes_for_table:
                    new_name = renamed_attributes_for_table[item["name"]]
                    logger.info(f"------Renaming attribute '{item['name']}' to '{new_name}'")
                    item["name"] = renamed_attributes_for_table[item["name"]]
                if "tabular_columns" in item and item["tabular_columns"] is not Unset:
                    for column in item["tabular_columns"]:
                        if column["name"] in renamed_attributes_for_table:
                            new_name = renamed_attributes_for_table[column["name"]]
                            logger.info(
                                f"------Renaming tabular column '{column['name']}' to '{new_name}' in attribute '{item['name']}'"  # noqa: E501
                            )
                            column["name"] = renamed_attributes_for_table[column["name"]]
    logger.info(f"----Fetching records in subset '{subset_name}'")
    records = [
        (record.history_guid, record.record_guid)
        for record in table.all_records(include_folders=True, include_generics=True)
    ]
    info[table_name] = {"layout": layout_info, "records": records}


def serialize_unset(obj):
    if obj is Unset:
        return None


logger.info(f"Finished processing data, writing to {OUTPUT_FILE_NAME}")
with open(OUTPUT_FILE_NAME, "w", encoding="utf8") as fp:
    json.dump(info, fp, default=serialize_unset)
