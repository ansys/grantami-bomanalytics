from enum import Enum, auto
from abc import ABC
from typing import List, Union

from ansys.granta import bomanalytics
from ansys.granta.bomanalytics import models


class IndicatorDefinition(ABC):
    def __init__(self, name, legislation_names, default_threshold_percentage):
        self.name = name
        self.legislation_names = legislation_names
        self.default_threshold_percentage = default_threshold_percentage
        self._indicator_type = None

    @property
    def definition(self):
        return (
            bomanalytics.GrantaBomAnalyticsServicesInterfaceCommonIndicatorDefinition(
                name=self.name,
                legislation_names=self.legislation_names,
                default_threshold_percentage=self.default_threshold_percentage,
                type=self._indicator_type,
            )
        )


class Flags(Enum):
    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return TypeError(f"Cannot compare {type(self)} with {type(other)}")


class RoHSFlags(Flags):
    RohsNotImpacted = auto()
    RohsBelowThreshold = auto()
    RohsCompliant = auto()
    RohsCompliantWithExemptions = auto()
    RohsAboveThreshold = auto()
    RohsNonCompliant = auto()
    RohsUnknown = auto()


class WatchListFlags(Flags):
    WatchListNotImpacted = auto()
    WatchListCompliant = auto()
    WatchListBelowThreshold = auto()
    WatchListAllSubstancesBelowThreshold = auto()
    WatchListAboveThreshold = auto()
    WatchListHasSubstanceAboveThreshold = auto()
    WatchListUnknown = auto()


class RoHSIndicatorDefinition(IndicatorDefinition):
    flags = RoHSFlags

    def __init__(
        self,
        name: str,
        legislation_names: List[str],
        default_threshold_percentage: Union[float, None] = None,
    ):
        super().__init__(name, legislation_names, default_threshold_percentage)
        self._indicator_type = "Rohs"


class WatchListIndicatorDefinition(IndicatorDefinition):
    flags = WatchListFlags

    def __init__(
        self,
        name: str,
        legislation_names: List[str],
        default_threshold_percentage: Union[float, None] = None,
    ):
        super().__init__(name, legislation_names, default_threshold_percentage)
        self._indicator_type = "WatchList"


class RoHSIndicatorResult(RoHSIndicatorDefinition):
    def __init__(
        self,
        name: str,
        legislation_names: List[str],
        flag: str,
        default_threshold_percentage: Union[float, None] = None,
    ):
        super().__init__(name, legislation_names, default_threshold_percentage)
        try:
            self.flag: str = RoHSFlags[flag]
        except KeyError as e:
            raise Exception(
                f'Unknown flag {flag} for indicator {name}, type "RohsIndicator"'
            ).with_traceback(e.__traceback__)


class WatchListIndicatorResult(WatchListIndicatorDefinition):
    def __init__(
        self,
        name: str,
        legislation_names: List[str],
        flag: str,
        default_threshold_percentage: Union[float, None] = None,
    ):
        super().__init__(name, legislation_names, default_threshold_percentage)
        try:
            self.flag: str = WatchListFlags[flag]
        except KeyError as e:
            raise Exception(
                f'Unknown flag {flag} for indicator {name}, type "WatchListIndicator"'
            ).with_traceback(e.__traceback__)


def create_indicator_result(
    indicator_from_mi: models.granta_bom_analytics_services_interface_common_indicator_result,
    indicator_definitions: List[IndicatorDefinition],
) -> Union[WatchListIndicatorResult, RoHSIndicatorResult, None]:

    assert indicator_definitions, "indicator_definitions is empty"
    for indicator_definition in indicator_definitions:
        if indicator_from_mi.name == indicator_definition.name:
            if isinstance(indicator_definition, WatchListIndicatorDefinition):
                result = WatchListIndicatorResult(
                    name=indicator_from_mi.name,
                    legislation_names=indicator_definition.legislation_names,
                    default_threshold_percentage=indicator_definition.default_threshold_percentage,
                    flag=indicator_from_mi.flag,
                )
                return result
            elif isinstance(indicator_definition, RoHSIndicatorDefinition):
                result = RoHSIndicatorResult(
                    name=indicator_from_mi.name,
                    legislation_names=indicator_definition.legislation_names,
                    default_threshold_percentage=indicator_definition.default_threshold_percentage,
                    flag=indicator_from_mi.flag,
                )
                return result
            else:
                raise RuntimeError(
                    f"Indicator {indicator_definition.name} has unknown type {type(indicator_definition)}"
                )
    raise RuntimeError(
        f"Indicator {indicator_from_mi.name} does not have a corresponding definition"
    )
