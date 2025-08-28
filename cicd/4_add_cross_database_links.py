import logging
from collections import defaultdict

from ansys.grantami.serverapi_openapi.v2025r2 import api, models

from cicd._connection import Connection
from cicd._config import (
    MI_URL,
    RS_DB_KEY,
    FOREIGN_DB_KEY,
    FOREIGN_RS_LINK_GROUPS,
    RS_UNIQUE_ID_STANDARD_NAMES,
    FOREIGN_RS_LINKS,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)

if __name__ == "__main__":
    api_client = Connection(api_url=MI_URL).with_autologon().connect()

    database_client = api.SchemaDatabasesApi(api_client)
    table_client = api.SchemaTablesApi(api_client)
    attribute_client = api.SchemaAttributesApi(api_client)
    rlg_client = api.SchemaRecordLinkGroupsApi(api_client)
    std_name_client = api.SchemaStandardNamesApi(api_client)
    record_client = api.RecordsRecordHistoriesApi(api_client)
    data_client = api.DataApi(api_client)

    logger.info("Setting foreign database name")
    database_client.update_database(
        database_key=FOREIGN_DB_KEY,
        body=models.GsaUpdateDatabase(
            name="Restricted Substances Foreign Database",
        ),
    )

    logger.info("Deleting existing standard names in foreign database")
    std_name_resp = std_name_client.get_standard_names(database_key=FOREIGN_DB_KEY)
    for standard_name in std_name_resp.standard_names:
        std_name_client.delete_standard_name(
            database_key=FOREIGN_DB_KEY,
            standard_name_guid=standard_name.guid,
        )

    logger.info("Ensuring tables exist in the foreign database")
    foreign_db_guid = database_client.get_database(database_key=FOREIGN_DB_KEY).guid
    foreign_tables = table_client.get_tables(database_key=FOREIGN_DB_KEY)
    foreign_tables = {t.name: t.guid for t in foreign_tables.tables}

    attribute_guids = defaultdict(dict)

    std_names_to_create = defaultdict(list)

    for rs_table_name, foreign_table_name in FOREIGN_RS_LINK_GROUPS.values():
        logger.info(f"  Checking {foreign_table_name}...")
        if foreign_table_name in foreign_tables:
            logger.info(f"  {foreign_table_name} exists with GUID {foreign_tables[foreign_table_name]}")

        else:
            logger.info(f"  {foreign_table_name} does not exist.")
            resp = table_client.create_table(
                database_key=FOREIGN_DB_KEY,
                body=models.GsaCreateTable(
                    name=foreign_table_name,
                    is_hidden_from_browse=False,
                    is_hidden_from_search=False,
                ),
            )
            foreign_tables[foreign_table_name] = resp.guid
            logger.info(f"  Created {foreign_table_name} with GUID {foreign_tables[foreign_table_name]}")

        table_guid = foreign_tables[foreign_table_name]

        logger.info(f"  Ensuring attributes exist for table {foreign_table_name}")
        attribute_resp = attribute_client.get_attributes(
            database_key=FOREIGN_DB_KEY,
            table_guid=table_guid,
        )
        attribute_guids[foreign_table_name] = {a.name: a.guid for a in attribute_resp.attributes}

        foreign_unique_id_attr_name = f"{foreign_table_name} standalone unique attribute"
        if foreign_unique_id_attr_name not in attribute_guids[foreign_table_name]:
            logger.info(f"    Attribute {foreign_unique_id_attr_name} not found. Creating...")
            resp = attribute_client.create_attribute(
                database_key=FOREIGN_DB_KEY,
                table_guid=table_guid,
                body=models.GsaCreateAttribute(
                    name=foreign_unique_id_attr_name,
                    type=models.GsaAttributeType.SHORTTEXT,
                ),
            )
            attribute_guids[foreign_table_name][foreign_unique_id_attr_name] = resp.guid

        for rs_attribute in RS_UNIQUE_ID_STANDARD_NAMES.get(rs_table_name, []):
            if rs_attribute not in attribute_guids[foreign_table_name]:
                logger.info(f"    Attribute {rs_attribute} not found. Creating...")
                create_attr_resp = attribute_client.create_attribute(
                    database_key=FOREIGN_DB_KEY,
                    table_guid=table_guid,
                    body=models.GsaCreateAttribute(
                        name=f"{rs_attribute}",
                        type=models.GsaAttributeType.SHORTTEXT,
                    ),
                )
                attribute_guids[foreign_table_name][rs_attribute] = create_attr_resp.guid
                std_names_to_create[rs_attribute].append(attribute_guids[foreign_table_name][rs_attribute])

    logger.info(f"Creating missing standard names...")
    for std_name, guids in std_names_to_create.items():
        logger.info(f"  Creating {std_name}")
        std_name_client.create_standard_name(
            database_key=FOREIGN_DB_KEY,
            body=models.GsaCreateStandardName(
                name=std_name, mapped_attributes=[models.GsaSlimEntity(guid=guid) for guid in guids]
            ),
        )

    logger.info("Ensuring record link groups exist between primary and foreign databases")
    rs_tables = table_client.get_tables(database_key=RS_DB_KEY)
    rs_table_guids = {t.name: t.guid for t in rs_tables.tables}

    link_mapping = {}

    for link_name, (source_table_name, dest_table_name) in FOREIGN_RS_LINK_GROUPS.items():
        logger.info(f"  Checking {link_name}")

        source_table_guid = rs_table_guids[source_table_name]
        dest_table_guid = foreign_tables[dest_table_name]

        rlgs = rlg_client.get_record_link_groups(
            database_key=RS_DB_KEY,
            table_guid=source_table_guid,
        )
        for rlg in rlgs.record_link_groups:
            if rlg.name == link_name:
                logger.info(f"  Link already exists")
                link_mapping[rlg.name] = rlg.guid
                break

        if link_name in link_mapping:
            continue

        logger.info(f"  Link not found. Creating.")
        create_response = rlg_client.create_record_link_group(
            database_key=RS_DB_KEY,
            table_guid=source_table_guid,
            body=models.GsaCreateRecordLinkGroup(
                link_target=models.GsaLinkTarget(
                    database_guid=foreign_db_guid,
                    table_guid=dest_table_guid,
                ),
                name=link_name,
                reverse_name=f"{link_name} (reverse)",
                type=models.GsaRecordLinkGroupType.CROSSDATABASE,
            ),
        )
        link_mapping[link_name] = create_response.guid

    logger.info("Deleting existing xdb standard name")
    std_name_resp = std_name_client.get_standard_names(database_key=RS_DB_KEY)
    try:
        xdb_std_name_guid = next(
            n.guid for n in std_name_resp.standard_names if n.name == "Granta record for analysis 1"
        )
        std_name_client.delete_standard_name(
            database_key=RS_DB_KEY,
            standard_name_guid=xdb_std_name_guid,
        )
    except StopIteration:
        pass

    logger.info("Creating new xdb standard name")
    std_name_client.create_standard_name(
        database_key=RS_DB_KEY,
        body=models.GsaCreateStandardName(
            name="Granta record for analysis 1",
            mapped_cross_database_record_link_groups=[
                models.GsaSlimEntity(guid=guid) for guid in link_mapping.values()
            ],
        ),
    )

    logger.info("Creating and linking foreign records")
    for link_group_name, (attribute_name, unique_id) in FOREIGN_RS_LINKS.items():
        source_table_name, dest_table_name = FOREIGN_RS_LINK_GROUPS[link_group_name]

        logger.info(f"  Creating record {unique_id}")

        create_resp = record_client.create_record_history(
            database_key=FOREIGN_DB_KEY,
            table_guid=foreign_tables[dest_table_name],
            body=models.GsaCreateRecordHistory(name=unique_id, record_type=models.GsaRecordType.RECORD),
        )
        history_guid = create_resp.guid

        logger.info(f"    Setting attribute {attribute_name} value {unique_id}")
        data_client.set_datum_for_attribute(
            database_key=FOREIGN_DB_KEY,
            record_history_guid=history_guid,
            attribute_guid=attribute_guids[dest_table_name][attribute_name],
        )

        logger.info(f"    Creating cross-database link")
