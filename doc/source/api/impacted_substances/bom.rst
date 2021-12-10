.. _ref_grantami_bomanalytics_api_impactedsubstances_bom:

BoM Impacted Substances
=======================

Query definition
~~~~~~~~~~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics.queries.BomImpactedSubstancesQuery
   :members:

   .. automethod:: with_legislations
   .. automethod:: with_bom

Query result
~~~~~~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics._query_results.BomImpactedSubstancesQueryResult
   :members:

   .. autoattribute:: impacted_substances_by_legislation
   .. autoattribute:: impacted_substances
