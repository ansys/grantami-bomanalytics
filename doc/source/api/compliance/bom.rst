.. _ref_bom_analytics_api_compliance_bom:

BoM Compliance
==============

Query definition
~~~~~~~~~~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics.queries.BomComplianceQuery
   :members:

   .. automethod:: with_bom
   .. automethod:: with_indicators

Query result
~~~~~~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics._query_results.BomComplianceQueryResult
   :members:

   .. autoproperty:: compliance_by_indicator

