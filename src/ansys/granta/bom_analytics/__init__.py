from .connection import Connection
from .query_builders import (
    MaterialImpactedSubstanceQueryBuilder as MaterialImpactedSubstanceQuery,
    MaterialComplianceQueryBuilder as MaterialComplianceQuery,
    PartImpactedSubstanceQueryBuilder as PartImpactedSubstanceQuery,
    PartComplianceQueryBuilder as PartComplianceQuery,
    SpecificationImpactedSubstanceQueryBuilder as SpecificationImpactedSubstanceQuery,
    SpecificationComplianceQueryBuilder as SpecificationComplianceQuery,
    SubstanceComplianceQueryBuilder as SubstanceComplianceQuery,
    Bom1711ImpactedSubstancesQueryBuilder as BomImpactedSubstancesQuery,
    Bom1711ComplianceQueryBuilder as BomComplianceQuery,
)
from .bom_indicators import (
    RoHSIndicatorDefinition as RoHSIndicator,
    WatchListIndicatorDefinition as WatchListIndicator,
)

# TODO Logging?!
# TODO use STK to extend bom services objects? e.g. adding all references to sparsely referenced object
