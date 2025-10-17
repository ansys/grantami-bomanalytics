"""
This script is the second step in the process of creating a new test database. It takes the json file output from
get_cleaned_db_entries.py and creates a new layout and subset with the required attributes and records.

It uses both the Ansys Granta MI Scripting Toolkit and the ansys-grantami-serverapi-openapi package to manipulate the
schema and records in the database.

Configuration is stored in _config.py. Set MI_URL appropriately for your system. Modify RS_DB_KEY_NEW and
CUSTOM_DB_KEY_NEW if required. For this script, RS_DB_KEY_NEW and CUSTOM_DB_KEY_NEW should refer to two separate
instances of the latest vanilla Restricted Substances & Sustainability database.

The database GUID of RS_DB_KEY_NEW **must** be unaltered to allow foreign links to persist to the database.
"""

import json
import logging
from pathlib import Path
from typing import Mapping, Iterable, Tuple, TYPE_CHECKING

from ansys.grantami.serverapi_openapi.v2025r2 import api, models
import GRANTA_MIScriptingToolkit as gdl

from cicd._connection import Connection
from cicd._utils import DatabaseBrowser, ServerApiClient
from cicd._config import LAYOUT_TO_PRESERVE, SUBSET_TO_PRESERVE, MI_URL, DATA_FILENAME, RS_DB_KEY_NEW, CUSTOM_DB_KEY_NEW

if TYPE_CHECKING:
    from ansys.openapi.common import ApiClient


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)


class TableLayoutApplier(ServerApiClient):
    def __init__(self, api_client: "ApiClient", logger: logging.Logger, db_key: str, table_guid: str) -> None:
        super().__init__(api_client, logger)
        self._attributes_api = api.SchemaAttributesApi(self._client)
        self._layouts_api = api.SchemaLayoutsApi(self._client)
        self._layout_sections_api = api.SchemaLayoutSectionsApi(self._client)
        table_attributes = self._attributes_api.get_attributes(database_key=db_key, table_guid=table_guid)
        self._db_key = db_key
        self._table_guid = table_guid
        self._attribute_name_map: Mapping[str, str] = {
            attribute.name: attribute.guid for attribute in table_attributes.attributes
        }

    def get_layout_name_guid_map(self) -> Mapping[str, str]:
        self.logger.info(f"Getting Layout Information for database '{self._db_key}' in table '{self._table_guid}'")
        layouts = self._layouts_api.get_layouts(database_key=self._db_key, table_guid=self._table_guid)
        layouts_map = {layout.name: layout.guid for layout in layouts.layouts}
        return layouts_map

    def delete_layout(self, layout_guid: str) -> None:
        logger.info(f"Deleting layout '{layout_guid}'")
        self._layouts_api.delete_layout(database_key=self._db_key, table_guid=self._table_guid, layout_guid=layout_guid)

    def create_layout(self, layout_name: str) -> str:
        logger.info(f"Creating new layout '{layout_name}'")
        layout_request = models.GsaCreateLayout(name=layout_name)
        layout_response = self._layouts_api.create_layout(
            database_key=self._db_key, table_guid=self._table_guid, body=layout_request
        )
        return layout_response.guid

    def create_layout_section(self, layout_guid: str, section_name: str) -> str:
        logger.info(f"Creating new layout section '{section_name}' in layout '{layout_guid}'")
        section_request = models.GsaCreateLayoutSection(name=section_name)
        section_response = self._layout_sections_api.create_section(  # noqa: E501
            database_key=self._db_key, table_guid=self._table_guid, layout_guid=layout_guid, body=section_request
        )
        return section_response.guid

    def add_layout_section_item(self, layout_guid: str, layout_section_guid: str, item_information: Mapping):
        logger.info(
            f"Adding new item '{item_information['name']}' to layout section '{layout_section_guid}' in layout '{layout_guid}'"  # noqa: E501
        )
        new_section_item = self._process_layout_item(item_information)
        if new_section_item is None:
            return
        self._layout_sections_api.create_layout_item(  # noqa: E501
            database_key=self._db_key,
            table_guid=self._table_guid,
            layout_guid=layout_guid,
            section_guid=layout_section_guid,
            body=new_section_item,
        )

    def _process_layout_item(self, item_information: Mapping) -> models.GsaNewLayoutItem | None:
        if item_information["item_type"] == "attribute":
            return self._process_attribute(item_information)
        elif item_information["item_type"] == "link":
            if item_information["link_type"] == "associationChain":
                return self._process_association_chain(item_information)
            elif item_information["link_type"] == "crossDatabaseLink":
                return None
        raise NotImplementedError("Other layout items are not supported yet...")

    def _process_association_chain(self, layout_item):
        item_name = layout_item["name"]
        logger.info(f"--Association Chain - '{item_name}'")
        links = self._process_association_chain_link(layout_item)
        return models.GsaNewLayoutAssociationChainItem(association_chain_name=item_name, association_chain_links=links)

    def _process_association_chain_link(self, chain_link):
        links = [
            models.GsaNewLayoutAssociationChainLink(
                forwards=chain_link["forwards"],
                tabular_attribute_guid=chain_link["underlying_entity_guid"],
                source_database_version_guid=chain_link["target_database"],
            )
        ]
        logger.info(f"----Link - {chain_link['name']}")
        if chain_link["next_link"] is not None:
            links.extend(self._process_association_chain_link(chain_link["next_link"]))
        return links

    def _process_attribute(self, layout_item: Mapping):
        attribute_name = layout_item["name"]
        logger.info(f"--Attribute - '{attribute_name}'")
        meta_names = [i["name"] for i in layout_item["meta_attributes"]]
        attribute_guid = self._attribute_name_map[attribute_name]

        new_section_item = models.GsaNewLayoutAttributeItem(attribute_guid=attribute_guid)
        if layout_item["tabular_columns"] is not None:
            detailed_attribute_info = self._attributes_api.get_attribute(
                database_key=self._db_key, table_guid=self._table_guid, attribute_guid=attribute_guid
            )
            assert isinstance(detailed_attribute_info, models.GsaTabularAttribute)
            column_map = {column.name: column for column in detailed_attribute_info.tabular_columns}
            columns = []
            for column_item in layout_item["tabular_columns"]:
                columns.append(column_map[column_item["name"]].guid)
            new_section_item.tabular_column_guids = columns
        if len(meta_names) > 0:
            logger.info("--Meta-attributes")
            metas = []
            meta_response = self._attributes_api.get_meta_attributes_for_attribute(  # noqa: E501
                database_key=self._db_key, table_guid=self._table_guid, attribute_guid=attribute_guid
            )
            meta_map = {meta.name: meta.guid for meta in meta_response.attributes}
            for meta_name in meta_names:
                logger.info(f"----{meta_name}")
                meta_item = meta_map[meta_name]
                metas.append(models.GsaNewLayoutAttributeItem(attribute_guid=meta_item))
            new_section_item.meta_attributes = metas
        return new_section_item


