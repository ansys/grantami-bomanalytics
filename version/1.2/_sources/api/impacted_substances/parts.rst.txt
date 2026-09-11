.. _ref_grantami_bomanalytics_api_impactedsubstances_parts:

Part impacted substances
========================

Query definition
~~~~~~~~~~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics.queries.PartImpactedSubstancesQuery
   :members:

   .. automethod:: with_legislations
   .. automethod:: with_part_numbers
   .. automethod:: with_record_guids
   .. automethod:: with_record_history_guids
   .. automethod:: with_record_history_ids
   .. automethod:: with_batch_size

Query result
~~~~~~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics._query_results.PartImpactedSubstancesQueryResult
   :members:
   :exclude-members: impacted_substances_by_part

   .. autoattribute:: impacted_substances_by_part
   .. autoattribute:: impacted_substances_by_legislation
   .. autoattribute:: impacted_substances
   .. autoattribute:: messages

Part result
~~~~~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics._item_results.PartWithImpactedSubstancesResult
