"""
create_foreign_database.py
-------------------------

This script is the fourth step in creating new test databases. It populates a blank database to serve as a foreign
database, which references records in a main RS database.

It performs the following steps:

1. Sets the database name
2. Creates tables and attributes
3. Creates standard names for attributes
4. Creates cross-database record link groups, and adds rlg standard names
5. Creates records, populates attributes, and creates links

Configuration is stored in _config.py.
"""

import logging
from collections import defaultdict
from typing import Mapping, Sequence

from ansys.grantami.serverapi_openapi.v2025r2 import api, models
from GRANTA_MIScriptingToolkit import granta as mpy

from cicd._connection import Connection
from cicd._config import (
    MI_URL,
    RS_DB_KEY,
    FOREIGN_DB_KEY,
    FOREIGN_XDB_LINK_GROUPS,
    FOREIGN_ATTRIBUTE_STANDARD_NAMES,
    FOREIGN_SCHEMA,
    LINKING_CRITERIA,
    FOREIGN_DB_NAME,
)
from cicd._utils import DatabaseBrowser

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)


def ensure_table_exists_with_attributes(
    db_key: str,
    table_name: str,
    attribute_names: Sequence[str],
) -> Mapping[str, str]:
    """
    Check if the provided table name exists within the database, and if the attribute names provided exist in that
    table.

    If the table does not exist, create it.

    If the attributes do not exist, create them as short-text attributes.

    Return a mapping of attribute names to attribute GUIDs.
    """

    _database_browser = DatabaseBrowser(api_client, logger)
    table_name_to_guid_map = _database_browser.get_table_name_guid_map(db_key)

    table_client = api.SchemaTablesApi(api_client)
    attribute_client = api.SchemaAttributesApi(api_client)

    logger.info(f"  Checking {table_name}...")
    if table_name in table_name_to_guid_map:
        table_guid = table_name_to_guid_map[table_name]
        logger.info(f"  {table_name} already exists with guid {table_guid}")
    else:
        logger.info(f"  {table_name} does not exist. Creating...")
        resp = table_client.create_table(
            database_key=db_key,
            body=models.GsaCreateTable(
                name=table_name,
                is_hidden_from_browse=False,
                is_hidden_from_search=False,
            ),
        )
        table_guid = resp.guid
        logger.info(f"  Created {table_name} with GUID {table_guid}")

    logger.info(f"  Ensuring attributes exist for table {table_name}")
    attribute_resp = attribute_client.get_attributes(
        database_key=db_key,
        table_guid=table_guid,
    )
    guid_map = {a.name: a.guid for a in attribute_resp.attributes}

    for attribute_name in attribute_names:
        if attribute_name in guid_map:
            logger.info(f"    Attribute {attribute_name} found with guid {guid_map[attribute_name]}")
        else:
            logger.info(f"    Attribute {attribute_name} not found. Creating...")
            resp = attribute_client.create_attribute(
                database_key=db_key,
                table_guid=table_guid,
                body=models.GsaCreateAttribute(
                    name=attribute_name,
                    type=models.GsaAttributeType.SHORTTEXT,
                ),
            )
            guid_map[attribute_name] = resp.guid
    return guid_map


def ensure_link_group_exists(
    name: str,
    db_key: str,
    source_table_guid: str,
    target_db_key: str,
    target_table_guid: str,
) -> str:
    """
    Check if the provided record link group name exists within the database with the provided table name as the source
    table.

    If the link group does not exist, create it as a cross-database record link group between the source table and
    destination table, and return the GUID.
    """
    logger.info(f"  Checking {name}")

    _database_browser = DatabaseBrowser(api_client, logger)

    rlg_client = api.SchemaRecordLinkGroupsApi(api_client)

    rlgs = rlg_client.get_record_link_groups(database_key=db_key, table_guid=source_table_guid)
    for rlg in rlgs.record_link_groups:
        if rlg.name == name:
            logger.info(f"  Link group already exists")
            return rlg.guid

    logger.info(f"  Link group not found. Creating.")
    target_db_guid = _database_browser.get_database_guid(target_db_key)
    create_response = rlg_client.create_record_link_group(
        database_key=db_key,
        table_guid=source_table_guid,
        body=models.GsaCreateRecordLinkGroup(
            link_target=models.GsaLinkTarget(
                database_guid=target_db_guid,
                table_guid=target_table_guid,
            ),
            name=link_name,
            reverse_name=f"{link_name} (reverse)",
            type=models.GsaRecordLinkGroupType.CROSSDATABASE,
        ),
    )
    return create_response.guid


def add_attribute_value_to_record(record: mpy.Record, attribute_name: str, attribute_value: str) -> None:
    """Populate a streamlined layer attribute."""
    logger.info(f"    Setting attribute '{attribute_name}' to value '{attribute_value}'")
    attribute = record.attributes[attribute_name]
    attribute.value = attribute_value
    record.set_attributes([attribute])