class SubsetCreator(ServerApiClient):
    def get_subset_name_guid_map(self, db_key: str, table_guid: str) -> Mapping[str, str]:
        subsets_api = api.SchemaSubsetsApi(self._client)
        self.logger.info(f"Getting Subset Information for database '{db_key}' in table '{table_guid}'")
        subsets = subsets_api.get_subsets(database_key=db_key, table_guid=table_guid)
        subsets_map = {subset.name: subset.guid for subset in subsets.subsets}
        return subsets_map

    def delete_subset(self, db_key: str, table_guid: str, subset_guid: str):
        subsets_api = api.SchemaSubsetsApi(self._client)
        self.logger.info(f"Deleting subset '{subset_guid}'")
        subsets_api.delete_subset(database_key=db_key, table_guid=table_guid, subset_guid=subset_guid)

    def create_subset(self, db_key: str, table_guid: str, subset_name: str) -> str:
        subsets_api = api.SchemaSubsetsApi(self._client)
        self.logger.info(f"Creating new subset '{subset_name}'")
        subset_request = models.GsaCreateSubset(name=subset_name)
        subset_response = subsets_api.create_subset(database_key=db_key, table_guid=table_guid, body=subset_request)
        return subset_response.guid


class SubsetPopulater:
    def __init__(self, gdl_session: gdl.GRANTA_MISession, logger: logging.Logger):
        self._session = gdl_session
        self._logger = logger
        self._data_import_session = self._session.dataImportService
        self._data_export_session = self._session.dataExportService

    def _get_subsets(
        self, db_key: str, record_identifiers: Iterable[Tuple[str, str]]
    ) -> Iterable[Iterable[gdl.SubsetReference]]:
        self._logger.info("Fetching subset membership for records")
        record_references = [
            gdl.RecordReference(DBKey=db_key, historyGUID=history_guid, recordUID=str(uid))
            for uid, (history_guid, _) in enumerate(record_identifiers)
        ]
        subsets_request = gdl.GetRecordAttributesByRefRequest(
            attributeReferences=[
                gdl.AttributeReference(
                    DBKey=db_key, pseudoAttribute=gdl.AttributeReference.MIPseudoAttributeReference.subsets
                )
            ],
            recordReferences=record_references,
        )
        subsets_response = self._data_export_session.GetRecordAttributesByRef(subsets_request)
        self._logger.info(f"Fetched subset membership for {len(record_references)} records")

        items = subsets_response.recordData
        items.sort(key=lambda x: x.recordReference.recordUID)
        existing_subsets = [
            [subset.subset for subset in item.attributeValues[0].subsetsDataType.namedSubsets] for item in items
        ]
        return existing_subsets

    def add_records_to_subset(
        self, db_key: str, record_identifiers: Iterable[Tuple[str, str]], table_guid: str, new_subset_name: str
    ) -> None:
        existing_subsets = self._get_subsets(db_key, record_identifiers)

        import_records = []
        for (history_guid, record_guid), existing_subsets in zip(record_identifiers, existing_subsets):
            new_subsets = existing_subsets
            new_subsets.append(
                gdl.SubsetReference(
                    DBKey=db_key,
                    name=new_subset_name,
                    partialTableReference=gdl.PartialTableReference(tableGUID=table_guid),
                )
            )
            import_record = gdl.ImportRecord(
                existingRecord=gdl.RecordReference(DBKey=db_key, historyGUID=history_guid),
                subsetReferences=new_subsets,
                releaseRecord=True,
                importRecordMode="Update",
            )
            import_records.append(import_record)
        self._logger.info("Adding specified records to the new subset")
        import_request = gdl.SetRecordAttributesRequest(importRecords=import_records)
        self._data_import_session.SetRecordAttributes(import_request)


