.. _ref_bom_analytics_api_compliance_substances:

Substance Compliance
====================

Query definition
~~~~~~~~~~~~~~~~

.. py:currentmodule::ansys.granta.bom_analytics.queries
.. autoclass:: ansys.granta.bom_analytics.queries.SubstanceComplianceQuery
   :members:

   .. automethod:: with_record_guids
   .. automethod:: with_record_history_guids
   .. automethod:: with_record_history_ids
   .. automethod:: with_stk_records
   .. automethod:: with_cas_numbers
   .. automethod:: with_ec_numbers
   .. automethod:: with_chemical_names
   .. automethod:: with_record_guids_and_amounts
   .. automethod:: with_record_history_guids_and_amounts
   .. automethod:: with_record_history_ids_and_amounts
   .. automethod:: with_cas_numbers_and_amounts
   .. automethod:: with_ec_numbers_and_amounts
   .. automethod:: with_chemical_names_and_amounts
   .. automethod:: with_batch_size
   .. automethod:: with_indicators

Query result
~~~~~~~~~~~~

.. py:currentmodule::ansys.granta.bom_analytics._query_results
.. autoclass:: ansys.granta.bom_analytics._query_results.SubstanceComplianceQueryResult
   :members:

   .. autoproperty:: compliance_by_indicator

Substance result
~~~~~~~~~~~~~~~~

.. py:currentmodule::ansys.granta.bom_analytics._item_results
.. autoclass:: ansys.granta.bom_analytics._item_results.SubstanceWithComplianceResult
   :members:

   .. autoattribute:: cas_number
   .. autoattribute:: ec_number
   .. autoattribute:: chemical_name
   .. autoattribute:: record_guid
   .. autoattribute:: record_history_guid
   .. autoattribute:: record_history_identity
   .. autoattribute:: indicators
