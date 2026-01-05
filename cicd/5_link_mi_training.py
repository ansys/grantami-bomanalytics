import logging

from GRANTA_MIScriptingToolkit import granta as mpy

from cicd._connection import Connection
from cicd._config import (
    MI_URL,
    RS_DB_KEY_CURRENT,
    MI_TRAINING_DB_KEY,
    MI_TRAINING_XDB_LINK_GROUPS,
    GUID_LINKING_CRITERIA,
)
from cicd._utils import DatabaseBrowser, ensure_link_group_exists

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)


def add_links_to_record(record: mpy.Record, link_group_name: str, link_records: list[mpy.Record]) -> None:
    """Add links to a record link group."""
    logger.info(f"    Adding links to record link group {link_group_name}")
    record.set_links(link_name=link_group_name, records=link_records)


if __name__ == "__main__":
    api_client = Connection(api_url=MI_URL).with_autologon().connect()
    database_browser = DatabaseBrowser(api_client, logger)

    mi_training_guid = database_browser.get_database_guid(MI_TRAINING_DB_KEY)

    # ------------------ Record link groups --------------------------

    logger.info("Ensuring record link groups exist between RS and MI Training database")
    xdb_link_group_guids = []

    mi_training_table_guids = database_browser.get_table_name_guid_map(MI_TRAINING_DB_KEY)
    rs_table_guids = database_browser.get_table_name_guid_map(RS_DB_KEY_CURRENT)

    for link_name, (mi_training_table_name, rs_table_name, reverse_link_name) in MI_TRAINING_XDB_LINK_GROUPS.items():
        new_guid = ensure_link_group_exists(
            api_client=api_client,
            name=link_name,
            reverse_name=reverse_link_name,
            db_key=MI_TRAINING_DB_KEY,
            source_table_guid=mi_training_table_guids[mi_training_table_name],
            target_db_key=RS_DB_KEY_CURRENT,
            target_table_guid=rs_table_guids[rs_table_name],
        )
        xdb_link_group_guids.append(new_guid)

    logger.info("Creating new cross-database record link group standard name")
    database_browser.create_standard_name(
        db_key=MI_TRAINING_DB_KEY,
        name="RS and Sustainability record",
        mapped_cross_database_record_link_group_guids=xdb_link_group_guids,
    )

    # ------------------ Link creation --------------------------

    streamlined_session = mpy.Session(service_layer_url=MI_URL, autologon=True)

    logger.info("Creating and linking foreign records")
    records_to_update = []

    for xdb_rlg_name, guids in GUID_LINKING_CRITERIA.items():
        for primary_guid, foreign_guid in guids:
            foreign_table_name, rs_table_name, _ = MI_TRAINING_XDB_LINK_GROUPS[xdb_rlg_name]

            primary_record = streamlined_session.get_db(db_key=MI_TRAINING_DB_KEY).get_record_by_id(hguid=primary_guid)
            foreign_record = (
                streamlined_session.get_db(db_key=RS_DB_KEY_CURRENT)
                .get_table(name=rs_table_name)
                .get_record_by_id(hguid=foreign_guid)
            )

            add_links_to_record(primary_record, xdb_rlg_name, [foreign_record])
            records_to_update.append(primary_record)

    streamlined_session.update_links(records_to_update)
