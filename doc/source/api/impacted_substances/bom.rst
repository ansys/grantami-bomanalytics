.. _ref_bom_analytics_api_impactedsubstances_bom:

BoM Impacted Substances
=======================

Query definition
~~~~~~~~~~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics.queries.BomImpactedSubstancesQuery
   :members:

   .. automethod:: with_bom
   .. automethod:: with_legislations

Query result
~~~~~~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics._query_results.BomImpactedSubstancesQueryResult
   :members:

   .. autoproperty:: impacted_substances_by_legislation
   .. autoproperty:: impacted_substances

Bom result
~~~~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics._item_results.BoM1711WithImpactedSubstancesResult
   :members:

   .. autoattribute:: legislations