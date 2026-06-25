.. _ref_grantami_bomanalytics_api_compliance_bom:

BoM compliance
==============

Query definition
~~~~~~~~~~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics.queries.BomComplianceQuery
   :members:

   .. automethod:: with_indicators
   .. automethod:: with_bom

Query result
~~~~~~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics._query_results.BomComplianceQueryResult
   :members:
   :exclude-members: compliance_by_part_and_indicator

   .. autoattribute:: compliance_by_indicator
   .. autoattribute:: compliance_by_part_and_indicator
   .. autoattribute:: messages
