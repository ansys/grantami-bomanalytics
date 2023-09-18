.. _ref_grantami_bomanalytics_api_impactedsubstances_bom:

BoM impacted substances
=======================

.. _ref_grantami_bomanalytics_api_impactedsubstances_bom_query:

Query definition
~~~~~~~~~~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics.queries.BomImpactedSubstancesQuery
   :members:

   .. automethod:: with_legislations
   .. automethod:: with_bom

.. _ref_grantami_bomanalytics_api_impactedsubstances_bom_queryresult:

Query result
~~~~~~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics._query_results.BomImpactedSubstancesQueryResult
   :members:

   .. autoattribute:: impacted_substances_by_legislation
   .. autoattribute:: impacted_substances
   .. autoattribute:: messages
