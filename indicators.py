from abc import ABC
from ansys.granta import bomanalytics


class Indicator(ABC):
    def __init__(self, name, legislation_names, default_threshold_percentage):
        self.name = name
        self.legislation_names = legislation_names
        self.default_threshold_percentage = default_threshold_percentage
        self._indicator_type = None

    @property
    def definition(self):
        return bomanalytics. \
            GrantaBomAnalyticsServicesInterfaceCommonIndicatorDefinition(name=self.name,
                                                                         legislation_names=self.legislation_names,
                                                                         default_threshold_percentage=self.default_threshold_percentage,
                                                                         type=self._indicator_type)


class RoHSIndicator(Indicator):
    def __init__(self, name, legislation_names, default_threshold_percentage):
        super().__init__(name, legislation_names, default_threshold_percentage)
        self._indicator_type = 'Rohs'


class WatchlistIndicator(Indicator):
    def __init__(self, name, legislation_names, default_threshold_percentage):
        super().__init__(name, legislation_names, default_threshold_percentage)
        self._indicator_type = 'WatchList'


class IndicatorResult:
    def __init__(self, name, result):
        self.name = name
        self.result = result
