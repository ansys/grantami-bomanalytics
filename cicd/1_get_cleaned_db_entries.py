"""
This script is the first step in the process for updating the test databases. It extracts the attributes and records
from a current version into a format that can be used to generate an updated version. This format is written to a file
with the name DATA_FILENAME.

Configuration is stored in _config.py. Set the value of MI_URL and RS_DB_KEY_PREVIOUS as appropriate for your setup. For
this script, RS_DB_KEY_PREVIOUS should refer to the most recent PyGranta BoM Analytics RS test database currently used
in CI.

The values of TABLE_INFORMATION, EXTRA_ATTRIBUTES, and RENAMED_ATTRIBUTES may need to be modified depending on the
changes made to the Restricted Substances & Sustainability database.
"""

import json
import logging
from pathlib import Path

from GRANTA_MIScriptingToolkit import granta as mpy
from ansys.grantami.serverapi_openapi.v2025r2 import api, models
from ansys.openapi.common import Unset

from cicd._connection import Connection
from cicd._config import (
    MI_URL,
    RS_DB_KEY_CURRENT,
    DATA_FILENAME,
    TABLE_INFORMATION,
    EXTRA_ATTRIBUTES,
    RENAMED_ATTRIBUTES,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)

logger.info(f"Connecting to MI at {MI_URL} with AutoLogon")
s = mpy.Session(MI_URL, autologon=True)
db = s.get_db(db_key=RS_DB_KEY_CURRENT)
api_client = Connection(api_url=MI_URL).with_autologon().connect()

tables_api = api.SchemaTablesApi(api_client)
attributes_api = api.SchemaAttributesApi(api_client)
layouts_api = api.SchemaLayoutsApi(api_client)
layout_sections_api = api.SchemaLayoutSectionsApi(api_client)

info = {}
logger.info(f"Reading records and attributes from database '{RS_DB_KEY_CURRENT}'")
logger.info("Getting Table Information")
tables = tables_api.get_tables(database_key=RS_DB_KEY_CURRENT)
table_name_map = {table.name: table for table in tables.tables}
for table_name, table_details in TABLE_INFORMATION.items():
    logger.info(f"--Processing table '{table_name}'")
    table = db.get_table(table_name)
    layout_name = table_details["layout"]
    subset_name = table_details["subset"]
    logger.info(f"----Fetching attributes in layout '{layout_name}")
    renamed_attributes_for_table = RENAMED_ATTRIBUTES.get(table_name, [])
    table_info = table_name_map[table_name]
    table_layouts = layouts_api.get_layouts(database_key=RS_DB_KEY_CURRENT, table_guid=table_info.guid)
    layout_map = {layout.name: layout for layout in table_layouts.layouts}
    layout_item = layout_map[layout_name]
    sections_response = layout_sections_api.get_layout_sections(
        database_key=RS_DB_KEY_CURRENT, table_guid=table_info.guid, layout_guid=layout_item.guid, show_full_detail=True
    )
    layout_info = [section.to_dict() for section in sections_response.layout_sections if section.section_items]
    if table_name in EXTRA_ATTRIBUTES:
        # Add extra attribute information to a section in the layout
        table_attributes = attributes_api.get_attributes(database_key=RS_DB_KEY_CURRENT, table_guid=table_info.guid)
        attribute_name_map = {attribute.name: attribute for attribute in table_attributes.attributes}
        added_items = []
        relevant_attribute_names = EXTRA_ATTRIBUTES[table_name]
        for extra_attribute_name in relevant_attribute_names:
            attribute_info = attribute_name_map[extra_attribute_name]
            added_items.append(
                models.GsaLayoutAttributeItem(
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
            models.GsaFullLayoutSection(
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


OUTPUT_FILE_NAME = Path(__file__).parent / DATA_FILENAME
OUTPUT_FILE_NAME.resolve()
logger.info(f"Finished processing data, writing to {OUTPUT_FILE_NAME}")
with open(OUTPUT_FILE_NAME, "w", encoding="utf8") as fp:
    json.dump(info, fp, default=serialize_unset)
