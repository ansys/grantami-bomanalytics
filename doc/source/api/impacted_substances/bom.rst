.. _ref_grantami_bomanalytics_api_impactedsubstances_bom:

BoM Impacted Substances Query
=============================

Query Definition
~~~~~~~~~~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics.queries.BomImpactedSubstancesQuery
   :members:

   .. automethod:: with_legislations
   .. automethod:: with_bom

Query Result
~~~~~~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics._query_results.BomImpactedSubstancesQueryResult
   :members:

   .. autoattribute:: impacted_substances_by_legislation
   .. autoattribute:: impacted_substances
   .. autoattribute:: messages
