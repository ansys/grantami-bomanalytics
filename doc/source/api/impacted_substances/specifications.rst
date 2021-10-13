.. _ref_bom_analytics_api_impactedsubstances_specifications:

Specification Impacted Substances
=================================

Query definition
~~~~~~~~~~~~~~~~

.. autoclass:: ansys.granta.bom_analytics.queries.SpecificationImpactedSubstancesQuery
   :members:

   .. automethod:: with_record_guids
   .. automethod:: with_record_history_guids
   .. automethod:: with_record_history_ids
   .. automethod:: with_specification_ids
   .. automethod:: with_batch_size
   .. automethod:: with_legislations

Query result
~~~~~~~~~~~~

.. autoclass:: ansys.granta.bom_analytics._query_results.SpecificationImpactedSubstancesQueryResult
   :members:

   .. autoproperty:: impacted_substances_by_legislation
   .. autoproperty:: impacted_substances


Specification result
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: ansys.granta.bom_analytics._item_results.SpecificationWithImpactedSubstancesResult
   :members:

   .. autoattribute:: legislations
