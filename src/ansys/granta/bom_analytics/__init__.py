from .connection import Connection
from .query_builders import (
    MaterialImpactedSubstanceQuery,
    MaterialComplianceQuery,
    PartImpactedSubstanceQuery,
    PartComplianceQuery,
    SpecificationImpactedSubstanceQuery,
    SpecificationComplianceQuery,
    SubstanceComplianceQuery,
    BomImpactedSubstanceQuery,
    BomComplianceQuery,
)
from .bom_indicators import (
    RoHSIndicator,
    WatchListIndicator,
)

# TODO Logging?!
# TODO use STK to extend bom services objects? e.g. adding all references to sparsely referenced object
