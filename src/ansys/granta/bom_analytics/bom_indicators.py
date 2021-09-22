from enum import Enum, auto
from abc import ABC
from typing import List, Union, Dict

from ansys.granta.bomanalytics import models

Indicator_Definitions = Dict[str, Union["WatchListIndicator", "RoHSIndicator"]]


class Flag(Enum):
    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return TypeError(f"Cannot compare {type(self)} with {type(other)}")


class RoHSFlag(Flag):
    RohsNotImpacted = auto()
    RohsBelowThreshold = auto()
    RohsCompliant = auto()
    RohsCompliantWithExemptions = auto()
    RohsAboveThreshold = auto()
    RohsNonCompliant = auto()
    RohsUnknown = auto()


class WatchListFlag(Flag):
    WatchListNotImpacted = auto()
    WatchListCompliant = auto()
    WatchListBelowThreshold = auto()
    WatchListAllSubstancesBelowThreshold = auto()
    WatchListAboveThreshold = auto()
    WatchListHasSubstanceAboveThreshold = auto()
    WatchListUnknown = auto()


class Indicator(ABC):
    available_flags = None

    def __init__(
        self,
        name: str,
        legislation_names: List[str],
        default_threshold_percentage: Union[float, None] = None,
    ):
        self.name: str = name
        self.legislation_names: List[str] = legislation_names
        self.default_threshold_percentage: float = default_threshold_percentage
        self._indicator_type: Union[str, None] = None
        self._flag: Union[Flag, None] = None

    @property
    def definition(self):
        return models.GrantaBomAnalyticsServicesInterfaceCommonIndicatorDefinition(
            name=self.name,
            legislation_names=self.legislation_names,
            default_threshold_percentage=self.default_threshold_percentage,
            type=self._indicator_type,
        )

    @property
    def flag(self) -> Flag:
        return self._flag

    @flag.setter
    def flag(self, flag: str):
        try:
            self._flag: Flag = self.__class__.available_flags[flag]
        except KeyError as e:
            raise Exception(
                f'Unknown flag {flag} for indicator {self.name}, type "{self._indicator_type}"'
            ).with_traceback(e.__traceback__)


class RoHSIndicator(Indicator):
    available_flags = RoHSFlag

    def __init__(
        self,
        name: str,
        legislation_names: List[str],
        default_threshold_percentage: Union[float, None] = None,
    ):
        super().__init__(name, legislation_names, default_threshold_percentage)
        self._indicator_type: str = "Rohs"


class WatchListIndicator(Indicator):
    available_flags = WatchListFlag

    def __init__(
        self,
        name: str,
        legislation_names: List[str],
        default_threshold_percentage: Union[float, None] = None,
    ):
        super().__init__(name, legislation_names, default_threshold_percentage)
        self._indicator_type: str = "WatchList"
