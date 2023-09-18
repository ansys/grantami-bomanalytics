.. _ref_grantami_bomanalytics_api_compliance_specifications:

Specification compliance
========================

Query definition
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


Query result
~~~~~~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics._query_results.SpecificationComplianceQueryResult
   :members:
   :exclude-members: compliance_by_specification_and_indicator

   .. autoattribute:: compliance_by_indicator
   .. autoattribute:: compliance_by_specification_and_indicator
   .. autoattribute:: messages


Specification result
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics._item_results.SpecificationWithComplianceResult
   :inherited-members:
   :member-order: by_mro_by_source

Coating result
~~~~~~~~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics._item_results.CoatingWithComplianceResult
   :inherited-members:
   :exclude-members: record_history_guid, record_guid
   :member-order: by_mro_by_source