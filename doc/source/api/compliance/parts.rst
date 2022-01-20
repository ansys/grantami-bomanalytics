.. include:: ../../_replacements.rst
.. _ref_grantami_bomanalytics_api_compliance_parts:

Part Compliance
===============

Query Definition
~~~~~~~~~~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics.queries.PartComplianceQuery
   :members:

   .. automethod:: with_indicators
   .. automethod:: with_part_numbers
   .. automethod:: with_record_guids
   .. automethod:: with_record_history_guids
   .. automethod:: with_record_history_ids
   .. automethod:: with_stk_records
   .. automethod:: with_batch_size


Query Result
~~~~~~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics._query_results.PartComplianceQueryResult
   :members:
   :exclude-members: compliance_by_part_and_indicator

   .. autoattribute:: compliance_by_indicator
   .. autoattribute:: compliance_by_part_and_indicator
   .. autoattribute:: messages


Part Result
~~~~~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics._item_results.PartWithComplianceResult
