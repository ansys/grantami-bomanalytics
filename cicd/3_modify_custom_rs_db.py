"""
This script is the third step in creating new test databases. It modifies a cut down database, changing the name,
renaming tables, and adding any extra records required for specific tests.

Configuration is stored in _config.py. Set MI_URL appropriately for your system. Modify CUSTOM_DB_KEY_NEW if required.

The first operation is to rename the database, this has no practical purpose, but it makes it easier to see which
database is which in log files.

Secondly the tables are renamed, this is required to test that the custom table name feature of the API works as
expected. If you change the names of the tables in the test setup you will need to change the names here as well.

The script then adds a copy of the styrene record as a child of Sulphuric Acid and withdraws it, this allows us to test
that the API returns a warning for us if more than one record matches a specific CAS number.

Finally, we create a new record in the specifications table which is linked to another, this allows us to test that the
specification depth parameter works as expected.
"""

import logging

import ansys.grantami.backend.soap as gdl

from ansys.grantami.serverapi_openapi.v2026r1 import api, models

from cicd._connection import Connection
from cicd._utils import DatabaseBrowser
from cicd._config import MI_URL, CUSTOM_DB_KEY_NEW, RS_CUSTOM_TABLE_NAME_MAPPING, CUSTOM_DB_NAME

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)


