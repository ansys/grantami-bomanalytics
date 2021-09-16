from .connection import Connection
from .query_managers import (
    MaterialImpactedSubstanceQuery,
    MaterialComplianceQuery,
    PartImpactedSubstanceQuery,
    PartComplianceQuery,
    SpecificationImpactedSubstanceQuery,
    SpecificationComplianceQuery,
    SubstanceComplianceQuery,
    BoMImpactedSubstancesQuery,
    BoMComplianceQuery,
)
from .indicators import (
    RoHSIndicatorDefinition as RoHSIndicator,
    WatchListIndicatorDefinition as WatchListIndicator,
)

# TODO Logging?!
# TODO use STK to extend bom services objects? e.g. adding all references to sparsely referenced object
