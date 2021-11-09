.. _ref_bom_analytics_api_compliance_specifications:

Specification Compliance
========================

Query definition
~~~~~~~~~~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics.queries.SpecificationComplianceQuery
   :members:

   .. automethod:: with_record_guids
   .. automethod:: with_record_history_guids
   .. automethod:: with_record_history_ids
   .. automethod:: with_stk_records
   .. automethod:: with_specification_ids
   .. automethod:: with_batch_size
   .. automethod:: with_indicators


Query result
~~~~~~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics._query_results.SpecificationComplianceQueryResult
   :members:

   .. autoproperty:: compliance_by_indicator


Specification result
~~~~~~~~~~~~~~~~~~~~

.. py:currentmodule::ansys.grantami.bomanalytics._item_results
.. autoclass:: ansys.grantami.bomanalytics._item_results.SpecificationWithComplianceResult
   :members:

   .. autoattribute:: specification_id
   .. autoattribute:: record_guid
   .. autoattribute:: record_history_guid
   .. autoattribute:: record_history_identity
   .. autoattribute:: indicators
   .. autoattribute:: specifications
   .. autoattribute:: materials
   .. autoattribute:: coatings
   .. autoattribute:: substances

Coating result
~~~~~~~~~~~~~~

.. py:currentmodule::ansys.grantami.bomanalytics._item_results
.. autoclass:: ansys.grantami.bomanalytics._item_results.CoatingWithComplianceResult
   :members:

   .. autoattribute:: record_guid
   .. autoattribute:: record_history_guid
   .. autoattribute:: record_history_identity
   .. autoattribute:: indicators
   .. autoattribute:: substances
