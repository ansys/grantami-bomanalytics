.. include:: ../../_replacements.rst
.. _ref_grantami_bomanalytics_api_compliance_specifications:

Specification Compliance
========================

Query Definition
~~~~~~~~~~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics.queries.SpecificationComplianceQuery
   :members:

   .. automethod:: with_indicators
   .. automethod:: with_specification_ids
   .. automethod:: with_record_guids
   .. automethod:: with_record_history_guids
   .. automethod:: with_record_history_ids
   .. automethod:: with_stk_records
   .. automethod:: with_batch_size


Query Result
~~~~~~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics._query_results.SpecificationComplianceQueryResult
   :members:
   :exclude-members: compliance_by_specification_and_indicator

   .. autoattribute:: compliance_by_indicator
   .. autoattribute:: compliance_by_specification_and_indicator
   .. autoattribute:: messages


Specification Result
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics._item_results.SpecificationWithComplianceResult


Coating Result
~~~~~~~~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics._item_results.CoatingWithComplianceResult
