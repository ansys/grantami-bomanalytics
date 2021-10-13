.. _ref_bom_analytics_api_compliance_materials:


Material Compliance Query
=========================

Query definition
~~~~~~~~~~~~~~~~

.. autoclass:: ansys.granta.bom_analytics.queries.MaterialComplianceQuery
   :members:

   .. automethod:: with_record_guids
   .. automethod:: with_record_history_guids
   .. automethod:: with_record_history_ids
   .. automethod:: with_stk_records
   .. automethod:: with_material_ids
   .. automethod:: with_batch_size
   .. automethod:: with_indicators

Query result
~~~~~~~~~~~~

.. autoclass:: ansys.granta.bom_analytics._query_results.MaterialComplianceQueryResult
   :members:

   .. autoproperty:: compliance_by_indicator

Material result
~~~~~~~~~~~~~~~

.. py:currentmodule::ansys.granta.bom_analytics._item_results
.. autoclass:: ansys.granta.bom_analytics._item_results.MaterialWithComplianceResult
   :members:

   .. autoattribute:: indicators
   .. autoattribute:: substances
