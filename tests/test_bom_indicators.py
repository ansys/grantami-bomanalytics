from .common import (
    pytest,
    random,
    indicators,
    GrantaBomAnalyticsServicesInterfaceCommonIndicatorDefinition,
)


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


@pytest.mark.parametrize("indicator", [indicators.RoHSIndicator, indicators.WatchListIndicator])
class TestFlagComparison:
    def test_flag_greater_than(self, indicator):
        assert get_high_flag(indicator.available_flags) > get_random_flag(indicator.available_flags) \
               > get_low_flag(indicator.available_flags)

    def test_flag_greater_than_equal_to(self, indicator):
        flag = get_random_flag(indicator.available_flags)
        assert flag >= flag >= get_low_flag(indicator.available_flags)

    def test_flag_less_than(self, indicator):
        assert get_low_flag(indicator.available_flags) < get_random_flag(indicator.available_flags) \
               < get_high_flag(indicator.available_flags)

    def test_flag_less_than_equal_to(self, indicator):
        flag = get_random_flag(indicator.available_flags)
        assert flag <= flag <= get_high_flag(indicator.available_flags)

    def test_flag_equal(self, indicator):
        flag = get_random_flag(indicator.available_flags)
        assert flag == flag
        assert not flag != flag

    def test_flag_identity(self, indicator):
        flag = get_random_flag(indicator.available_flags)
        assert flag is flag


@pytest.mark.parametrize("indicator", [indicators.RoHSIndicator, indicators.WatchListIndicator])
class TestIndicators:
    def test_indicator_definition(self, indicator):
        test_indicator = create_indicator(indicator)

        assert test_indicator.name == "TestIndicator"
        assert test_indicator.legislation_names == ["Test legislation 1, Test legislation 2"]
        assert test_indicator.default_threshold_percentage == 5
        if indicator is indicators.RoHSIndicator:
            assert test_indicator._indicator_type == "Rohs"
        elif indicator is indicators.WatchListIndicator:
            assert test_indicator._indicator_type == "WatchList"
        else:
            raise AssertionError
        assert test_indicator.available_flags
        assert not test_indicator.flag

    def test_indicator_definition_property(self, indicator):
        test_indicator = create_indicator(indicator)

        definition = test_indicator._definition
        assert isinstance(definition, GrantaBomAnalyticsServicesInterfaceCommonIndicatorDefinition)
        assert definition.to_dict()["name"] == test_indicator.name
        assert definition.to_dict()["legislation_names"] == test_indicator.legislation_names
        assert definition.to_dict()["default_threshold_percentage"] == test_indicator.default_threshold_percentage
        assert definition.to_dict()["type"] == test_indicator._indicator_type

    def test_indicator_unknown_flag_key_error(self, indicator):
        test_indicator = create_indicator(indicator)
        with pytest.raises(KeyError) as e:
            test_indicator.flag = "Invalid Flag"
        assert 'Unknown flag "Invalid Flag"' in str(e.value)
        assert repr(test_indicator) in str(e.value)

    def test_indicator_str_with_flag(self, indicator):
        test_indicator = create_indicator(indicator)
        test_indicator.flag = get_random_flag(test_indicator.available_flags).name
        assert str(test_indicator) == f"{test_indicator.name}, {str(test_indicator.flag.name)}"

    def test_indicator_str_without_flag(self, indicator):
        test_indicator = create_indicator(indicator)
        assert str(test_indicator) == f"{test_indicator.name}"

    def test_indicator_repr_with_flag(self, indicator):
        test_indicator = create_indicator(indicator)
        test_indicator.flag = get_random_flag(test_indicator.available_flags).name

        assert repr(test_indicator) == f"<{indicator.__name__}, name: {test_indicator.name}," \
                                       f" flag: {str(test_indicator.flag)}>"

    def test_indicator_repr_without_flag(self, indicator):
        test_indicator = create_indicator(indicator)
        assert repr(test_indicator) == f"<{indicator.__name__}, name: {test_indicator.name}>"


