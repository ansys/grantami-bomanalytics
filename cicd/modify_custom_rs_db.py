"""
modify_custom_rs_db.py
-------------------------

This script is the last step in creating new test databases. It modifies a cut down database, changing the name,
renaming tables, and adding any extra records required for specific tests.

Set the URL as appropriate for your database server.

The first operation is to rename the database, this has no practical purpose, but it makes it easier to see which which
database is which in log files.

Secondly the tables are renamed, this is required to test that the custom table name feature of the API works as
expected. If you change the names of the tables in the test setup you will need to change the names here as well.

The script then adds a copy of the styrene record as a child of Sulphuric Acid and withdraws it, this allows us to test
that the API returns a warning for us if more than one record matches a specific CAS number.

Finally, we create a new record in the specifications table which is linked to another, this allows us to test that the
specification depth parameter works as expected.
"""

import logging

import GRANTA_MIScriptingToolkit as gdl

from ansys.grantami.serverapi_openapi import api, models

from cicd.connection import Connection
from cicd.prepare_rs_db import TableBrowser

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)

CUSTOM_DB_KEY = "MI_Restricted_Substances_Custom_Tables"

if __name__ == "__main__":
    logger.info("Renaming tables")
    table_name_remapping = {
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

    URL = "http://localhost/mi_servicelayer"
    api_client = Connection(api_url=URL).with_autologon().connect()
    gdl_session = gdl.GRANTA_MISession(url=URL, autoLogon=True)

    database_client = api.SchemaDatabasesApi(api_client)

    logger.info("Renaming Database")
    database_info: models.GrantaServerApiSchemaDatabase = database_client.v1alpha_databases_database_key_get(
        database_key=CUSTOM_DB_KEY
    )
    guid = database_info.guid
    new_name = "Restricted Substances Custom Tables"
    rename_request = models.GrantaServerApiSchemaUpdateDatabase(name=new_name)

    database_client.v1alpha_databases_database_key_patch(database_key=CUSTOM_DB_KEY, body=rename_request)

    table_browser = TableBrowser(api_client, logger)
    custom_table_name_map = table_browser.get_table_name_guid_map(CUSTOM_DB_KEY)

    for old_name, new_name in table_name_remapping.items():
        table_guid = custom_table_name_map[old_name]
        table_browser.update_table_name(db_key=CUSTOM_DB_KEY, table_guid=table_guid, new_table_name=new_name)

    logger.info("Duplicating styrene record then withdrawing it. (TestActAsReadUser)")
    data_import_service = gdl_session.dataImportService
    substances_guid = custom_table_name_map["Restricted Substances"]
    copy_import_record = gdl.ImportRecord(
        existingRecord=gdl.RecordReference(
            DBKey=CUSTOM_DB_KEY,
            lookupValue=gdl.LookupValue(
                attributeReference=gdl.AttributeReference(
                    DBKey=CUSTOM_DB_KEY,
                    name="CAS number",
                    partialTableReference=gdl.PartialTableReference(tableGUID=substances_guid),
                ),
                attributeValue="100-42-5",
            ),
        ),
        copyDestinationParent=gdl.RecordReference(
            DBKey=CUSTOM_DB_KEY,
            lookupValue=gdl.LookupValue(
                attributeReference=gdl.AttributeReference(
                    DBKey=CUSTOM_DB_KEY,
                    name="CAS number",
                    partialTableReference=gdl.PartialTableReference(tableGUID=substances_guid),
                ),
                attributeValue="7664-93-9",
            ),
        ),
        subsetReferences=[
            gdl.SubsetReference(
                DBKey=CUSTOM_DB_KEY,
                name="All Substances",
                partialTableReference=gdl.PartialTableReference(tableGUID=substances_guid),
            )
        ],
        recordName="Styrene Copy",
        releaseRecord=True,
        importRecordMode="Copy",
    )
    copy_request = gdl.SetRecordAttributesRequest(importRecords=[copy_import_record])
    copy_response = data_import_service.SetRecordAttributes(copy_request)

    record_reference = copy_response.recordsImported[0].recordReference
    withdrawal_request = gdl.DeleteOrWithdrawIfLatestRecordVersionRequest(
        deleteOrWithdrawRecords=[gdl.DeleteOrWithdrawRecord(recordReference=record_reference)]
    )
    delete_response = data_import_service.DeleteOrWithdrawIfLatestRecordVersion(withdrawal_request)

    logger.info("Creating linked specifications. (TestSpecificationLinkDepth)")
    specs_guid = custom_table_name_map["Specifications"]

    tabular_type = gdl.TabularDataType()
    tabular_type.AddColumn("Thickness")
    new_row = tabular_type.CreateRow()

    new_row.linkingValue = "Coating-203"
    new_row.cells[0].data = gdl.RangeDataType(low=0.0508, high=0.127, unitSymbol="mm")
    tabular_type.tabularDataRows.append(new_row)

    spec_link_attribute = gdl.TabularDataType()
    new_spec_row = spec_link_attribute.CreateRow()
    new_spec_row.linkingValue = "MIL-DTL-53039,TypeI"
    spec_link_attribute.tabularDataRows.append(new_spec_row)

    import_spec_record = gdl.ImportRecord(
        existingRecord=gdl.RecordReference(
            DBKey=CUSTOM_DB_KEY,
            lookupValue=gdl.LookupValue(
                attributeReference=gdl.AttributeReference(
                    DBKey=CUSTOM_DB_KEY,
                    name="Specification ID",
                    partialTableReference=gdl.PartialTableReference(tableGUID=specs_guid),
                ),
                attributeValue="MIL-DTL-53039",
            ),
        ),
        recordName="MIL-DTL-53039, Type II",
        releaseRecord=True,
        importRecordMode="Create",
        importAttributeValues=[
            gdl.ImportAttributeValue(
                attributeReference=gdl.AttributeReference(
                    DBKey=CUSTOM_DB_KEY,
                    name="Specification ID",
                    partialTableReference=gdl.PartialTableReference(tableGUID=specs_guid),
                ),
                shortTextDataValue=gdl.ShortTextDataType(value="MIL-DTL-53039,TypeII"),
            ),
            gdl.ImportAttributeValue(
                attributeReference=gdl.AttributeReference(
                    pseudoAttribute=gdl.AttributeReference.MIPseudoAttributeReference.shortName
                ),
                shortTextDataValue=gdl.ShortTextDataType(value="MIL-DTL-53039, Type II"),
            ),
            gdl.ImportAttributeValue(
                attributeReference=gdl.AttributeReference(
                    DBKey=CUSTOM_DB_KEY,
                    name="Coatings in this specification",
                    partialTableReference=gdl.PartialTableReference(tableGUID=specs_guid),
                ),
                tabularDataValue=tabular_type,
            ),
            gdl.ImportAttributeValue(
                attributeReference=gdl.AttributeReference(
                    DBKey=CUSTOM_DB_KEY,
                    name="Specifications in this specification",
                    partialTableReference=gdl.PartialTableReference(tableGUID=specs_guid),
                ),
                tabularDataValue=spec_link_attribute,
            ),
            gdl.ImportAttributeValue(
                attributeReference=gdl.AttributeReference(
                    DBKey=CUSTOM_DB_KEY,
                    name="Declaration type",
                    partialTableReference=gdl.PartialTableReference(tableGUID=specs_guid),
                ),
                discreteDataValue=gdl.DiscreteDataType(discreteValues=[gdl.DiscreteValue(value="Generic data")]),
            ),
        ],
        subsetReferences=[
            gdl.SubsetReference(
                DBKey=CUSTOM_DB_KEY,
                name="All specifications",
                partialTableReference=gdl.PartialTableReference(tableGUID=specs_guid),
            )
        ],
    )
    import_spec_request = gdl.SetRecordAttributesRequest(importRecords=[import_spec_record])
    import_spec_response = data_import_service.SetRecordAttributes(import_spec_request)
