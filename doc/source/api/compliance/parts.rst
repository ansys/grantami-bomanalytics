.. _ref_bom_analytics_api_compliance_parts:

Part Compliance Query
=====================

Query definition
~~~~~~~~~~~~~~~~

.. autoclass:: ansys.granta.bom_analytics.queries.PartComplianceQuery
   :members:

   .. automethod:: with_record_guids
   .. automethod:: with_record_history_guids
   .. automethod:: with_record_history_ids
   .. automethod:: with_stk_records
   .. automethod:: with_part_numbers
   .. automethod:: with_batch_size
   .. automethod:: with_indicators


Query result
~~~~~~~~~~~~

.. autoclass:: ansys.granta.bom_analytics._query_results.PartComplianceQueryResult
   :members:

   .. autoproperty:: compliance_by_indicator


Part result
~~~~~~~~~~~

.. py:currentmodule::ansys.granta.bom_analytics._item_results
.. autoclass:: ansys.granta.bom_analytics._item_results.PartWithComplianceResult
   :members:

   .. autoattribute:: indicators
   .. autoattribute:: parts
   .. autoattribute:: materials
   .. autoattribute:: specifications
   .. autoattribute:: substances