@pytest.mark.parametrize("indicator", [indicators.RoHSIndicator, indicators.WatchListIndicator])
class TestIndicatorComparison:
    @pytest.mark.parametrize("add_flag", [True, False])
    def test_definition_comparison_value_error(self, indicator, add_flag):
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

    def test_less_than(self, indicator):
        test_indicator = create_indicator(indicator)
        test_indicator.flag = get_random_flag(test_indicator.available_flags).name

        low_indicator = create_indicator(indicator)
        low_indicator.flag = get_low_flag(test_indicator.available_flags).name

        assert low_indicator < test_indicator
        assert not low_indicator >= test_indicator

    def test_greater_than(self, indicator):
        test_indicator = create_indicator(indicator)
        test_indicator.flag = get_random_flag(test_indicator.available_flags).name

        high_indicator = create_indicator(indicator)
        high_indicator.flag = get_high_flag(test_indicator.available_flags).name

        assert high_indicator > test_indicator
        assert not high_indicator <= test_indicator

    def test_equal_to(self, indicator):
        test_indicator = create_indicator(indicator)
        test_indicator.flag = get_random_flag(test_indicator.available_flags).name

        same_indicator = create_indicator(indicator)
        same_indicator.flag = test_indicator.flag.name

        assert same_indicator == test_indicator
        assert not same_indicator != test_indicator

    def test_not_equal_to(self, indicator):
        test_indicator = create_indicator(indicator)
        test_indicator.flag = get_high_flag(test_indicator.available_flags).name

        other_indicator = create_indicator(indicator)
        other_indicator.flag = get_low_flag(test_indicator.available_flags).name

        assert test_indicator != other_indicator
        assert not test_indicator == other_indicator

    def test_less_than_equal_to(self, indicator):
        test_indicator = create_indicator(indicator)
        test_indicator.flag = get_random_flag(test_indicator.available_flags).name

        same_indicator = create_indicator(indicator)
        same_indicator.flag = test_indicator.flag.name

        low_indicator = create_indicator(indicator)
        low_indicator.flag = get_low_flag(test_indicator.available_flags).name

        assert same_indicator <= test_indicator
        assert low_indicator <= test_indicator
        assert not same_indicator > test_indicator
        assert not low_indicator > test_indicator

    def test_greater_than_equal_to(self, indicator):
        test_indicator = create_indicator(indicator)
        test_indicator.flag = get_random_flag(test_indicator.available_flags).name

        same_indicator = create_indicator(indicator)
        same_indicator.flag = test_indicator.flag.name

        high_indicator = create_indicator(indicator)
        high_indicator.flag = get_high_flag(test_indicator.available_flags).name

        assert same_indicator >= test_indicator
        assert high_indicator >= test_indicator
        assert not same_indicator < test_indicator
        assert not high_indicator < test_indicator

