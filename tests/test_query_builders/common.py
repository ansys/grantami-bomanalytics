def check_query_manager_attributes(query_manager, none_attributes, populated_attributes, populated_values):
    assert len(query_manager._data._item_definitions) == len(populated_values)
    for idx, value in enumerate(populated_values):
        if query_manager._data._item_definitions[idx].__getattribute__(populated_attributes) != value:
            return False
        for none_attr in none_attributes:
            if query_manager._data._item_definitions[idx].__getattribute__(none_attr):
                return False
    return True
