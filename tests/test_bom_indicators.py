import pytest
import random
from ansys.granta.bom_analytics import RoHSIndicator, WatchListIndicator
from ansys.granta.bomanalytics import models


def create_indicator(indicator):
    return indicator(
        name="TestIndicator",
        legislation_names=["Test legislation 1, Test legislation 2"],
        default_threshold_percentage=5,
    )


def get_random_flag(flag_enum):
    number_of_flags = len(flag_enum)
    flag = flag_enum(random.randint(2, number_of_flags - 1))
    return flag


def get_high_flag(flag_enum):
    return flag_enum(len(flag_enum))


def get_low_flag(flag_enum):
    return flag_enum(1)


@pytest.mark.parametrize("indicator, indicator_type", [(RoHSIndicator, "Rohs"), (WatchListIndicator, "WatchList")])
def test_indicator_definition(indicator, indicator_type):
    test_indicator = create_indicator(indicator)

    assert test_indicator.name == "TestIndicator"
    assert test_indicator.legislation_names == ["Test legislation 1, Test legislation 2"]
    assert test_indicator.default_threshold_percentage == 5
    assert test_indicator._indicator_type == indicator_type
    assert test_indicator.available_flags
    assert not test_indicator.flag


@pytest.mark.parametrize("indicator", [RoHSIndicator, WatchListIndicator])
def test_indicator_definition_property(indicator):
    test_indicator = create_indicator(indicator)

    definition = test_indicator.definition
    assert isinstance(definition, models.GrantaBomAnalyticsServicesInterfaceCommonIndicatorDefinition)
    assert definition.to_dict()["name"] == test_indicator.name
    assert definition.to_dict()["legislation_names"] == test_indicator.legislation_names
    assert definition.to_dict()["default_threshold_percentage"] == test_indicator.default_threshold_percentage
    assert definition.to_dict()["type"] == test_indicator._indicator_type


@pytest.mark.parametrize("indicator", [RoHSIndicator, WatchListIndicator])
@pytest.mark.parametrize("add_flag", [True, False])
def test_indicator_definition_comparison_value_error(indicator, add_flag):
    test_indicator = create_indicator(indicator)
    if add_flag:
        test_indicator.flag = get_random_flag(test_indicator.available_flags).name

    other_indicator = create_indicator(indicator)
    with pytest.raises(ValueError) as e:
        _ = test_indicator == other_indicator
    assert test_indicator.name in str(e.value)
    assert "has no flag" in str(e.value)

    with pytest.raises(ValueError) as e:
        _ = test_indicator < other_indicator
    assert test_indicator.name in str(e.value)
    assert "has no flag" in str(e.value)


@pytest.mark.parametrize("indicator, indicator_type", [(RoHSIndicator, "Rohs"), (WatchListIndicator, "WatchList")])
def test_indicator_result_less_than(indicator, indicator_type):
    test_indicator = create_indicator(indicator)
    test_indicator.flag = get_random_flag(test_indicator.available_flags).name

    low_indicator = create_indicator(indicator)
    low_indicator.flag = get_low_flag(test_indicator.available_flags).name

    assert test_indicator > low_indicator


@pytest.mark.parametrize("indicator, indicator_type", [(RoHSIndicator, "Rohs"), (WatchListIndicator, "WatchList")])
def test_indicator_result_greater_than(indicator, indicator_type):
    test_indicator = create_indicator(indicator)
    test_indicator.flag = get_random_flag(test_indicator.available_flags).name

    high_indicator = create_indicator(indicator)
    high_indicator.flag = get_high_flag(test_indicator.available_flags).name

    assert test_indicator < high_indicator


@pytest.mark.parametrize("indicator", [RoHSIndicator, WatchListIndicator])
def test_indicator_result_equal_to(indicator):
    test_indicator = create_indicator(indicator)
    test_indicator.flag = get_random_flag(test_indicator.available_flags).name

    same_indicator = create_indicator(indicator)
    same_indicator.flag = test_indicator.flag.name

    assert same_indicator == test_indicator


@pytest.mark.parametrize("indicator", [RoHSIndicator, WatchListIndicator])
def test_indicator_result_less_than_equal_to(indicator):
    test_indicator = create_indicator(indicator)
    test_indicator.flag = get_random_flag(test_indicator.available_flags).name

    same_indicator = create_indicator(indicator)
    same_indicator.flag = test_indicator.flag.name

    assert same_indicator >= test_indicator


@pytest.mark.parametrize(
    "indicator, other_indicator", [(RoHSIndicator, WatchListIndicator), (WatchListIndicator, RoHSIndicator)]
)
def test_indicator_result_different_indicators_type_error(indicator, other_indicator):
    test_indicator = create_indicator(indicator)
    test_indicator.flag = get_random_flag(test_indicator.available_flags).name

    other_test_indicator = create_indicator(other_indicator)
    other_test_indicator.flag = get_random_flag(other_test_indicator.available_flags).name

    with pytest.raises(TypeError) as e:
        _ = other_test_indicator == test_indicator
    assert str(indicator) in str(e.value)
    assert str(other_indicator) in str(e.value)

    with pytest.raises(TypeError) as e:
        _ = other_test_indicator < test_indicator
    assert str(indicator) in str(e.value)
    assert str(other_indicator) in str(e.value)


@pytest.mark.parametrize("indicator", [RoHSIndicator, WatchListIndicator])
def test_indicator_unknown_flag_key_error(indicator):
    test_indicator = create_indicator(indicator)
    with pytest.raises(KeyError) as e:
        test_indicator.flag = "Invalid Flag"
    assert 'Unknown flag "Invalid Flag"' in str(e.value)
    assert repr(test_indicator) in str(e.value)


@pytest.mark.parametrize("indicator", [RoHSIndicator, WatchListIndicator])
@pytest.mark.parametrize("add_flag", [True, False])
def test_indicator_str(indicator, add_flag):
    test_indicator = create_indicator(indicator)
    if add_flag:
        test_indicator.flag = get_random_flag(test_indicator.available_flags).name

    if add_flag:
        assert str(test_indicator) == f"{test_indicator.name}, {str(test_indicator.flag.name)}"
    else:
        assert str(test_indicator) == f"{test_indicator.name}"


@pytest.mark.parametrize("indicator", [RoHSIndicator, WatchListIndicator])
@pytest.mark.parametrize("add_flag", [True, False])
def test_indicator_repr(indicator, add_flag):
    test_indicator = create_indicator(indicator)
    if add_flag:
        test_indicator.flag = get_random_flag(test_indicator.available_flags).name

    if add_flag:
        assert (
            repr(test_indicator)
            == f"<{indicator.__name__}, name: {test_indicator.name}, flag: {str(test_indicator.flag)}>"
        )
    else:
        assert repr(test_indicator) == f"<{indicator.__name__}, name: {test_indicator.name}>"