def process_database(
    database_key: str, api_client: "ApiClient", gdl_session: gdl.GRANTA_MISession, table_name_map: Mapping[str, str]
):
    for table_name, table_data in input_data.items():
        table_guid = table_name_map.get(table_name, None)
        logger.info(f"Processing table '{table_name}'")
        if table_guid is None:
            message = [
                f"No table with name {table_name} in database... Perhaps the schema has changed?",
                "Tables available:",
            ]
            for available_table_name in table_name_map:
                message.append(f"  {available_table_name}")
            raise KeyError("\n".join(message))

        logger.info("Checking whether subset already exists")
        subsets_creator = SubsetCreator(api_client, logger)
        existing_subsets = subsets_creator.get_subset_name_guid_map(db_key=database_key, table_guid=table_guid)
        if SUBSET_TO_PRESERVE in existing_subsets:
            logger.info("Deleting existing subset")
            subsets_creator.delete_subset(
                db_key=database_key, table_guid=table_guid, subset_guid=existing_subsets[SUBSET_TO_PRESERVE]
            )

        logger.info("Creating subset for use")
        created_subset_guid = subsets_creator.create_subset(
            db_key=database_key, table_guid=table_guid, subset_name=SUBSET_TO_PRESERVE
        )
        logger.info(f"Created subset {SUBSET_TO_PRESERVE} with GUID {created_subset_guid}")

        logger.info("Checking whether layout already exists")
        table_layout_provider = TableLayoutApplier(api_client, logger, db_key=database_key, table_guid=table_guid)
        layout_name_guid_map = table_layout_provider.get_layout_name_guid_map()
        if LAYOUT_TO_PRESERVE in layout_name_guid_map:
            logger.info("Deleting existing layout")
            table_layout_provider.delete_layout(layout_name_guid_map[LAYOUT_TO_PRESERVE])

        logger.info("Creating layout to preserve attributes")
        new_layout_guid = table_layout_provider.create_layout(LAYOUT_TO_PRESERVE)

        logger.info("Populating layout sections")
        for section in table_data["layout"]:
            section_name = section["name"]
            section_items = section["section_items"]
            logger.info(f"Creating layout section '{section_name}'")
            section_guid = table_layout_provider.create_layout_section(
                layout_guid=new_layout_guid, section_name=section_name
            )
            logger.info("Populating with attributes")

            for section_item in section_items:
                table_layout_provider.add_layout_section_item(
                    layout_guid=new_layout_guid, layout_section_guid=section_guid, item_information=section_item
                )

        logging.info("Schema changes completed, populating subset")
        subset_populater = SubsetPopulater(gdl_session, logger)
        subset_populater.add_records_to_subset(
            db_key=database_key,
            record_identifiers=table_data["records"],
            table_guid=table_guid,
            new_subset_name=SUBSET_TO_PRESERVE,
        )


if __name__ == "__main__":
    api_client = Connection(api_url=MI_URL).with_autologon().connect()
    gdl_session = gdl.GRANTA_MISession(url=MI_URL, autoLogon=True)

    logger.info("Loading saved RS information...")
    INPUT_FILE_NAME = Path(__file__).parent / DATA_FILENAME
    if not INPUT_FILE_NAME.exists():
        logger.error("No saved data available. Run 'get_cleaned_db_entries.py' against an existing test DB first")
        exit(1)
    with open(INPUT_FILE_NAME, "r", encoding="utf8") as fp:
        input_data = json.load(fp)

    database_browser = DatabaseBrowser(api_client, logger)
    logger.info("Getting Table Information")

    vanilla_table_name_map = database_browser.get_table_name_guid_map(RS_DB_KEY_NEW)
    process_database(RS_DB_KEY_NEW, api_client, gdl_session, vanilla_table_name_map)

    custom_table_name_map = database_browser.get_table_name_guid_map(CUSTOM_DB_KEY_NEW)
    process_database(CUSTOM_DB_KEY_NEW, api_client, gdl_session, custom_table_name_map)

    logger.info("All done")
