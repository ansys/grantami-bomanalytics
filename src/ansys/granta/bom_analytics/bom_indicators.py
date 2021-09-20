from enum import Enum, auto
from abc import ABC
from typing import List, Union

from ansys.granta.bomanalytics import models


class IndicatorDefinition(ABC):
    def __init__(self, name, legislation_names, default_threshold_percentage):
        self.name = name
        self.legislation_names = legislation_names
        self.default_threshold_percentage = default_threshold_percentage
        self._indicator_type = None

    @property
    def definition(self):
        return models.GrantaBomAnalyticsServicesInterfaceCommonIndicatorDefinition(
            name=self.name,
            legislation_names=self.legislation_names,
            default_threshold_percentage=self.default_threshold_percentage,
            type=self._indicator_type,
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
