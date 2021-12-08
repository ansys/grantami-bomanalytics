.. _ref_bom_analytics_api_compliance_materials:

Material Compliance
===================

Query definition
~~~~~~~~~~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics.queries.MaterialComplianceQuery
   :members:

   .. automethod:: with_indicators
   .. automethod:: with_material_ids
   .. automethod:: with_record_guids
   .. automethod:: with_record_history_guids
   .. automethod:: with_record_history_ids
   .. automethod:: with_stk_records
   .. automethod:: with_batch_size

Query result
~~~~~~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics._query_results.MaterialComplianceQueryResult
   :members:
   :exclude-members: compliance_by_material_and_indicator

   .. autoattribute:: compliance_by_indicator
   .. autoattribute:: compliance_by_material_and_indicator

Material result
~~~~~~~~~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics._item_results.MaterialWithComplianceResult
