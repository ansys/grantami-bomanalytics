import logging
from typing import MutableMapping, Optional

from ansys.grantami.serverapi_openapi.v2025r2 import api, models
from ansys.openapi.common import ApiClient


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)


class ServerApiClient:
    def __init__(self, api_client: ApiClient, logger: logging.Logger) -> None:
        self._client = api_client
        self.logger = logger


class DatabaseBrowser(ServerApiClient):
    def get_database_guid(self, db_key: str) -> str:
        database_api = api.SchemaDatabasesApi(self._client)
        return database_api.get_database(database_key=db_key).guid

    def get_table_name_guid_map(self, db_key: str) -> MutableMapping[str, str]:
        tables_api = api.SchemaTablesApi(self._client)
        self.logger.info(f"Getting Table Information for database '{db_key}'")
        tables = tables_api.get_tables(database_key=db_key)
        table_name_map = {table.name: table.guid for table in tables.tables}
        logger.info(f"Fetched {len(table_name_map)} tables")
        for name, guid in table_name_map.items():
            logger.debug(f"Name: '{name}' - Guid: '{guid}'")
        return table_name_map

    def update_table_name(self, db_key: str, table_guid: str, new_table_name: str) -> None:
        tables_api = api.SchemaTablesApi(self._client)
        self.logger.info(f"Updating Table - {db_key}:{table_guid} with name '{new_table_name}'")
        patch_request = models.GsaUpdateTable(name=new_table_name)
        tables_api.update_table(database_key=db_key, table_guid=table_guid, body=patch_request)

    def update_database_name(self, db_key: str, new_database_name: str) -> None:
        database_api = api.SchemaDatabasesApi(self._client)
        self.logger.info(f"Updating Database - {db_key} with name '{new_database_name}'")
        patch_request = models.GsaUpdateDatabase(name=new_database_name)
        database_api.update_database(database_key=db_key, body=patch_request)

    def create_standard_name(
        self,
        db_key: str,
        name: str,
        mapped_attribute_guids: Optional[list[str]] = None,
        mapped_cross_database_record_link_group_guids: Optional[list[str]] = None,
    ) -> None:
        standard_name_client = api.SchemaStandardNamesApi(self._client)
        self.logger.info(f"Creating standard name - {name} in database - {db_key}")
        standard_name_client.create_standard_name(
            database_key=db_key,
            body=models.GsaCreateStandardName(
                name=name,
                mapped_attributes=(
                    [models.GsaSlimEntity(guid=guid) for guid in mapped_attribute_guids]
                    if mapped_attribute_guids
                    else None
                ),
                mapped_cross_database_record_link_groups=(
                    [models.GsaSlimEntity(guid=guid) for guid in mapped_cross_database_record_link_group_guids]
                    if mapped_cross_database_record_link_group_guids
                    else None
                ),
            ),
        )

    def delete_all_standard_names(self, db_key: str) -> None:
        standard_name_client = api.SchemaStandardNamesApi(self._client)
        self.logger.info(f"Deleting all standard names in database - {db_key}")
        all_standard_names = standard_name_client.get_standard_names(database_key=db_key).standard_names
        for standard_name in all_standard_names:
            standard_name_client.delete_standard_name(
                database_key=db_key,
                standard_name_guid=standard_name.guid,
            )

    def find_record_in_table_with_name(self, db_key: str, table_name: str, record_name: str) -> str | None:
        search_client = api.SearchApi(self._client)

        logger.info(
            f"Searching for record with name '{record_name}' exists in database - {db_key}, table - {table_name}"
        )

        table_name_to_guid_map = self.get_table_name_guid_map(db_key)
        table_guid = table_name_to_guid_map[table_name]

        search_result = search_client.database_search_in_table_with_guid(
            database_key=db_key,
            table_guid=table_guid,
            body=models.GsaSearchRequest(
                criterion=models.GsaRecordPropertyCriterion(
                    inner_criterion=models.GsaShortTextDatumCriterion(
                        value=record_name,
                        text_match_behavior=models.GsaTextMatchBehavior.EXACTMATCH,
                    ),
                    _property=models.GsaSearchableRecordProperty.RECORDNAME,
                )
            ),
        )
        if search_result.total_result_count == 0:
            logger.info("No record found.")
            return None
        if search_result.total_result_count == 1:
            result = search_result.results[0].record_history_guid
            logger.info(f"Record found with guid {result}.")
            return result
        raise RuntimeError(
            f"Multiple results found for Record Name search in database - {db_key}, table - {table_name} for record "
            f"name '{record_name}'. Cannot continue."
        )

    def create_record_in_table_with_name(self, db_key: str, table_name: str, record_name: str) -> str:
        record_client = api.RecordsRecordHistoriesApi(self._client)

        table_name_to_guid_map = self.get_table_name_guid_map(db_key)
        table_guid = table_name_to_guid_map[table_name]

        create_resp = record_client.create_record_history(
            database_key=db_key,
            table_guid=table_guid,
            body=models.GsaCreateRecordHistory(name=record_name, record_type=models.GsaRecordType.RECORD),
        )
        guid = create_resp.guid
        logger.info(f"  Record created with guid '{guid}'")
        return guid

    def ensure_record_exists_with_name(self, db_key: str, table_name: str, record_name: str) -> str:
        guid = self.find_record_in_table_with_name(db_key, table_name, record_name)
        if not guid:
            guid = self.create_record_in_table_with_name(db_key, table_name, record_name)
        return guid


def ensure_link_group_exists(
    api_client: ApiClient,
    name: str,
    db_key: str,
    source_table_guid: str,
    target_db_key: str,
    target_table_guid: str,
    reverse_name: Optional[str] = None,
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
            logger.info("  Link group already exists")
            return rlg.guid

    logger.info("  Link group not found. Creating.")
    target_db_guid = _database_browser.get_database_guid(target_db_key)
    create_response = rlg_client.create_record_link_group(
        database_key=db_key,
        table_guid=source_table_guid,
        body=models.GsaCreateRecordLinkGroup(
            link_target=models.GsaLinkTarget(
                database_guid=target_db_guid,
                table_guid=target_table_guid,
            ),
            name=name,
            reverse_name=f"{name} (reverse)" if reverse_name is None else reverse_name,
            type=models.GsaRecordLinkGroupType.CROSSDATABASE,
        ),
    )
    return create_response.guid
