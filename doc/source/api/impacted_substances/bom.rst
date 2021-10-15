.. _ref_bom_analytics_api_impactedsubstances_bom:

BoM Impacted Substances
=======================

Query definition
~~~~~~~~~~~~~~~~

.. autoclass:: ansys.granta.bom_analytics.queries.BomImpactedSubstancesQuery
   :members:

   .. automethod:: with_bom
   .. automethod:: with_legislations

Query result
~~~~~~~~~~~~

.. autoclass:: ansys.granta.bom_analytics._query_results.BomImpactedSubstancesQueryResult
   :members:

   .. autoproperty:: impacted_substances_by_legislation
   .. autoproperty:: impacted_substances

Bom result
~~~~~~~~~~

.. autoclass:: ansys.granta.bom_analytics._item_results.BoM1711WithImpactedSubstancesResult
   :members:

   .. autoattribute:: legislations