from ansys.grantami.bomanalytics import indicators


LEGISLATIONS = ["The SIN List 2.1 (Substitute It Now!)", "Canadian Chemical Challenge"]


two_legislation_indicator = indicators.WatchListIndicator(
    name="Two legislations",
    legislation_names=["GADSL", "California Proposition 65 List"],
    default_threshold_percentage=2,
)
one_legislation_indicator = indicators.RoHSIndicator(
    name="One legislation",
    legislation_names=["EU Directive 2011/65/EU (RoHS 2)"],
    default_threshold_percentage=0.01,
)


INDICATORS = {"Two legislations": two_legislation_indicator,
              "One legislation": one_legislation_indicator}


def check_query_manager_attributes(query_manager, none_attributes, populated_attributes, populated_values):
    assert len(query_manager._item_argument_manager._items) == len(populated_values)
    for idx, value in enumerate(populated_values):
        if query_manager._item_argument_manager._items[idx].__getattribute__(populated_attributes) != value:
            return False
        for none_attr in none_attributes:
            if query_manager._item_argument_manager._items[idx].__getattribute__(none_attr):
                return False
    return True
