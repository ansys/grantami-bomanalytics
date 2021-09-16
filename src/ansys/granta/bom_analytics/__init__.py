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
from .item_definitions import RoHSIndicator, WatchlistIndicator

# TODO Logging?!
# TODO use STK to extend bom services objects? e.g. adding all references to sparsely referenced object
