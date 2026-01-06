def example_0_basic_usage():
    assert len(result.impacted_substances) == 12
    assert len(result.messages) == 0
    # Expected cells with outputs
    assert set(Out.keys()) == set([2, 3, 4, 5, 6, 7, 8, 9, 10, 11])

def example_1_database_config():
    assert cxn._table_names["inhouse_materials_table_name"] == "ACME Materials"
    assert spec_query._data.batch_size == 5
    assert cxn.maximum_spec_link_depth == 2

def example_4_1_sustainability():
    assert len(records) == 50


examples_expectations = {
    "0_Basic_usage.py": example_0_basic_usage,
    "1_Database-specific_configuration.py": example_1_database_config,
    "4_Sustainability/4-1_Sustainability.py": example_4_1_sustainability,
}
