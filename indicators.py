from abc import ABC

from ansys.granta import bomanalytics


class Indicator(ABC):
    def __init__(self, name, legislation_names, default_threshold_percentage):
        self._name = name
        self._legislation_names = legislation_names
        self._default_threshold_percentage = default_threshold_percentage
        self._indicator_type = None

    @property
    def definition(self):
        return bomanalytics. \
            GrantaBomAnalyticsServicesInterfaceCommonIndicatorDefinition(name=self._name,
                                                                         legislation_names=self._legislation_names,
                                                                         default_threshold_percentage=self._default_threshold_percentage,
                                                                         type=self._indicator_type)


class RoHSIndicator(Indicator):
    def __init__(self, name, legislation_names, default_threshold_percentage):
        super().__init__(name, legislation_names, default_threshold_percentage)
        self._indicator_type = 'Rohs'


class WatchListIndicator(Indicator):
    def __init__(self, name, legislation_names, default_threshold_percentage):
        super().__init__(name, legislation_names, default_threshold_percentage)
        self._indicator_type = 'WatchList'
