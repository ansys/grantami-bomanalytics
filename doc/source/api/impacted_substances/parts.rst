.. _ref_bom_analytics_api_impactedsubstances_parts:

Part Impacted Substances
========================

Query definition
~~~~~~~~~~~~~~~~

.. autoclass:: ansys.granta.bom_analytics.queries.PartImpactedSubstancesQuery
   :members:

   .. automethod:: with_record_guids
   .. automethod:: with_record_history_guids
   .. automethod:: with_record_history_ids
   .. automethod:: with_part_numbers
   .. automethod:: with_batch_size
   .. automethod:: with_legislations

Query result
~~~~~~~~~~~~

.. autoclass:: ansys.granta.bom_analytics._query_results.PartImpactedSubstancesQueryResult
   :members:

   .. autoproperty:: impacted_substances_by_legislation
   .. autoproperty:: impacted_substances

Part result
~~~~~~~~~~~

.. autoclass:: ansys.granta.bom_analytics._item_results.PartWithImpactedSubstancesResult
   :members:

   .. autoattribute:: part_number
   .. autoattribute:: record_guid
   .. autoattribute:: record_history_guid
   .. autoattribute:: record_history_identity
   .. autoattribute:: legislations