@pytest.mark.parametrize(
    "indicator, other_indicator",
    [
        (indicators.RoHSIndicator, indicators.WatchListIndicator),
        (indicators.WatchListIndicator, indicators.RoHSIndicator),
    ],
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


@pytest.mark.parametrize("indicator", [indicators.RoHSIndicator, indicators.WatchListIndicator])
class TestCompareFlagWithIndicator:
    def test_compare_with_definition_value_error(self, indicator):
        test_indicator = create_indicator(indicator)
        test_indicator.flag = get_random_flag(test_indicator.available_flags).name

        other_indicator = create_indicator(indicator)
        with pytest.raises(ValueError) as e:
            _ = test_indicator.flag == other_indicator
        assert test_indicator.name in str(e.value)
        assert "has no flag" in str(e.value)

        with pytest.raises(ValueError) as e:
            _ = test_indicator.flag < other_indicator
        assert test_indicator.name in str(e.value)
        assert "has no flag" in str(e.value)

    def test_less_than(self, indicator):
        test_indicator = create_indicator(indicator)
        test_indicator.flag = get_random_flag(test_indicator.available_flags).name

        assert get_low_flag(test_indicator.available_flags) < test_indicator
        assert not get_low_flag(test_indicator.available_flags) >= test_indicator

    def test_greater_than(self, indicator):
        test_indicator = create_indicator(indicator)
        test_indicator.flag = get_random_flag(test_indicator.available_flags).name

        assert get_high_flag(test_indicator.available_flags) > test_indicator
        assert not get_high_flag(test_indicator.available_flags) <= test_indicator

    def test_equal_to(self, indicator):
        test_indicator = create_indicator(indicator)
        test_indicator.flag = get_random_flag(test_indicator.available_flags).name

        assert test_indicator.flag == test_indicator
        assert not test_indicator.flag != test_indicator

    def test_not_equal_to(self, indicator):
        low_indicator = create_indicator(indicator)
        low_indicator.flag = get_low_flag(low_indicator.available_flags).name

        assert get_high_flag(low_indicator.available_flags) != low_indicator
        assert not get_high_flag(low_indicator.available_flags) == low_indicator

    def test_less_than_equal_to(self, indicator):
        test_indicator = create_indicator(indicator)
        test_indicator.flag = get_random_flag(test_indicator.available_flags).name

        low_indicator = create_indicator(indicator)
        low_indicator.flag = get_low_flag(test_indicator.available_flags).name

        assert test_indicator.flag <= test_indicator
        assert get_low_flag(test_indicator.available_flags) <= test_indicator
        assert not test_indicator.flag > test_indicator
        assert not get_low_flag(test_indicator.available_flags) > test_indicator

    def test_greater_than_equal_to(self, indicator):
        test_indicator = create_indicator(indicator)
        test_indicator.flag = get_random_flag(test_indicator.available_flags).name

        high_indicator = create_indicator(indicator)
        high_indicator.flag = get_high_flag(test_indicator.available_flags).name

        assert test_indicator.flag >= test_indicator
        assert get_high_flag(test_indicator.available_flags) >= test_indicator
        assert not test_indicator.flag < test_indicator
        assert not get_high_flag(test_indicator.available_flags) < test_indicator


@pytest.mark.parametrize("indicator", [(indicators.RoHSIndicator), (indicators.WatchListIndicator)])
class TestCompareIndicatorWithFlag:
    def test_compare_with_definition_value_error(self, indicator):
        test_indicator = create_indicator(indicator)
        test_indicator.flag = get_random_flag(test_indicator.available_flags).name

        other_indicator = create_indicator(indicator)
        with pytest.raises(ValueError) as e:
            _ = other_indicator == test_indicator.flag
        assert test_indicator.name in str(e.value)
        assert "has no flag" in str(e.value)

        with pytest.raises(ValueError) as e:
            _ = other_indicator < test_indicator.flag
        assert test_indicator.name in str(e.value)
        assert "has no flag" in str(e.value)

    def test_less_than(self, indicator):
        low_indicator = create_indicator(indicator)
        low_indicator.flag = get_low_flag(low_indicator.available_flags).name

        assert low_indicator < get_random_flag(low_indicator.available_flags)
        assert not low_indicator >= get_random_flag(low_indicator.available_flags)

    def test_greater_than(self, indicator):
        high_indicator = create_indicator(indicator)
        high_indicator.flag = get_high_flag(high_indicator.available_flags).name

        assert high_indicator > get_random_flag(high_indicator.available_flags)
        assert not high_indicator <= get_random_flag(high_indicator.available_flags)

    def test_equal_to(self, indicator):
        test_indicator = create_indicator(indicator)
        test_indicator.flag = get_random_flag(test_indicator.available_flags).name

        assert test_indicator == test_indicator.flag
        assert not test_indicator != test_indicator.flag

    def test_not_equal_to(self, indicator):
        low_indicator = create_indicator(indicator)
        low_indicator.flag = get_low_flag(low_indicator.available_flags).name

        assert low_indicator != get_high_flag(low_indicator.available_flags)
        assert not low_indicator == get_high_flag(low_indicator.available_flags)

    def test_less_than_equal_to(self, indicator):
        test_indicator = create_indicator(indicator)
        test_indicator.flag = get_random_flag(test_indicator.available_flags).name

        low_indicator = create_indicator(indicator)
        low_indicator.flag = get_low_flag(test_indicator.available_flags).name

        assert test_indicator <= test_indicator.flag
        assert low_indicator <= test_indicator.flag
        assert not test_indicator > test_indicator.flag
        assert not low_indicator > test_indicator.flag

    def test_greater_than_equal_to(self, indicator):
        test_indicator = create_indicator(indicator)
        test_indicator.flag = get_random_flag(test_indicator.available_flags).name

        high_indicator = create_indicator(indicator)
        high_indicator.flag = get_high_flag(test_indicator.available_flags).name

        assert test_indicator >= test_indicator.flag
        assert high_indicator >= test_indicator.flag
        assert not test_indicator < test_indicator.flag
        assert not high_indicator < test_indicator.flag