def add_links_to_record(record: mpy.Record, link_group_name: str, link_records: list[mpy.Record]) -> None:
    """Add links to a record link group."""
    logger.info(f"    Adding links to record link group {link_group_name}")
    record.set_links(link_name=link_group_name, records=link_records)


if __name__ == "__main__":
    api_client = Connection(api_url=MI_URL).with_autologon().connect()
    database_browser = DatabaseBrowser(api_client, logger)

    # ----------------- Clean up ------------------------------------------------------

    database_browser.delete_all_standard_names(FOREIGN_DB_KEY)

    # ------------------ Set database name --------------------------

    database_browser.update_database_name(FOREIGN_DB_KEY, FOREIGN_DB_NAME)

    # ------------------ Create tables and attributes --------------------------

    logger.info("Ensuring tables exist in the foreign database")
    foreign_table_name_to_attribute_name_to_guid_map: dict[str, Mapping[str, str]] = defaultdict(dict)
    for foreign_table_name, foreign_attribute_names in FOREIGN_SCHEMA.items():
        attribute_name_to_guid_map = ensure_table_exists_with_attributes(
            db_key=FOREIGN_DB_KEY,
            table_name=foreign_table_name,
            attribute_names=foreign_attribute_names,
        )
        foreign_table_name_to_attribute_name_to_guid_map[foreign_table_name] = attribute_name_to_guid_map

    # ------------------ Create attribute standard names --------------------------

    logger.info(f"Creating attribute standard names...")
    for foreign_standard_name, mappings in FOREIGN_ATTRIBUTE_STANDARD_NAMES.items():
        attribute_guids = [
            foreign_table_name_to_attribute_name_to_guid_map[table_name][attribute_name]
            for (table_name, attribute_name) in mappings
        ]
        database_browser.create_standard_name(
            db_key=FOREIGN_DB_KEY,
            name=foreign_standard_name,
            mapped_attribute_guids=attribute_guids,
        )

    # ------------------ Record link groups --------------------------

    logger.info("Ensuring record link groups exist between primary and foreign databases")
    xdb_link_group_guids = []

    foreign_table_guids = database_browser.get_table_name_guid_map(FOREIGN_DB_KEY)
    rs_table_guids = database_browser.get_table_name_guid_map(RS_DB_KEY)

    for link_name, (foreign_table_name, rs_table_name) in FOREIGN_XDB_LINK_GROUPS.items():
        new_guid = ensure_link_group_exists(
            name=link_name,
            db_key=FOREIGN_DB_KEY,
            source_table_guid=foreign_table_guids[foreign_table_name],
            target_db_key=RS_DB_KEY,
            target_table_guid=rs_table_guids[rs_table_name],
        )
        xdb_link_group_guids.append(new_guid)

    logger.info("Creating new cross-database record link group standard name")
    database_browser.create_standard_name(
        db_key=FOREIGN_DB_KEY,
        name="Granta record for analysis 1",
        mapped_cross_database_record_link_group_guids=xdb_link_group_guids,
    )

    # ------------------ Foreign record creation and population --------------------------

    streamlined_session = mpy.Session(service_layer_url=MI_URL, autologon=True)

    logger.info("Creating and link foreign records")
    records_to_update = []

    for xdb_rlg_name, (attribute_name, unique_ids) in LINKING_CRITERIA.items():
        foreign_table_name, rs_table_name = FOREIGN_XDB_LINK_GROUPS[xdb_rlg_name]

        for unique_id in unique_ids:
            foreign_guid = database_browser.ensure_record_exists_with_name(
                db_key=FOREIGN_DB_KEY,
                table_name=foreign_table_name,
                record_name=unique_id,
            )
            foreign_record = streamlined_session.get_db(db_key=FOREIGN_DB_KEY).get_record_by_id(hguid=foreign_guid)
            rs_record = (
                streamlined_session.get_db(db_key=RS_DB_KEY)
                .get_table(name=rs_table_name)
                .get_record_by_lookup_value(
                    attribute_name=attribute_name,
                    lookup_value=unique_id,
                )
            )

            add_attribute_value_to_record(
                record=foreign_record,
                attribute_name=attribute_name,
                attribute_value=unique_id,
            )
            standalone_attribute_name = f"{foreign_table_name}, foreign unique attribute"
            standalone_attribute_value = f"{unique_id}-foreign"
            add_attribute_value_to_record(
                record=foreign_record,
                attribute_name=standalone_attribute_name,
                attribute_value=standalone_attribute_value,
            )
            add_links_to_record(
                record=foreign_record,
                link_group_name=xdb_rlg_name,
                link_records=[rs_record],
            )
            records_to_update.append(foreign_record)

    streamlined_session.update(
        records_to_update,
        update_attributes=True,
        update_links=True,
    )