if __name__ == "__main__":
    logger.info("Renaming tables")

    api_client = Connection(api_url=MI_URL).with_autologon().connect()
    gdl_session = gdl.GRANTA_MISession(url=MI_URL, auto_logon=True)

    database_client = api.SchemaDatabasesApi(api_client)

    logger.info("Renaming Database")
    database_info: models.GsaDatabase = database_client.get_database(database_key=CUSTOM_DB_KEY_NEW)
    guid = database_info.guid
    rename_request = models.GsaUpdateDatabase(name=CUSTOM_DB_NAME)

    database_client.update_database(database_key=CUSTOM_DB_KEY_NEW, body=rename_request)

    database_browser = DatabaseBrowser(api_client, logger)
    custom_table_name_map = database_browser.get_table_name_guid_map(CUSTOM_DB_KEY_NEW)

    for old_name, new_name in RS_CUSTOM_TABLE_NAME_MAPPING.items():
        table_guid = custom_table_name_map[old_name]
        database_browser.update_table_name(db_key=CUSTOM_DB_KEY_NEW, table_guid=table_guid, new_table_name=new_name)

    logger.info("Duplicating styrene record then withdrawing it. (TestActAsReadUser)")
    data_import_service = gdl_session.data_import_service
    substances_guid = custom_table_name_map["Restricted Substances"]
    copy_import_record = gdl.ImportRecord(
        existing_record=gdl.RecordReference(
            db_key=CUSTOM_DB_KEY_NEW,
            lookup_value=gdl.LookupValue(
                attribute_reference=gdl.AttributeReference(
                    db_key=CUSTOM_DB_KEY_NEW,
                    name="CAS number",
                    partial_table_reference=gdl.PartialTableReference(table_guid=substances_guid),
                ),
                attribute_value="100-42-5",
            ),
        ),
        copy_destination_parent=gdl.RecordReference(
            db_key=CUSTOM_DB_KEY_NEW,
            lookup_value=gdl.LookupValue(
                attribute_reference=gdl.AttributeReference(
                    db_key=CUSTOM_DB_KEY_NEW,
                    name="CAS number",
                    partial_table_reference=gdl.PartialTableReference(table_guid=substances_guid),
                ),
                attribute_value="7664-93-9",
            ),
        ),
        subset_references=[
            gdl.SubsetReference(
                db_key=CUSTOM_DB_KEY_NEW,
                name="All Substances",
                partial_table_reference=gdl.PartialTableReference(table_guid=substances_guid),
            )
        ],
        record_name="Styrene Copy",
        release_record=True,
        import_record_mode="Copy",
    )
    copy_request = gdl.SetRecordAttributesRequest(import_records=[copy_import_record])
    copy_response = data_import_service.set_record_attributes(copy_request)

    record_reference = copy_response.records_imported[0].record_reference
    withdrawal_request = gdl.DeleteOrWithdrawIfLatestRecordVersionRequest(
        delete_or_withdraw_records=[gdl.DeleteOrWithdrawRecord(record_reference=record_reference)]
    )
    delete_response = data_import_service.delete_or_withdraw_if_latest_record_version(withdrawal_request)

    logger.info("Creating linked specifications. (TestSpecificationLinkDepth)")
    specs_guid = custom_table_name_map["Specifications"]

    thickness_value = gdl.RangeDataType(low=0.0508, high=0.127, unit_symbol="mm")
    thickness_cell = gdl.TabularDataImportCell(
        column_name="Thickness",
        range_data_value=thickness_value,
    )

    coating_row = gdl.TabularDataImportRow(cells=[thickness_cell], linking_value="Coating-203")
    coating_attribute = gdl.TabularDataImportType(import_rows=[coating_row])

    spec_row = gdl.TabularDataImportRow(linking_value="MIL-DTL-53039,TypeI")
    spec_attribute = gdl.TabularDataImportType(import_rows=[spec_row])

    import_spec_record = gdl.ImportRecord(
        existing_record=gdl.RecordReference(
            db_key=CUSTOM_DB_KEY_NEW,
            lookup_value=gdl.LookupValue(
                attribute_reference=gdl.AttributeReference(
                    db_key=CUSTOM_DB_KEY_NEW,
                    name="Specification ID",
                    partial_table_reference=gdl.PartialTableReference(table_guid=specs_guid),
                ),
                attribute_value="MIL-DTL-53039",
            ),
        ),
        record_name="MIL-DTL-53039, Type II",
        release_record=True,
        import_record_mode="Create",
        import_attribute_values=[
            gdl.ImportAttributeValue(
                attribute_reference=gdl.AttributeReference(
                    db_key=CUSTOM_DB_KEY_NEW,
                    name="Specification ID",
                    partial_table_reference=gdl.PartialTableReference(table_guid=specs_guid),
                ),
                short_text_data_value=gdl.ShortTextDataType(value="MIL-DTL-53039,TypeII"),
            ),
            gdl.ImportAttributeValue(
                attribute_reference=gdl.AttributeReference(
                    pseudo_attribute=gdl.AttributeReference.MIPseudoAttributeReference.shortName
                ),
                short_text_data_value=gdl.ShortTextDataType(value="MIL-DTL-53039, Type II"),
            ),
            gdl.ImportAttributeValue(
                attribute_reference=gdl.AttributeReference(
                    db_key=CUSTOM_DB_KEY_NEW,
                    name="Coatings in this specification",
                    partial_table_reference=gdl.PartialTableReference(table_guid=specs_guid),
                ),
                tabular_data_value=coating_attribute,
            ),
            gdl.ImportAttributeValue(
                attribute_reference=gdl.AttributeReference(
                    db_key=CUSTOM_DB_KEY_NEW,
                    name="Specifications in this specification",
                    partial_table_reference=gdl.PartialTableReference(table_guid=specs_guid),
                ),
                tabular_data_value=spec_attribute,
            ),
            gdl.ImportAttributeValue(
                attribute_reference=gdl.AttributeReference(
                    db_key=CUSTOM_DB_KEY_NEW,
                    name="Declaration type",
                    partial_table_reference=gdl.PartialTableReference(table_guid=specs_guid),
                ),
                discrete_data_value=gdl.DiscreteDataType(discrete_values=[gdl.DiscreteValue(value="Generic data")]),
            ),
        ],
        subset_references=[
            gdl.SubsetReference(
                db_key=CUSTOM_DB_KEY_NEW,
                name="All specifications",
                partial_table_reference=gdl.PartialTableReference(table_guid=specs_guid),
            )
        ],
    )
    import_spec_request = gdl.SetRecordAttributesRequest(import_records=[import_spec_record])
    import_spec_response = data_import_service.set_record_attributes(import_spec_request)
