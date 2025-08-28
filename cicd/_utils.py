import logging
from typing import Mapping

from ansys.grantami.serverapi_openapi.v2025r2 import api, models
from ansys.openapi.common import ApiClient


class ServerApiClient:
    def __init__(self, api_client: ApiClient, logger: logging.Logger) -> None:
        self._client = api_client
        self.logger = logger


class TableBrowser(ServerApiClient):
    def get_table_name_guid_map(self, db_key: str) -> Mapping[str, str]:
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
