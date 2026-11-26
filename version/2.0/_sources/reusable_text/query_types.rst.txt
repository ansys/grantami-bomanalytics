.. _ref_query_types:

The queries supported by this package can be split into two broad groups: record-based queries and
BoM-based queries. Whereas BoM-based queries can only be constructed with a single BoM, record-based
queries can be constructed with any number of records. For example, a
:class:`~ansys.grantami.bomanalytics.queries.SpecificationImpactedSubstancesQuery` could include
any number of specification references.
