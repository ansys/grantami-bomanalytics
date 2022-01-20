.. include:: ../../_replacements.rst
.. _ref_grantami_bomanalytics_api_compliance_substances:

Substance Compliance
====================

Query Definition
~~~~~~~~~~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics.queries.SubstanceComplianceQuery
   :members:

   .. automethod:: with_indicators
   .. automethod:: with_cas_numbers_and_amounts
   .. automethod:: with_ec_numbers_and_amounts
   .. automethod:: with_chemical_names_and_amounts
   .. automethod:: with_cas_numbers
   .. automethod:: with_ec_numbers
   .. automethod:: with_chemical_names
   .. automethod:: with_record_guids_and_amounts
   .. automethod:: with_record_history_guids_and_amounts
   .. automethod:: with_record_history_ids_and_amounts
   .. automethod:: with_record_guids
   .. automethod:: with_record_history_guids
   .. automethod:: with_record_history_ids
   .. automethod:: with_stk_records
   .. automethod:: with_batch_size

Query Result
~~~~~~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics._query_results.SubstanceComplianceQueryResult
   :members:
   :exclude-members: compliance_by_substance_and_indicator

   .. autoattribute:: compliance_by_indicator
   .. autoattribute:: compliance_by_substance_and_indicator
   .. autoattribute:: messages

Substance Result
~~~~~~~~~~~~~~~~

.. autoclass:: ansys.grantami.bomanalytics._item_results.SubstanceWithComplianceResult
