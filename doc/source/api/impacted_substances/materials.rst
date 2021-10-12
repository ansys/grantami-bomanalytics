.. _ref_bom_analytics_api_impactedsubstances_materials:

Material Impacted Substances
============================

Query definition
~~~~~~~~~~~~~~~~

.. py:currentmodule::ansys.granta.bom_analytics.queries
.. autoclass:: ansys.granta.bom_analytics.queries.MaterialImpactedSubstances
   :members:

   .. automethod:: with_record_guids
   .. automethod:: with_record_history_guids
   .. automethod:: with_record_history_ids
   .. automethod:: with_material_ids
   .. automethod:: with_batch_size
   .. automethod:: with_legislations

Query result
~~~~~~~~~~~~

.. py:currentmodule::ansys.granta.bom_analytics._query_results
.. autoclass:: ansys.granta.bom_analytics._query_results.MaterialImpactedSubstancesResult
   :members:

   .. autoproperty:: impacted_substances_by_legislation
   .. autoproperty:: impacted_substances

Material result
~~~~~~~~~~~~~~~

.. py:currentmodule::ansys.granta.bom_analytics._item_results
.. autoclass:: ansys.granta.bom_analytics._item_results.MaterialWithImpactedSubstancesResult
   :members:

   .. autoattribute:: legislations
